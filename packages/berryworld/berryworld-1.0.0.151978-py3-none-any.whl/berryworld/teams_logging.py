import pandas as pd
import requests as req
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def response_validation(response, key=None):
    response_df = pd.DataFrame()
    if str(response.status_code) == '201':
        if str(response.status_code) != '204':
            response_json = response.json()
            if key is None:
                response_df = pd.json_normalize(response_json)
            else:
                response_df = pd.json_normalize(response.json()[key])

    return response_df, str(response.status_code)


def read_webhook(webhook_json):
    incoming_id = webhook_json['id']
    message_id = webhook_json['conversation']['id'].split(';')[1].split('=')[1]
    if message_id == incoming_id:
        print('The message is a new conversation')
    else:
        print('The message is a reply to a conversation')


class TeamsLogging:
    """ Manage Error Logs in Microsoft Teams """

    def __init__(self, client_id, client_secret, org, scope, user=None, password=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.organisation = org
        self.scope = scope
        self.grant_type = 'client_credentials'
        self.user = user
        self.password = password
        self.auth_url = f"https://login.microsoftonline.com/{self.organisation}/oauth2/v2.0/token"
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = self.get_access_token()

    def get_access_token(self, grant_type=None, user=None, password=None):
        """ Initialise MS ClientApplication object with your client_id and authority URL and return the header
            to be attached to authenticate the requests
        """
        session = req.Session()
        retry = Retry(total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=30)
        retry.BACKOFF_MAX = 190

        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        if grant_type is None:
            grant_type = self.grant_type

        token_payload = f'grant_type={grant_type}&scope={self.scope}&client_id={self.client_id}' \
                        f'&client_secret={self.client_secret}'

        if grant_type == 'password':
            if user is None:
                user = self.user

            if password is None:
                password = self.password

            token_payload = token_payload + f'&username={user}&password={password}'

        token_headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        token_response = session.request("POST", self.auth_url, headers=token_headers, data=token_payload)

        # GET & ASSIGN Access_Token
        auth_access_token = json.loads(token_response.text)['access_token']
        headers = {"Authorization": f"Bearer {auth_access_token}", "Content-Type": "application/json"}

        return headers

    def next_link_pagination(self, messages_response, response_df):
        session = req.Session()
        retry = Retry(total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=30)
        retry.BACKOFF_MAX = 190

        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        while "@odata.nextLink" in messages_response:
            message_response_nextLink = messages_response['@odata.nextLink']
            nextLink_response = session.request("GET", message_response_nextLink, headers=self.headers)

            if str(nextLink_response.status_code).startswith('2'):
                nextLink_json = nextLink_response.json()
                nextLink_df = pd.json_normalize(nextLink_json['value'])

                if len(nextLink_df) > 0:
                    response_df = pd.concat([response_df, nextLink_df])
                else:
                    break

        return response_df

    def session_request(self, method, url, key='value', body=None, headers=None):
        """ GET Request """
        session = req.Session()
        retry = Retry(total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=30)
        retry.BACKOFF_MAX = 190

        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        if headers is None:
            headers = self.headers

        if method.upper() in ['POST', 'PATCH']:
            response = session.request(method, url, headers=headers, data=body)
            response_df, status_code = response_validation(response)

        else:
            response = session.request(method, url, headers=headers)
            response_df, status_code = response_validation(response, key=key)

            response_df = self.next_link_pagination(response.json(), response_df)

        return response_df, status_code

    def get_teams(self):
        """ Get the teams for the organisation """
        url = f"{self.base_url}/teams?$top=500"
        response_df, status_code = self.session_request("GET", url)

        return response_df, status_code

    def get_channels(self, team_id):
        """ Get the channel id for the team id passed in """
        url = f"{self.base_url}/teams/{team_id}/channels"
        response_df, status_code = self.session_request("GET", url)

        return response_df, status_code

    def get_channel_info(self, team_id, channel_name):
        """ Get the channel info for the channel name passed in """
        url = f"{self.base_url}/teams/{team_id}/channels"
        response_df, status_code = self.session_request("GET", url)
        if response_df.shape[0] > 0:
            for i, res in response_df.iterrows():
                if res['displayName'] == channel_name:
                    return pd.DataFrame(res).T, status_code
        else:
            return response_df, status_code

    def get_channel_messages(self, team_id, channel_id):
        """ Get the channel messages for the channel id passed in """
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages?$top=50"
        response_df, status_code = self.session_request("GET", url)

        return response_df, status_code

    def get_channel_delta_messages(self, team_id, channel_id, date_filter=None, expand=None):
        """ Get the channel messages for the channel id passed in """
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages"
        query_params = ''
        if date_filter is not None:
            query_params = query_params + f"$filter=createdDateTime ge {date_filter}"

        if expand is not None:
            if len(query_params) > 0:
                query_params = query_params + f"&$expand={expand}"
            else:
                query_params = query_params + f"$expand={expand}"

        if len(query_params) > 0:
            url = url + '?' + query_params

        response_df, status_code = self.session_request("GET", url)

        return response_df, status_code

    def get_message_replies(self, team_id, channel_id, message_id):
        """ Get the message replies for the message id passed in """
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies"
        response_df, status_code = self.session_request("GET", url)

        return response_df, status_code

    def post_message(self, team_id, channel_id, message, mentions=None):
        """ Post a message to the channel id passed in """
        mentions_payload = []
        mentions_body_content = ''
        if mentions is None:
            mentions = list()
        for mention in mentions:
            req_id = 0
            user_response_df, status_code = self.session_request(
                "GET", f"{self.base_url}/users?$filter=mail eq '{mention}'")
            user_id = user_response_df['id'][0]
            user_name = user_response_df['displayName'][0]

            mentions_payload.append(
                {
                    "id": req_id,
                    "mentionText": user_name,
                    "mentioned": {
                        "user": {
                            "id": user_id,
                            "displayName": user_name,
                            "userIdentityType": "aadUser"
                        }
                    }
                }
            )

            mentions_body_content = mentions_body_content + f"<at id=\"{req_id}\">{user_name}</at> "
            req_id += 1

        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages"
        payload = {
            "body": {
                "contentType": "html",
                "content": mentions_body_content + message
            },
            "mentions": mentions_payload
        }

        headers = self.get_access_token(grant_type='password', user=self.user, password=self.password)
        response, status_code = self.session_request("POST", url, body=json.dumps(payload), headers=headers)

        return response, status_code

    def update_message(self, team_id, channel_id, message_id, message=None, importance=None):
        """ Update a message to the message id passed in """
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}"
        payload = {}
        if importance is not None:
            payload.update({"importance": importance})

        if message is not None:
            payload.update({"body": {"contentType": "html", "content": message}})

        if len(payload) > 0:
            headers = self.get_access_token(grant_type='password', user=self.user, password=self.password)
            response, status_code = self.session_request("PATCH", url, body=json.dumps(payload), headers=headers)

            return response, status_code
        else:
            return None, None

    def post_message_reply(self, team_id, channel_id, message_id, message):
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies"
        payload = {
            "body": {
                "contentType": "html",
                "content": message
            }
        }

        headers = self.get_access_token(grant_type='password', user=self.user, password=self.password)
        response, status_code = self.session_request("POST", url, body=json.dumps(payload), headers=headers)

        return response, status_code

    def update_message_reply(self, team_id, channel_id, message_id, reply_id, message=None, importance=None):
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies/{reply_id}"
        payload = {}
        if importance is not None:
            payload.update({"importance": importance})

        if message is not None:
            payload.update({"body": {"contentType": "html", "content": message}})

        if len(payload) > 0:
            headers = self.get_access_token(grant_type='password', user=self.user, password=self.password)
            response, status_code = self.session_request("PATCH", url, body=json.dumps(payload), headers=headers)

            return response, status_code
        else:
            return None, None

    def delete_message(self, team_id, channel_id, message_id):
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/softDelete"
        headers = self.get_access_token(grant_type='password', user=self.user, password=self.password)
        response, status_code = self.session_request("POST", url, headers=headers)

        return response, status_code

    def delete_message_reply(self, team_id, channel_id, message_id, reply_id):
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies/{reply_id}" \
              f"/softDelete"
        headers = self.get_access_token(grant_type='password', user=self.user, password=self.password)
        response, status_code = self.session_request("POST", url, headers=headers)

        return response, status_code
