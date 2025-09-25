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
    """Format planning items into bilingual advisory output"""
    events_list: List[Dict[str, Any]] = []
    calendar_groups: Dict[str, List[Dict[str, Any]]] = {}

    planning_service = get_resource_service("planning")
    desk_service = get_resource_service("desks")
    event_service = get_resource_service("events")
    VALID_COVERAGE_TYPES = [
        "text",
        "picture",
        "video",
        "audio",
        "infographics",
        "live_video",
        "live_blog",
    ]

    for planning in planning_data:
        coverages = planning.get("coverages", [])
        has_valid_coverage = any(
            (
                (
                    c.get("planning", {}).get("g2_content_type")
                    if isinstance(c, dict)
                    else c
                )
                or ""
            ).lower()
            in VALID_COVERAGE_TYPES
            for c in coverages
        )
        if not has_valid_coverage:
            continue

        # Set calendar from linked event if exists
        calendar = "Overig / Divers"
        if planning.get("event_item"):
            event_item = event_service.find_one(req=None, _id=planning["event_item"])
            if event_item and event_item.get("calendars"):
                calendar = event_item["calendars"][0]["qcode"].capitalize()

        # Set translations
        planning_nl = planning.copy()
        set_event_translations_value(planning_nl, "nl")
        planning_fr = planning.copy()
        set_event_translations_value(planning_fr, "fr")

        # Format item
        formatted_planning = {
            "subject": ",".join(get_subjects(planning, "nl")),
            "calendar": calendar,
            "contacts": get_formatted_contacts(planning),
            "coverages": get_coverages_bilingual(
                planning, planning_service, desk_service
            ),
            "location": get_item_location(planning, "nl"),
            "links": planning.get("links", []),
            "title_nl": planning.get("name")
            or planning.get("slugline")
            or planning.get("headline")
            or "",
            "title_fr": planning.get("name")
            or planning.get("slugline")
            or planning.get("headline")
            or "",
            "description_nl": (planning_nl.get("description_text") or "").rstrip(),
            "description_fr": (planning_fr.get("description_text") or "").rstrip(),
            "topic_nl": planning_nl.get("slugline", ""),
            "topic_fr": planning_fr.get("slugline", ""),
            "time": "",
        }

        # Set time from first coverage or planning date
        scheduled = planning.get("planning_date")
        if coverages and isinstance(coverages[0], dict):
            scheduled = coverages[0].get("planning", {}).get("scheduled", scheduled)
        if scheduled:
            tz = "Europe/Brussels"
            start_local = utc_to_local(tz, scheduled)
            formatted_planning["time"] = start_local.strftime("%H:%M")

        calendar_groups.setdefault(calendar, []).append(formatted_planning)

    # Merge and sort by CALENDAR_ORDER
    for calendar in CALENDAR_ORDER + sorted(
        [c for c in calendar_groups if c not in CALENDAR_ORDER]
    ):
        if calendar in calendar_groups:
            events_sorted = sorted(
                calendar_groups[calendar], key=lambda x: (x["time"] == "", x["time"])
            )
            events_list.append({"calendar": calendar, "events": events_sorted})

    return events_list


def get_coverages_bilingual(
    item: Dict[str, Any], planning_service, desk_service
) -> List[Dict[str, Any]]:
    """Get coverage info with proper status and language for export"""
    formatted_coverages = []
    lang_map = {"nl": "N", "n": "N", "fr": "F", "f": "F", "de": "N"}

    # Get all planning IDs to fetch full coverage info
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

            # Coverage status
            cov_status = (
                coverage.get("news_coverage_status", {}).get("label") or "ON MERIT"
            ).upper()

            # Desk language
            desk_language_code = "N"
            desk_id = planning_info.get("desk") or item.get("task", {}).get("desk")
            if desk_id:
                desk_item = desk_service.find_one(req=None, _id=desk_id)
                if desk_item and desk_item.get("desk_language"):
                    desk_language_code = lang_map.get(
                        desk_item["desk_language"].lower(), "N"
                    )

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
