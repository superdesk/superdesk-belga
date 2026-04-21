from .common import (
    get_subjects,
    get_formatted_contacts,
    get_item_location,
    set_event_translations_value,
    is_editorial_calendar,
    get_advisory_weekday_date,
    get_coverages_bilingual,
    sort_calendar_groups,
    get_planning_display_times,
)
from typing import List, Dict, Any
from superdesk import get_resource_service


def format_planning_for_tomorrow_bilingual(
    planning_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Format planning items into bilingual advisory output"""
    calendar_groups: Dict[str, List[Dict[str, Any]]] = {}
    event_service = get_resource_service("events")

    weekday_date = ""
    if planning_data:
        weekday_date = get_advisory_weekday_date(planning_data[0])

    # Process each planning
    for planning in planning_data:
        # Fetch linked event
        event_item = None
        event_links = []
        if planning.get("event_item"):
            event_item = event_service.find_one(req=None, _id=planning["event_item"])
            if event_item and is_editorial_calendar(event_item):
                continue
            if event_item:
                event_links = event_item.get("links", [])

        planning_nl = planning.copy()
        planning_fr = planning.copy()
        set_event_translations_value(planning_nl, "nl")
        set_event_translations_value(planning_fr, "fr")

        event_nl = None
        event_fr = None
        if event_item:
            event_nl = event_item.copy()
            event_fr = event_item.copy()
            set_event_translations_value(event_nl, "nl")
            set_event_translations_value(event_fr, "fr")

        calendar = "Overig / Divers"
        if event_item and event_item.get("calendars"):
            calendar = event_item["calendars"][0]["qcode"].capitalize()

        title_nl = (
            (event_nl.get("name") if event_nl else None)
            or planning_nl.get("name")
            or planning_nl.get("slugline")
            or planning_nl.get("headline")
            or ""
        )

        title_fr = (
            (event_fr.get("name") if event_fr else None)
            or planning_fr.get("name")
            or planning_fr.get("slugline")
            or planning_fr.get("headline")
            or ""
        )

        formatted_planning = {
            "subject": ",".join(get_subjects(planning, "nl")),
            "calendar": calendar,
            "contacts": get_formatted_contacts(event_item if event_item else planning),
            "coverages": get_coverages_bilingual(planning),
            "location": get_item_location(event_item if event_item else planning, "nl"),
            "links": event_links,
            "title_nl": title_nl,
            "title_fr": title_fr,
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
