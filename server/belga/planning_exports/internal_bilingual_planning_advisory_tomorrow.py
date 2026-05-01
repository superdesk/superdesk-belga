from .common import (
    get_subjects,
    get_formatted_contacts,
    get_item_location,
    set_event_translations_value,
    get_advisory_weekday_date,
    get_coverages_bilingual,
    sort_calendar_groups,
    get_planning_display_times,
)
from typing import List, Dict, Any
import json
from markupsafe import Markup
from superdesk import get_resource_service


def format_planning_for_tomorrow_bilingual_internal(
    planning_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Format planning items into bilingual advisory output for internal use"""
    calendar_groups: Dict[str, List[Dict[str, Any]]] = {}
    event_service = get_resource_service("events")

    weekday_date = ""
    if planning_data:
        weekday_date = get_advisory_weekday_date(planning_data[0])

    for planning in planning_data:
        event_item = None
        event_links = []
        if planning.get("event_item"):
            event_item = event_service.find_one(req=None, _id=planning["event_item"])
            if event_item:
                event_links = event_item.get("links", [])

        calendar = ""
        if event_item and event_item.get("calendars"):
            calendar = event_item["calendars"][0]["qcode"].capitalize()

        planning_nl = planning.copy()
        planning_fr = planning.copy()
        set_event_translations_value(planning_nl, "nl")
        set_event_translations_value(planning_fr, "fr")

        formatted_planning = {
            "subject": ",".join(get_subjects(planning, "nl")),
            "calendar": calendar,
            "contacts": get_formatted_contacts(event_item if event_item else planning),
            "coverages": get_coverages_bilingual(planning, include_assignee=True),
            "location": get_item_location(event_item if event_item else planning, "nl"),
            "links": event_links,
            "title_nl": planning.get("name")
            or planning.get("slugline")
            or planning.get("headline")
            or "",
            "title_fr": planning_fr.get("name")
            or planning_fr.get("slugline")
            or planning_fr.get("headline")
            or "",
            "description_nl": (planning_nl.get("description_text") or "").rstrip(),
            "description_fr": (planning_fr.get("description_text") or "").rstrip(),
            "time": "",
            "display_time": "",
        }

        # Use event dates if available, otherwise fall back to coverage scheduled / planning_date
        formatted_planning["time"], formatted_planning["display_time"] = (
            get_planning_display_times(planning, event_item)
        )

        calendar_groups.setdefault(calendar, []).append(formatted_planning)

    return {
        "weekday_date": weekday_date,
        "events": sort_calendar_groups(calendar_groups),
    }


def format_planning_for_tomorrow_bilingual_internal_event_ids_json(
    planning_data: List[Dict[str, Any]],
) -> str:
    """Return a JSON list of unique event IDs for the selected planning items.

    Used by the "Event IDs: Program of the day for internal use" custom layout.
    The selection of valid items (events with associated planning items, including
    those with the internal Calendar set) is performed by the user in the
    Planning only view, so no coverage-type or calendar filtering is applied here.
    """
    event_ids: List[str] = []
    seen_ids = set()

    for planning in planning_data:
        event_item = planning.get("event_item")
        if not event_item:
            continue

        event_id = str(event_item)
        if event_id in seen_ids:
            continue

        seen_ids.add(event_id)
        event_ids.append(event_id)

    return Markup(json.dumps(event_ids))
