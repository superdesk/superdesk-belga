from .common import (
    get_subjects,
    get_formatted_contacts,
    get_item_location,
    set_event_translations_value,
)
from typing import List, Dict, Any
from superdesk.utc import utc_to_local
from superdesk import get_resource_service

CALENDAR_ORDER = [
    "General",
    "Politics",
    "Economy",
    "Regional",
    "Justice",
    "International",
    "Sports",
    "Culture",
]


def format_planning_for_tomorrow_bilingual(
    planning_data: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Format planning items into bilingual event list for advisory output"""
    events_list: List[Dict[str, Any]] = []
    calendar_groups: Dict[str, List[Dict[str, Any]]] = {}

    # Collect unique event IDs from planning items with matching coverages
    event_ids = set()
    standalone_plannings: List[Dict[str, Any]] = []

    for item in planning_data:
        has_valid_coverage = False
        for coverage in item.get("coverages", []):
            cov_type = None

            if isinstance(coverage, dict):
                planning_info = coverage.get("planning") or {}
                cov_type = (planning_info.get("g2_content_type") or "").lower()
            elif isinstance(coverage, str):
                cov_type = coverage.lower()

            if cov_type in ["picture", "video", "text"]:
                has_valid_coverage = True
                if item.get("event_item"):
                    event_ids.add(item["event_item"])

        # If coverage exists but no linked event → keep as standalone planning
        if has_valid_coverage and not item.get("event_item"):
            standalone_plannings.append(item)

    # Fetch associated events
    events_service = get_resource_service("events")
    events = [
        events_service.find_one(req=None, _id=event_id)
        for event_id in event_ids
        if event_id
    ]
    events = [e for e in events if e]

    # Process events for both languages
    for event in events:
        calendar = (
            event["calendars"][0]["qcode"].capitalize()
            if event.get("calendars")
            else "Overig / Divers"
        )

        event_nl = event.copy()
        set_event_translations_value(event_nl, "nl")
        event_fr = event.copy()
        set_event_translations_value(event_fr, "fr")

        formatted_event = {
            "subject": ",".join(get_subjects(event, "nl")),
            "calendar": calendar,
            "contacts": get_formatted_contacts(event),
            "coverages": get_coverages_bilingual(event),
            "location": get_item_location(event, "nl"),
            "links": event.get("links", []),
            "title_nl": event_nl.get("name") or event_nl.get("slugline") or "",
            "title_fr": event_fr.get("name") or event_fr.get("slugline") or "",
            "description_nl": (
                event_nl.get("definition_long")
                or event_nl.get("description_text")
                or event_nl.get("definition_short")
                or ""
            ).rstrip(),
            "description_fr": (
                event_fr.get("definition_long")
                or event_fr.get("description_text")
                or event_fr.get("definition_short")
                or ""
            ).rstrip(),
        }

        # Set dates and handle all-day events
        dates = event["dates"]
        tz = dates.get("tz") or "Europe/Brussels"
        start_local = utc_to_local(tz, dates["start"])
        end_local = utc_to_local(tz, dates["end"])

        # Check if this is an all-day event (00:00-23:59)
        is_all_day = (
            start_local.hour == 0
            and start_local.minute == 0
            and end_local.hour == 23
            and end_local.minute == 59
        )

        formatted_event["time"] = (
            ""
            if is_all_day
            else (f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')}")
        )

        calendar_groups.setdefault(calendar, []).append(formatted_event)

    for planning in standalone_plannings:
        calendar = "Overig / Divers"

        formatted_planning = {
            "subject": "",
            "calendar": calendar,
            "coverages": get_coverages_bilingual(planning),
            "location": get_item_location(planning, "nl"),
            "links": planning.get("links", []),
            "title_nl": planning.get("slugline") or planning.get("headline") or "",
            "title_fr": planning.get("slugline") or planning.get("headline") or "",
            "description_nl": (planning.get("description_text") or "").rstrip(),
            "description_fr": (planning.get("description_text") or "").rstrip(),
            "time": "",
        }

        calendar_groups.setdefault(calendar, []).append(formatted_planning)

    # Sort and merge by CALENDAR_ORDER
    for calendar in CALENDAR_ORDER + sorted(
        [c for c in calendar_groups if c not in CALENDAR_ORDER]
    ):
        if calendar in calendar_groups:
            events_sorted = sorted(
                calendar_groups[calendar], key=lambda x: (x["time"] == "", x["time"])
            )
            events_list.append({"calendar": calendar, "events": events_sorted})

    return events_list


def get_coverages_bilingual(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get coverage info with language and status for bilingual output"""
    formatted_coverages = []
    planning_service = get_resource_service("planning")
    desk_service = get_resource_service("desks")

    lang_map = {"nl": "N", "n": "N", "fr": "F", "f": "F", "de": "N"}

    planning_ids = item.get("planning_ids") or [item.get("_id")]

    for planning_id in planning_ids:
        planning_item = planning_service.find_one(req=None, _id=planning_id)
        if not planning_item:
            continue

        for coverage in planning_item.get("coverages", []):
            if not isinstance(coverage, dict):
                continue

            # Coverage type
            planning_info = coverage.get("planning") or {}
            cov_type = (
                planning_info.get("g2_content_type")
                or coverage.get("g2_content_type")
                or ""
            ).lower()
            cov_status = (
                coverage.get("news_coverage_status", {}).get("label") or "ON MERIT"
            ).upper()

            # Desk language
            desk_language_code = "N"
            desk_id = (
                planning_info.get("desk")
                or coverage.get("assigned_to", {}).get("desk")
                or item.get("task", {}).get("desk")
            )

            if desk_id:
                desk_item = desk_service.find_one(req=None, _id=desk_id)
                if desk_item:
                    lang = desk_item.get("desk_language", "").lower()
                    desk_language_code = lang_map.get(lang, "N")

            # Format coverage display
            if cov_type == "text":
                coverage_display = f"TEXT {desk_language_code} ({cov_status})"
            else:
                coverage_display = f"{cov_type.upper()} ({cov_status})"

            formatted_coverages.append(
                {
                    "display": coverage_display,
                    "type": cov_type,
                    "status": cov_status,
                    "language": desk_language_code,
                }
            )

    return formatted_coverages
