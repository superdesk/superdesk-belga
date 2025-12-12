from .common import (
    set_metadata,
    get_subjects,
    get_formatted_contacts,
    get_item_location,
    set_event_translations_value,
    get_advisory_date_from_events,
    format_coverage_label,
    get_display_times,
    ADVISORY_TIMEZONE,
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
) -> Dict[str, Any]:
    """Format events into bilingual event list for advisory output"""
    events_list: List[Dict[str, Any]] = []
    calendar_groups: Dict[str, List[Dict[str, Any]]] = {}

    # Determine weekday and date from the event
    weekday_date = get_advisory_date_from_events(event_data)

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

        # Use shared helper to compute display times and handle all-day events
        dates = event.get("dates", {})
        times = get_display_times(dates, default_tz=ADVISORY_TIMEZONE)
        formatted_event["time"] = times.get("time", "")
        formatted_event["display_time"] = times.get("display_time", "")

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

    return {"weekday_date": weekday_date, "events": events_list}


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

            coverage_display = format_coverage_label(
                cov_type, desk_language_code, cov_status
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
