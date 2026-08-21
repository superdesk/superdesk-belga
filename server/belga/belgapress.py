import logging
import requests
import superdesk

from typing import Optional
from urllib.parse import urljoin
from flask import current_app as app

from .keycloak import KeycloakAuth

logger = logging.getLogger(__name__)

SHARE_ENDPOINT = "/belgapress/api/internal/newsobjects/share"
TIMEOUT = 10

BELGABOX_URL = (
    "https://www.belgabox.be/belgabox/fo/detail"
    "?contentType=news&targetSide=Right&id={id}&parentId={id}&isArchive=true"
)

_auth: Optional[KeycloakAuth] = None
_session: Optional[requests.Session] = None


def _get_archive_id(guid: str) -> str:
    return str(guid).split(":")[-1]


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


def _get_auth() -> KeycloakAuth:
    global _auth
    if _auth is None:
        _auth = KeycloakAuth(
            endpoint=app.config["BELGA_KEYCLOAK_ENDPOINT"],
            client_id=app.config["BELGA_KEYCLOAK_CLIENT_ID"],
            client_secret=app.config["BELGA_KEYCLOAK_CLIENT_SECRET"],
        )
    return _auth


def get_share_url(guid: str) -> str:
    """Get share url for given item guid, fallback to belgabox url."""
    archive_id = _get_archive_id(guid)
    url = app.config.get("BELGA_PRESS_URL")
    if not url:
        return BELGABOX_URL.format(id=archive_id)

    try:
        res = _get_session().get(
            urljoin(url, SHARE_ENDPOINT),
            params={"archiveId": archive_id},
            headers={"Authorization": f"Bearer {_get_auth().get_token()}"},
            timeout=TIMEOUT,
        )
        res.raise_for_status()
        return res.json()
    except (requests.RequestException, ValueError, KeyError) as err:
        logger.exception("Could not fetch share url for %s: %s", guid, err)
        return BELGABOX_URL.format(id=archive_id)


def init_app(_app):
    superdesk.register_jinja_filter("belgapress_share_url", get_share_url)
