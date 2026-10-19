import asyncio
import aiohttp

from unittest.mock import AsyncMock, MagicMock, patch
from superdesk.flask import render_template
from superdesk.tests import TestCase

from belga import belgapress


GUID = "urn:belga.be:360archive:167010875"
SHARE_URL = "https://belgapress/share/abc123"


def get_response(json_data):
    response = MagicMock()
    response.json = AsyncMock(return_value=json_data)
    return response


class BelgaPressShareUrlTestCase(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        belgapress._auth = None
        self.app.config["BELGA_PRESS_URL"] = "https://belgapress"
        self.app.config["BELGAPRESS_KEYCLOAK_ENDPOINT"] = "https://keycloak/token"
        self.app.config["BELGAPRESS_KEYCLOAK_CLIENT_ID"] = "client"
        self.app.config["BELGAPRESS_KEYCLOAK_CLIENT_SECRET"] = "secret"

    def test_auth_uses_belgapress_credentials(self):
        auth = belgapress._get_auth()

        self.assertEqual("https://keycloak/token", auth.endpoint)
        self.assertEqual("client", auth.client_id)
        self.assertEqual("secret", auth.client_secret)

    def test_filter_is_registered(self):
        self.assertEqual(
            belgapress.get_share_url,
            self.app.jinja_env.filters["belgapress_share_url"],
        )

    async def test_fallback_when_not_configured(self):
        self.app.config["BELGA_PRESS_URL"] = None
        url = await belgapress.get_share_url(GUID)
        self.assertIn("belgabox.be", url)
        self.assertIn("id=167010875", url)
        self.assertIn("parentId=167010875", url)

    @patch.object(belgapress, "_get_auth")
    @patch("belga.belgapress.aiohttp.ClientSession")
    async def test_get_share_url(self, client_session, _get_auth):
        _get_auth.return_value.get_token = AsyncMock(return_value="token")
        session = MagicMock()
        client_session.return_value.__aenter__.return_value = session
        session.get.return_value.__aenter__.return_value = get_response(SHARE_URL)

        self.assertEqual(SHARE_URL, await belgapress.get_share_url(GUID))
        self.assertEqual(SHARE_URL, await belgapress.get_share_url(GUID))
        _get_auth.return_value.get_token.assert_awaited_once_with(session)

        session.get.assert_called_once_with(
            "https://belgapress/belgapress/api/internal/newsobjects/share",
            params={"archiveId": "167010875"},
            headers={"Authorization": "Bearer token"},
        )
        client_session.assert_called_once_with(
            timeout=aiohttp.ClientTimeout(total=belgapress.TIMEOUT)
        )

    @patch.object(belgapress, "_get_auth")
    @patch("belga.belgapress.aiohttp.ClientSession")
    async def test_fallback_on_error(self, client_session, _get_auth):
        _get_auth.return_value.get_token = AsyncMock(return_value="token")
        session = MagicMock()
        client_session.return_value.__aenter__.return_value = session
        session.get.side_effect = aiohttp.ClientConnectionError()

        url = await belgapress.get_share_url(GUID)
        self.assertIn("belgabox.be", url)
        self.assertIn("id=167010875", url)
        self.assertEqual(url, await belgapress.get_share_url(GUID))
        session.get.assert_called_once()

    @patch.object(belgapress, "_get_auth")
    @patch("belga.belgapress.aiohttp.ClientSession")
    async def test_email_formats_reuse_share_urls(self, client_session, _get_auth):
        _get_auth.return_value.get_token = AsyncMock(return_value="token")
        session = MagicMock()
        client_session.return_value.__aenter__.return_value = session
        session.get.return_value.__aenter__.return_value = get_response(SHARE_URL)
        data = {
            "event": {"related_items": [{"guid": GUID}, {"guid": GUID}]},
            "assignment": {},
        }

        for suffix in ("html", "txt"):
            rendered = await render_template(
                f"assignment_details_email.{suffix}", **data
            )
            self.assertEqual(2, rendered.count(SHARE_URL))

        session.get.assert_called_once()

    @patch.object(belgapress, "_get_auth")
    @patch("belga.belgapress.aiohttp.ClientSession")
    async def test_resolution_yields_during_auth_and_share_request(
        self, client_session, _get_auth
    ):
        auth_started = asyncio.Event()
        auth_release = asyncio.Event()
        share_started = asyncio.Event()
        share_release = asyncio.Event()

        async def get_token(session):
            auth_started.set()
            await auth_release.wait()
            return "token"

        async def get_json():
            share_started.set()
            await share_release.wait()
            return SHARE_URL

        _get_auth.return_value.get_token = AsyncMock(side_effect=get_token)
        session = MagicMock()
        client_session.return_value.__aenter__.return_value = session
        response = get_response(SHARE_URL)
        response.json.side_effect = get_json
        session.get.return_value.__aenter__.return_value = response

        task = asyncio.create_task(belgapress.get_share_url(GUID))
        try:
            await asyncio.wait_for(auth_started.wait(), timeout=1)
            self.assertFalse(task.done())
            auth_release.set()
            await asyncio.wait_for(share_started.wait(), timeout=1)
            self.assertFalse(task.done())
            share_release.set()
            self.assertEqual(SHARE_URL, await asyncio.wait_for(task, timeout=1))
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    @patch("belga.belgapress.aiohttp.ClientSession")
    async def test_async_token_request(self, client_session):
        session = MagicMock()
        client_session.return_value.__aenter__.return_value = session
        token_response = get_response({"access_token": "token", "expires_in": 3600})
        session.post.return_value.__aenter__.return_value = token_response
        session.get.return_value.__aenter__.return_value = get_response(SHARE_URL)

        self.assertEqual(SHARE_URL, await belgapress.get_share_url(GUID))

        session.post.assert_called_once_with(
            "https://keycloak/token",
            data={
                "grant_type": "client_credentials",
                "client_id": "client",
                "client_secret": "secret",
            },
        )
        token_response.json.assert_awaited_once()

    @patch.object(belgapress, "_get_auth")
    @patch("belga.belgapress.aiohttp.ClientSession")
    async def test_fallback_on_auth_errors(self, client_session, _get_auth):
        for error in (
            aiohttp.ClientConnectionError(),
            asyncio.TimeoutError(),
            ValueError("Invalid JSON"),
            KeyError("access_token"),
        ):
            with self.subTest(error=error):
                async with self.app.app_context():
                    _get_auth.return_value.get_token = AsyncMock(side_effect=error)
                    with self.assertLogs(belgapress.logger, level="ERROR"):
                        url = await belgapress.get_share_url(GUID)
                    self.assertEqual(
                        belgapress.BELGABOX_URL.format(id="167010875"), url
                    )

    @patch.object(belgapress, "_get_auth")
    @patch("belga.belgapress.aiohttp.ClientSession")
    async def test_cache_is_scoped_to_app_context(self, client_session, _get_auth):
        _get_auth.return_value.get_token = AsyncMock(return_value="token")
        session = MagicMock()
        client_session.return_value.__aenter__.return_value = session
        session.get.return_value.__aenter__.return_value = get_response(SHARE_URL)

        for _ in range(2):
            async with self.app.app_context():
                self.assertEqual(SHARE_URL, await belgapress.get_share_url(GUID))

        self.assertEqual(2, session.get.call_count)
