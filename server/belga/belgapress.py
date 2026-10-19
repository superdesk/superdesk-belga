import asyncio
import logging
import aiohttp
import superdesk

from typing import Optional
from urllib.parse import urljoin
from flask import current_app as app
from superdesk.flask import g

from .keycloak import AsyncKeycloakAuth

logger = logging.getLogger(__name__)

SHARE_ENDPOINT = "/belgapress/api/internal/newsobjects/share"
TIMEOUT = 10

BELGABOX_URL = (
    "https://www.belgabox.be/belgabox/fo/detail"
    "?contentType=news&targetSide=Right&id={id}&parentId={id}&isArchive=true"
)

_auth: Optional[AsyncKeycloakAuth] = None


def _get_archive_id(guid: str) -> str:
    return str(guid).split(":")[-1]


def _get_auth() -> AsyncKeycloakAuth:
    global _auth
    if _auth is None:
        _auth = AsyncKeycloakAuth(
            endpoint=app.config["BELGAPRESS_KEYCLOAK_ENDPOINT"],
            client_id=app.config["BELGAPRESS_KEYCLOAK_CLIENT_ID"],
            client_secret=app.config["BELGAPRESS_KEYCLOAK_CLIENT_SECRET"],
        )
    return _auth


async def get_share_url(guid: str) -> str:
    """Resolve a share URL asynchronously, reusing results within the app context."""
    archive_id = _get_archive_id(guid)
    url = app.config.get("BELGA_PRESS_URL")
    if not url:
        return BELGABOX_URL.format(id=archive_id)

    share_urls: dict[str, str] = g.setdefault("belgapress_share_urls", {})
    if archive_id in share_urls:
        return share_urls[archive_id]

    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=TIMEOUT)
        ) as session:
            token = await _get_auth().get_token(session)
            async with session.get(
                urljoin(url, SHARE_ENDPOINT),
                params={"archiveId": archive_id},
                headers={"Authorization": f"Bearer {token}"},
            ) as res:
                res.raise_for_status()
                share_urls[archive_id] = await res.json()
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, KeyError) as err:
        logger.exception("Could not fetch share url for %s: %s", guid, err)
        share_urls[archive_id] = BELGABOX_URL.format(id=archive_id)

    return share_urls[archive_id]


def init_app(_app):
    superdesk.register_jinja_filter("belgapress_share_url", get_share_url)
