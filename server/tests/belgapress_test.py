import requests

from unittest.mock import MagicMock, patch
from superdesk.tests import TestCase

from belga import belgapress


GUID = "urn:belga.be:360archive:167010875"
SHARE_URL = "https://belgapress/share/abc123"


def get_response(json_data):
    response = MagicMock()
    response.json.return_value = json_data
    return response


class BelgaPressShareUrlTestCase(TestCase):
    def setUp(self):
        belgapress._auth = None
        belgapress._session = None
        self.app.config["BELGA_PRESS_URL"] = "https://belgapress"
        self.app.config["BELGA_KEYCLOAK_ENDPOINT"] = "https://keycloak/token"
        self.app.config["BELGA_KEYCLOAK_CLIENT_ID"] = "client"
        self.app.config["BELGA_KEYCLOAK_CLIENT_SECRET"] = "secret"

    def test_filter_is_registered(self):
        self.assertEqual(
            belgapress.get_share_url,
            self.app.jinja_env.filters["belgapress_share_url"],
        )

    def test_fallback_when_not_configured(self):
        self.app.config["BELGA_PRESS_URL"] = None
        url = belgapress.get_share_url(GUID)
        self.assertIn("belgabox.be", url)
        self.assertIn("id=167010875", url)
        self.assertIn("parentId=167010875", url)

    @patch.object(belgapress, "_get_auth")
    @patch.object(belgapress, "_get_session")
    def test_get_share_url(self, _get_session, _get_auth):
        _get_auth.return_value.get_token.return_value = "token"
        session = _get_session.return_value
        session.get.return_value = get_response(SHARE_URL)

        self.assertEqual(SHARE_URL, belgapress.get_share_url(GUID))

        session.get.assert_called_once_with(
            "https://belgapress/belgapress/api/internal/newsobjects/share",
            params={"archiveId": "167010875"},
            headers={"Authorization": "Bearer token"},
            timeout=belgapress.TIMEOUT,
        )

    @patch.object(belgapress, "_get_auth")
    @patch.object(belgapress, "_get_session")
    def test_fallback_on_error(self, _get_session, _get_auth):
        _get_auth.return_value.get_token.return_value = "token"
        _get_session.return_value.get.side_effect = requests.ConnectionError()

        url = belgapress.get_share_url(GUID)
        self.assertIn("belgabox.be", url)
        self.assertIn("id=167010875", url)
