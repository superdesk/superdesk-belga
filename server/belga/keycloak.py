import aiohttp

from datetime import datetime, timedelta


class AsyncKeycloakAuth:
    """Handles asynchronous Keycloak authentication and token management."""

    def __init__(self, endpoint: str, client_id: str, client_secret: str):
        self.endpoint = endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: str | None = None
        self._token_expiry: datetime | None = None

    async def get_token(self, http_client: aiohttp.ClientSession) -> str:
        """Get a valid access token."""
        if (
            not self._token
            or not self._token_expiry
            or datetime.now() >= self._token_expiry
        ):
            await self._fetch_new_token(http_client)

        assert self._token is not None, "Access token was not fetched"
        return self._token

    async def _fetch_new_token(self, http_client: aiohttp.ClientSession) -> None:
        """Fetch a new token from Keycloak."""
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        async with http_client.post(self.endpoint, data=data) as response:
            response.raise_for_status()
            token_data = await response.json()

        self._token = token_data["access_token"]
        self._token_expiry = datetime.now() + timedelta(
            seconds=max(token_data["expires_in"] - 300, 0)
        )
