import requests

from datetime import datetime, timedelta


class KeycloakAuth:
    """Handles Keycloak authentication and token management."""

    def __init__(self, endpoint: str, client_id: str, client_secret: str):
        self.endpoint = endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None
        self._token_expiry = None

    def get_token(self) -> str:
        """Get a valid access token"""
        if (
            not self._token
            or not self._token_expiry
            or datetime.now() >= self._token_expiry
        ):
            self._fetch_new_token()

        assert self._token is not None, "Access token was not fetched"
        return self._token

    def _fetch_new_token(self):
        """Fetch new token from Keycloak."""
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(self.endpoint, data=data, verify=False)
        response.raise_for_status()

        token_data = response.json()
        self._token = token_data["access_token"]
        # Set expiry 5 minutes before actual expiry to be safe
        self._token_expiry = datetime.now() + timedelta(
            seconds=token_data["expires_in"] - 300
        )
