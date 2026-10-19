# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2024 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""Wrapper around the Belga AI translate endpoint."""

import flask
import requests
import superdesk

TRANSLATE_PATH = "toolkit/translate"
DEFAULT_TARGET_LANGUAGE = "en"
DEFAULT_TIMEOUT = (5, 30)


def _get_user_header():
    if not flask.has_request_context():
        return ""
    user = flask.g.get("user") or {}
    return user.get("username") or user.get("email") or ""


def translate_text(text, target_language=DEFAULT_TARGET_LANGUAGE):
    """Translate ``text`` into ``target_language`` using the Belga AI endpoint."""
    if not text:
        return text

    base_url = superdesk.app.config.get("BELGA_AI_URL")
    if not base_url:
        raise RuntimeError("BELGA_AI_URL is not configured")

    response = requests.post(
        base_url.rstrip("/") + "/" + TRANSLATE_PATH,
        json={"language": target_language, "text": text},
        headers={"User": _get_user_header()},
        timeout=superdesk.app.config.get("HTTP_PROXY_TIMEOUT", DEFAULT_TIMEOUT),
    )
    response.raise_for_status()

    translated = response.json().get("response")
    if isinstance(translated, list):
        return translated[0] if translated else ""
    return translated or ""
