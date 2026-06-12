# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2024 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""Auto translate a French or Dutch item into English and remap its packages."""

import html
import logging

from superdesk.editor_utils import generate_fields
from superdesk.etree import parse_html, to_string
from superdesk.text_utils import get_text

from .common import get_cv_by_qcode
from .helpers.belga_ai_translate import translate_text

logger = logging.getLogger(__name__)

FIELDS = ("headline", "body_html")

HEADLINE_TAG = "h1"
HEADLINE_FIELD = "headline"

SERVICES_PRODUCTS = "services-products"
COUNTRY = "country"

TARGET_LANGUAGE = "en"

SPORTS_SERVICES = ("SPN", "SPF")
NEWS_SERVICES = ("BIN", "BTL", "INT", "EXT")
BELGIUM_SERVICES = ("BIN", "INT")

PRODUCT_MAPPING = {
    "ECO": "ECONOMY",
    "POL": "POLITICS",
    "GEN": "GENERAL",
    "ALG": "GENERAL",
}
FALLBACK_PRODUCT = "GENERAL"

SPORTS_PACKAGE = "NEWS/SPORTS"
FALLBACK_PACKAGE = "NEWS/GENERAL"

BELGIUM_QCODE = "country_bel"


def _map_package_qcode(source_qcode):
    """Map a Belga wire package qcode to its English ``(qcode, service)``."""
    service, _, product = (source_qcode or "").partition("/")

    if service in SPORTS_SERVICES:
        return SPORTS_PACKAGE, service
    if service in NEWS_SERVICES:
        return "NEWS/{}".format(PRODUCT_MAPPING.get(product, FALLBACK_PRODUCT)), service
    return FALLBACK_PACKAGE, service


def _set_belgium_country(item):
    belgium = get_cv_by_qcode(COUNTRY).get(BELGIUM_QCODE)
    if not belgium:
        logger.warning("country CV value '%s' not found", BELGIUM_QCODE)
        return

    item["subject"] = [s for s in item.get("subject", []) if s.get("scheme") != COUNTRY]
    item["subject"].append(belgium)


def map_packages(item):
    """Remap the services-products package and set countries keywords."""
    subject = item.setdefault("subject", [])
    services_products = [s for s in subject if s.get("scheme") == SERVICES_PRODUCTS]
    if not services_products:
        return

    source_qcode = services_products[0].get("qcode", "")
    mapped_qcode, service = _map_package_qcode(source_qcode)

    mapped_subject = get_cv_by_qcode(SERVICES_PRODUCTS).get(mapped_qcode)
    if not mapped_subject:
        logger.warning("services-products CV value '%s' not found", mapped_qcode)
        return

    item["subject"] = [s for s in subject if s.get("scheme") != SERVICES_PRODUCTS]
    item["subject"].append(mapped_subject)

    if service in BELGIUM_SERVICES:
        _set_belgium_country(item)


def _strip_markup(value):
    """Return the plain-text version of a (possibly) HTML string."""
    return get_text(value, content="html").strip()


def _split_headline_body(translated):
    """Split the translated headline and body, or ``(None, None)`` if no h1."""
    root = parse_html(translated, content="html")
    heading = root.find('.//{}[@data-field="{}"]'.format(HEADLINE_TAG, HEADLINE_FIELD))
    if heading is None:
        heading = root.find(".//{}".format(HEADLINE_TAG))
    if heading is None:
        return None, None

    headline = "".join(heading.itertext()).strip()
    parent = heading.getparent()
    if parent is not None:
        parent.remove(heading)
    return headline, to_string(root).strip()


def _translate_combined(item, headline, body_html):
    """Translate headline and body in one call, with a per-field fallback."""
    combined = '<{tag} data-field="{field}">{headline}</{tag}>{body}'.format(
        tag=HEADLINE_TAG,
        field=HEADLINE_FIELD,
        headline=html.escape(headline),
        body=body_html,
    )
    translated_headline, translated_body = _split_headline_body(
        translate_text(combined, TARGET_LANGUAGE)
    )

    if translated_headline is None:
        logger.warning(
            "Combined translation missing <%s> marker, falling back to "
            "separate calls",
            HEADLINE_TAG,
        )
        item["headline"] = _strip_markup(translate_text(headline, TARGET_LANGUAGE))
        item["body_html"] = translate_text(body_html, TARGET_LANGUAGE)
        return

    item["headline"] = translated_headline
    item["body_html"] = translated_body


def translate_item(item):
    """Translate the headline and body into English and set the language."""
    headline = item.get("headline")
    body_html = item.get("body_html")

    if headline and body_html:
        _translate_combined(item, headline, body_html)
    elif headline:
        item["headline"] = _strip_markup(translate_text(headline, TARGET_LANGUAGE))
    elif body_html:
        item["body_html"] = translate_text(body_html, TARGET_LANGUAGE)

    item["language"] = TARGET_LANGUAGE
    generate_fields(item, FIELDS, force=True, reload=True)


def auto_translate_to_en(item, **kwargs):
    try:
        translate_item(item)
    except Exception:
        logger.exception(
            "Auto translate to en failed",
            extra={"guid": item.get("guid", "unknown")},
        )

    map_packages(item)
    return item


name = "Auto translate to en"
label = name
callback = auto_translate_to_en
access_type = "frontend"
action_type = "direct"
replace_type = "editor_state"
