from .common import (
    get_subjects,
    get_formatted_contacts,
    get_item_location,
    set_event_translations_value,
    ADVISORY_TIMEZONE,
    format_advisory_weekday_date,
    format_coverage_label,
    get_display_times,
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


def format_planning_for_tomorrow_bilingual_internal(
    planning_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Format planning items into bilingual advisory output"""
    events_list: List[Dict[str, Any]] = []
    calendar_groups: Dict[str, List[Dict[str, Any]]] = {}

    planning_service = get_resource_service("planning")
    desk_service = get_resource_service("desks")
    event_service = get_resource_service("events")

    # weekday and date
    weekday_date = ""
    if planning_data:
        first_planning = planning_data[0]
        weekday_date = get_advisory_weekday_date(
            first_planning,
            planning_service=planning_service,
            event_service=event_service,
        )

    # Process each planning
    for planning in planning_data:
        # Fetch linked event
        event_item = None
        event_links = []
        if planning.get("event_item"):
            event_item = event_service.find_one(req=None, _id=planning["event_item"])
            if event_item:
                event_links = event_item.get("links", [])

        # Calendar
        calendar = ""
        if event_item and event_item.get("calendars"):
            calendar = event_item["calendars"][0]["qcode"].capitalize()

        # Set translations
        planning_nl = planning.copy()
        set_event_translations_value(planning_nl, "nl")
        planning_fr = planning.copy()
        set_event_translations_value(planning_fr, "fr")

        # Contacts
        contacts = (
            get_formatted_contacts(event_item)
            if event_item
            else get_formatted_contacts(planning)
        )

        # Location
        location = (
            get_item_location(event_item, "nl")
            if event_item
            else get_item_location(planning, "nl")
        )

        # Format item
        formatted_planning = {
            "subject": ",".join(get_subjects(planning, "nl")),
            "calendar": calendar,
            "contacts": contacts,
            "coverages": get_coverages_bilingual_internal(
                planning, planning_service, desk_service
            ),
            "location": location,
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
        }

        # Set time from first coverage or planning date
        scheduled = planning.get("planning_date")
        coverages = planning.get("coverages", [])
        if coverages and isinstance(coverages[0], dict):
            scheduled = coverages[0].get("planning", {}).get("scheduled", scheduled)
        if scheduled:
            tz = planning.get("dates", {}).get("tz") or ADVISORY_TIMEZONE
            times = get_display_times(
                {"start": scheduled, "end": scheduled, "tz": tz},
                default_tz=ADVISORY_TIMEZONE,
            )
            formatted_planning["time"] = times.get("time", "")
            formatted_planning["display_time"] = times.get("display_time", "")
        else:
            formatted_planning["display_time"] = ""

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

    return {"weekday_date": weekday_date, "events": events_list}


def get_coverages_bilingual_internal(
    item: Dict[str, Any], planning_service, desk_service
) -> List[Dict[str, Any]]:
    """Get coverage info with proper status and language for export"""
    user_service = get_resource_service("users")
    formatted_coverages = []
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

            # Coverage status
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

            assigned_user_id = coverage.get("assigned_to", {}).get("user")
            username = ""
            desk_name = ""

            if assigned_user_id:
                # Coverage assigned to a user
                user_item = user_service.find_one(req=None, _id=assigned_user_id)
                if user_item:
                    username = user_item.get("sign_off") or user_item.get("username")

            if desk_id:
                desk_item = desk_service.find_one(req=None, _id=desk_id)
                if desk_item:
                    # Get desk name for display
                    desk_name = desk_item.get("name", "")

                    if desk_item and desk_item.get("desk_language"):
                        desk_language_code = lang_map.get(
                            desk_item["desk_language"].lower(), "N"
                        )

            # Format coverage display
            coverage_display = format_coverage_label(
                cov_type, desk_language_code, cov_status
            )

            # Add assigned user or desk name
            if username:
                coverage_display = f"{coverage_display} BY {username.upper()}"
            elif desk_name:
                # When no user assigned, show full desk name only
                coverage_display = f"{coverage_display} BY {desk_name.upper()}"

            formatted_coverages.append(
                {
                    "display": coverage_display,
                    "type": cov_type,
                    "status": cov_status,
                    "language": desk_language_code,
                    "username": username,
                    "desk_name": desk_name,
                }
            )

    return formatted_coverages


def get_advisory_weekday_date(planning_item, planning_service=None, event_service=None):
    """Get weekday/date of planning, preferring linked event date"""
    # If planning has linked event, use event start date
    event_item = None
    if event_service and planning_item.get("event_item"):
        event_item = event_service.find_one(req=None, _id=planning_item["event_item"])
        if event_item and event_item.get("dates") and event_item["dates"].get("start"):
            tz = event_item["dates"].get("tz", ADVISORY_TIMEZONE)
            local_dt = utc_to_local(tz, event_item["dates"]["start"])
            return format_advisory_weekday_date(local_dt)

    # Otherwise, fallback to scheduled in coverages or planning_date
    if planning_service:
        planning_item = planning_service.find_one(req=None, _id=planning_item["_id"])

    coverages = planning_item.get("coverages", [])
    scheduled = None

    # Find scheduled from coverage
    for cov in coverages:
        if isinstance(cov, dict):
            scheduled = cov.get("planning", {}).get("scheduled")
            if scheduled:
                break

    # Fallback to planning_date
    if not scheduled:
        scheduled = planning_item.get("planning_date")

    if scheduled:
        local_dt = utc_to_local(ADVISORY_TIMEZONE, scheduled)
        return format_advisory_weekday_date(local_dt)

    return ""
