import re
import logging
import superdesk
from typing import List

from datetime import timedelta, time
from superdesk.metadata.item import CONTENT_STATE, PUBLISH_SCHEDULE, SCHEDULE_SETTINGS
from superdesk.macros.internal_destination_auto_publish import (
    internal_destination_auto_publish,
)
from superdesk.editor_utils import replace_text, filter_blocks
from apps.archive.common import update_schedule_settings
from superdesk.errors import StopDuplication, DocumentError
from superdesk.text_utils import get_word_count
from superdesk.utc import utcnow, utc_to_local


CREDITS = "credits"
SOURCES = "sources"
COUNTRY = "country"
PRODUCTS = "services-products"

BRIEF_SOURCE = BRIEF_CREDIT = "BELGA"
DEFAULT_PRODUCT = "NEWS/GENERAL"
PRODUCT_MAPPING = {
    "NEWS/SPORTS": ("SPN/", "SPF/"),
    "NEWS/POLITICS": ("/POL",),
    "NEWS/ECONOMY": ("/ECO",),
}

TEXT_PROFILE = "TEXT"
BRIEF_PROFILE = "BRIEF"

logger = logging.getLogger(__name__)


def _get_profile_id(label):
    profile = superdesk.get_resource_service("content_types").find_one(
        req=None, label=label
    )
    if profile:
        return profile["_id"]
    return None


def _find_subj(subject: List, scheme: str):
    return next((subj for subj in subject if subj.get("scheme") == scheme), None)


def _get_brief_subject(subject: List) -> List:
    if not subject:
        subject = []
    credit = _find_subj(subject, CREDITS)
    if credit and "BELGA" not in credit.get("qcode"):
        credit["name"] = credit["qcode"] = BRIEF_CREDIT
    elif not credit:
        subject.append(
            {
                "name": BRIEF_CREDIT,
                "qcode": BRIEF_CREDIT,
                "scheme": CREDITS,
            }
        )
    source = _find_subj(subject, SOURCES)
    if not source:
        # if no source found, append BRIEF_SOURCE
        subject.append(
            {
                "name": BRIEF_SOURCE,
                "qcode": BRIEF_SOURCE,
                "scheme": SOURCES,
            }
        )
    elif "BELGA" not in [
        subj.get("qcode") for subj in subject if subj.get("scheme") == SOURCES
    ]:
        # append BRIEF_SOURCE only if BELGA is not already in sources
        subject.append(
            {
                "name": BRIEF_SOURCE,
                "qcode": BRIEF_SOURCE,
                "scheme": SOURCES,
            }
        )
    return subject


def _get_product_subject(subject: List) -> List:
    if not subject:
        subject = []
    product = _find_subj(subject, PRODUCTS)
    if product:
        name = product.get("name") or ""
        next_value = DEFAULT_PRODUCT
        for value, items in PRODUCT_MAPPING.items():
            if any([item for item in items if item in name]):
                next_value = value
                break
        product["name"] = product["qcode"] = next_value
        if name.startswith(("BIN/", "INT/")):
            subject = [subj for subj in subject if subj.get("scheme") != COUNTRY]
            subject.append(
                {
                    "name": "Belgium",
                    "qcode": "country_bel",
                    "scheme": COUNTRY,
                }
            )
    return subject


def _fix_headline(item):
    for old in (" BELGANIGHT", "BELGANIGHT ", "BELGANIGHT"):
        replace_text(item, "headline", old, "", is_html=False)


class BlockFilter:
    filtered = False

    def __call__(self, block):
        if not self.filtered and any(
            [pattern in block.text for pattern in ("Disclaimer:", "ATTENTION USERS")]
        ):
            self.filtered = True
        return not self.filtered


def _fix_body_html(item):
    filter_blocks(item, "body_html", BlockFilter())


def brief_internal_routing(item: dict, **kwargs):
    guid = item.get("guid", "unknown")
    logger.info("macro started item=%s", guid)

    try:
        assert str(item["profile"]) == str(
            _get_profile_id(TEXT_PROFILE)
        ), "profile is not text"
        assert get_word_count(item["body_html"]) < 301, "body is too long"
        # The title should not start with the word "CORRECTION"
        if item.get("headline"):
            title_start_with_correction = (
                item["headline"].lstrip().startswith("CORRECTION")
            )
            assert (
                not title_start_with_correction
            ), "The headline/title should not start with word CORRECTION"
    except AssertionError as err:
        logger.info("macro stop on assert item=%s error=%s", guid, err)
        raise StopDuplication()
    except KeyError as err:
        logger.error(err)
        raise StopDuplication()

    item.setdefault("subject", [])
    item["urgency"] = 2
    item["profile"] = _get_profile_id(BRIEF_PROFILE)
    item["subject"] = _get_product_subject(_get_brief_subject(item.get("subject", [])))
    item["status"] = CONTENT_STATE.SCHEDULED
    item["operation"] = "publish"

    _fix_headline(item)
    _fix_body_html(item)

    UTC_FIELD = "utc_{}".format(PUBLISH_SCHEDULE)
    try:
        published_at = item[SCHEDULE_SETTINGS][UTC_FIELD]
    except KeyError:
        published_at = utcnow()
    item[SCHEDULE_SETTINGS] = {
        "time_zone": "Europe/Brussels",
    }

    # Set item publish schedule to 7:30 am for autopublish between 4 to 7 am
    is_press_headline = item.get("headline") and "press" in item["headline"].lower()
    current_datetime = utc_to_local(superdesk.app.config["DEFAULT_TIMEZONE"], utcnow())
    if is_press_headline and time(4, 00) <= current_datetime.time() <= time(7, 00):
        item[PUBLISH_SCHEDULE] = current_datetime.replace(hour=7, minute=30, second=00)
        logger.info(
            "Set publish schedule to 7:30 am for autopublish between 4 to 7 am item=%s",
            item.get("guid", "unknown"),
        )
    else:
        # schedule +30m
        item[PUBLISH_SCHEDULE] = utc_to_local(
            item[SCHEDULE_SETTINGS]["time_zone"], published_at + timedelta(minutes=30)
        )

    update_schedule_settings(item, PUBLISH_SCHEDULE, item[PUBLISH_SCHEDULE])
    item[PUBLISH_SCHEDULE] = item[PUBLISH_SCHEDULE].replace(tzinfo=None)

    # remove text in () brackets along with brackets
    if item.get("headline"):
        title = re.sub(r"\([^()]*\)", "", item["headline"])
        item["headline"] = " ".join(title.split())

    # publish
    try:
        internal_destination_auto_publish(item)
    except StopDuplication:
        logger.info("macro done item=%s", guid)
    except DocumentError as err:
        logger.error("validation error when creating brief item=%s error=%s", guid, err)
    except Exception as err:
        logger.exception(err)

    # avoid another item to be created
    raise StopDuplication()


name = "Brief internal routing"
label = "Brief internal routing"
callback = brief_internal_routing
access_type = "frontend"
action_type = "direct"
