import requests

AUTH_API_URL = "https://oauth.zettle.com/token"


class Authenticate:

    def __init__(self, client_id: str, api_key: str):
        self.client_id = client_id
        self.api_key = api_key
        self.auth_api_url = AUTH_API_URL

        self.full_token = self._get_token()
        self.access_token = self.full_token['access_token']
        self.token_expires_in = self.full_token['expires_in']

    def _get_token(self):
        # Create the payload for the POST request
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "client_id": self.client_id,
            "assertion": self.api_key
        }

        # Set the headers
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            # Send the POST request to retrieve the access token
            response = requests.post(self.auth_api_url, data=payload, headers=headers)

            # Check the response status and parse the token
            if response.status_code == 200:
                return response.json()
            else:
                raise ValueError(f"Did not get a 200 response from API. Instead got {response.status_code}")

        except requests.exceptions.RequestException as e:
            raise SystemExit(f"Request failed: {e}")
