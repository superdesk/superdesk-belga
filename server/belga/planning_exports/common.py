from superdesk.utc import utc_to_local
from flask import current_app as app
from typing import List, Dict, Any
from babel.dates import format_date


def set_item_title(item: Dict[str, Any], event: Dict[str, Any]):
    """Set the item's title

    Prioritise the Event's slugline/name before Planning item's
    """

    item["title"] = event.get("name") or event.get("slugline") or ""


def set_item_description(item: Dict[str, Any], event: Dict[str, Any]):
    """Set the item's description

    Prioritise the Event's description before Planning item's
    """

    description = (
        event.get("definition_long")
        or event.get("description_text")
        or event.get("definition_short")
        or ""
    ).rstrip()
    item["description"] = description


def set_item_dates(item: Dict[str, Any], event: Dict[str, Any]):
    """Set the item's dates to be used for sorting"""
    item["dates"] = {
        "start": event["dates"]["start"],
        "tz": event["dates"]["tz"],
    }

    tz = item["dates"].get("tz") or app.config.get("DEFAULT_TIMEZONE")
    start_local = utc_to_local(tz, item["dates"]["start"])
    start_local_str = start_local.strftime("%Hu%M")

    item["local_time"] = start_local_str
    item["local_date_time"] = start_local


def set_item_location(item: Dict[str, Any], event: Dict[str, Any]):
    """Set the location to be used for sorting / displaying"""

    item.setdefault("address", {})
    if len(event.get("location") or []):
        try:
            location = event.get("location", {})[0]
            address = location.get("address") or {}
            item["address"] = {
                "country": address["country"] if address.get("country") else "",
                "city": address["city"] if address.get("city") else "",
                "name": address.get("city") or location.get("name") or "",
            }
        except (IndexError, KeyError):
            pass


def get_language_name(item: Dict[str, Any], language: str):
    return ((item.get("translations") or {}).get("name") or {}).get(
        language
    ) or item.get("name")


def get_subject(event: Dict[str, Any], language: str):
    subjects = event.get("subject")
    filter_subj = []
    if subjects:
        for subj in subjects:
            if subj.get("scheme") == "belga-keywords":
                filter_subj.append(get_language_name(subj, language))
        return filter_subj
    return []


def format_datetime(event: Dict[str, Any], locale: str, format: str):
    tz = event.get("dates", {}).get("tz") or app.config.get("DEFAULT_TIMEZONE")
    start_time = event.get("dates", {}).get("start")
    return format_date(utc_to_local(tz, start_time), format, locale=locale).capitalize()


def set_metadata(formatted_event: Dict[str, Any], event: Dict[str, Any]):
    formatted_event["links"] = event.get("links", "")
    set_item_dates(formatted_event, event)
    set_item_title(formatted_event, event)
    set_item_description(formatted_event, event)
    set_item_location(formatted_event, event)
