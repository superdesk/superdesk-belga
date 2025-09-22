from .common import (
    set_metadata,
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


def format_event_for_tommorow_bilingual(
    event_data: List[Dict[str, Any]], locale: str
) -> List[Dict[str, Any]]:
    """Format events into bilingual event list for advisory output"""
    events_list: List[Dict[str, Any]] = []
    calendar_groups: Dict[str, List[Dict[str, Any]]] = {}

    # Process events for both languages
    for event in event_data:
        # Get Dutch version
        event_nl = event.copy()
        set_event_translations_value(event_nl, "nl")

        # Get French version
        event_fr = event.copy()
        set_event_translations_value(event_fr, "fr")

        calendar = (
            event["calendars"][0]["qcode"].capitalize()
            if event.get("calendars")
            else "Overig / Divers"
        )

        formatted_event = {
            "subject": ",".join(get_subjects(event, "nl")),
            "calendar": calendar,
            "contacts": get_formatted_contacts(event),
            "coverages": get_coverages_bilingual(event),
            "location": get_item_location(event, "nl"),
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

        # Set metadata (links, etc.)
        set_metadata(formatted_event, event, locale)

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

        if is_all_day:
            # For all-day events, don't show the time range
            formatted_event["time"] = ""
        else:
            # Show specific time range
            formatted_event["time"] = (
                f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')}"
            )

        calendar_groups.setdefault(calendar, []).append(formatted_event)

    # Sort and merge by CALENDAR_ORDER
    for calendar in CALENDAR_ORDER + sorted(
        [c for c in calendar_groups if c not in CALENDAR_ORDER]
    ):
        if calendar in calendar_groups:
            # Sort events: timed events first, then all-day events
            events_sorted = sorted(
                calendar_groups[calendar],
                key=lambda x: (
                    x["time"] == "",
                    x["time"],
                ),  # Empty time (all-day) goes last
            )
            events_list.append({"calendar": calendar, "events": events_sorted})

    return events_list


def get_coverages_bilingual(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get coverages with language information formatted for bilingual output"""
    formatted_coverages = []
    planning_ids = event.get("planning_ids", [])
    planning_service = get_resource_service("planning")
    desk_service = get_resource_service("desks")

    for planning_id in planning_ids:
        planning_item = planning_service.find_one(req=None, _id=planning_id)
        if not planning_item:
            continue

        for coverage in planning_item.get("coverages", []):
            if not isinstance(coverage, dict):
                continue

            planning_info = coverage.get("planning", {})
            cov_type = (planning_info.get("g2_content_type") or "").lower()
            cov_status = (
                coverage.get("news_coverage_status", {})
                .get("label", "ON MERIT")
                .upper()
            )

            desk_language_code = "N"
            desk_id = (
                planning_info.get("desk")
                or coverage.get("assigned_to", {}).get("desk")
                or event.get("task", {}).get("desk")
            )

            if desk_id:
                desk_item = desk_service.find_one(req=None, _id=desk_id)
                if desk_item:
                    lang = desk_item.get("desk_language")
                    if lang:
                        lang = lang.lower()
                        if lang in ("nl", "n", "de"):
                            desk_language_code = "N"
                        elif lang in ("fr", "f"):
                            desk_language_code = "F"
                        else:
                            desk_language_code = "N"

            coverage_display = (
                f"TEXT {desk_language_code} ({cov_status})"
                if cov_type == "text"
                else f"{cov_type.upper()} ({cov_status})"
            )

            formatted_coverages.append(
                {
                    "display": coverage_display,
                    "type": cov_type,
                    "status": cov_status,
                    "language": desk_language_code,
                }
            )

    return formatted_coverages
