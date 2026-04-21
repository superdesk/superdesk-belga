from .common import (
    set_metadata,
    get_subjects,
    get_formatted_contacts,
    get_coverages,
    get_item_location,
    set_event_translations_value,
    CALENDAR_ORDER,
)
from typing import List, Dict, Any
from superdesk.utc import utc_to_local
from superdesk import get_resource_service


def format_planning_for_tomorrow(
    planning_data: List[Dict[str, Any]], locale: str
) -> List[Dict[str, Any]]:
    events_list: List[Dict[str, Any]] = []
    calendar_groups: Dict[str, List[Dict[str, Any]]] = {}

    # Collect unique event IDs from planning items with matching coverages
    event_ids = set()
    for item in planning_data:
        for coverage in item.get("coverages", []):
            cov_type = None

            if isinstance(coverage, dict):
                planning_info = coverage.get("planning") or {}
                cov_type = (planning_info.get("g2_content_type") or "").lower()
            elif isinstance(coverage, str):
                cov_type = coverage.lower()

            if cov_type in ["picture", "video"] and item.get("event_item"):
                event_ids.add(item["event_item"])

    # Fetch associated events
    events_service = get_resource_service("events")
    events = [
        events_service.find_one(req=None, _id=event_id)
        for event_id in event_ids
        if event_id
    ]
    events = [e for e in events if e]

    # Process events
    for event in events:
        set_event_translations_value(event, locale)

        calendar = (
            event["calendars"][0]["qcode"].capitalize()
            if event.get("calendars")
            else "Overig / Divers"
        )

        formatted_event = {
            "subject": ",".join(get_subjects(event, locale)),
            "calendars": calendar,
            "contacts": get_formatted_contacts(event),
            "coverages": get_coverages(event, locale),
            "location": get_item_location(event, locale),
            "links": event.get("links", []),
        }
        set_metadata(formatted_event, event, locale)

        dates = formatted_event["dates"]
        start_local = utc_to_local(dates["tz"], dates["start"])
        end_local = utc_to_local(dates["tz"], dates["end"])
        formatted_event["time"] = (
            f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')}"
        )

        calendar_groups.setdefault(calendar, []).append(formatted_event)

    # Sort and merge by CALENDAR_ORDER
    for calendar in CALENDAR_ORDER + sorted(
        [c for c in calendar_groups if c not in CALENDAR_ORDER]
    ):
        if calendar in calendar_groups:
            events_sorted = sorted(calendar_groups[calendar], key=lambda x: x["time"])
            events_list.append({"calendar": calendar, "events": events_sorted})

    return events_list
