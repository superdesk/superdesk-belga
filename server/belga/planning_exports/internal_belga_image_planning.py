from typing import List, Dict, Any
from datetime import date
from superdesk.utc import utc_to_local
from superdesk import get_resource_service

from .common import (
    get_formatted_contacts,
    get_item_location,
    set_event_translations_value,
    ADVISORY_TIMEZONE,
    format_advisory_weekday_date,
    format_coverage_label,
    get_display_times,
)

CALENDAR_ORDER = [
    "Sports",
    "General",
    "Politics",
    "Economy",
    "Regional",
    "Justice",
    "International",
    "Culture",
]


def format_image_planning(
    planning_data: List[Dict[str, Any]],
    allowed_coverage_types: set,
    title_prefix: str,
) -> Dict[str, Any]:

    planning_service = get_resource_service("planning")
    desk_service = get_resource_service("desks")
    event_service = get_resource_service("events")

    days: Dict[date, Dict[str, Any]] = {}

    for planning in planning_data:
        event_item = None
        links = []

        if planning.get("event_item"):
            event_item = event_service.find_one(req=None, _id=planning["event_item"])
            if event_item:
                links = event_item.get("links", [])

        calendar = ""
        if event_item and event_item.get("calendars"):
            calendar = event_item["calendars"][0]["qcode"].capitalize()

        planning_nl = planning.copy()
        planning_fr = planning.copy()
        set_event_translations_value(planning_nl, "nl")
        set_event_translations_value(planning_fr, "fr")

        contacts = (
            get_formatted_contacts(event_item)
            if event_item
            else get_formatted_contacts(planning)
        )

        location = (
            get_item_location(event_item, "nl")
            if event_item
            else get_item_location(planning, "nl")
        )

        scheduled = planning.get("planning_date")
        for cov in planning.get("coverages", []):
            if isinstance(cov, dict):
                scheduled = cov.get("planning", {}).get("scheduled", scheduled)
                if scheduled:
                    break

        if not scheduled:
            continue

        local_dt = utc_to_local(ADVISORY_TIMEZONE, scheduled)
        day_date = local_dt.date()

        if day_date not in days:
            days[day_date] = {
                "label": format_advisory_weekday_date(local_dt),
                "calendars": {},
            }

        tz = planning.get("dates", {}).get("tz") or ADVISORY_TIMEZONE
        times = get_display_times(
            {"start": scheduled, "end": scheduled, "tz": tz},
            default_tz=ADVISORY_TIMEZONE,
        )

        event = {
            "calendar": calendar,
            "time": times.get("time", ""),
            "display_time": times.get("display_time", ""),
            "location": location,
            "links": links,
            "contacts": contacts,
            "title_nl": planning.get("name") or planning.get("slugline") or "",
            "title_fr": planning_fr.get("name") or planning_fr.get("slugline") or "",
            "description_nl": (planning_nl.get("description_text") or "").rstrip(),
            "description_fr": (planning_fr.get("description_text") or "").rstrip(),
            "coverages": get_filtered_coverages(
                planning,
                planning_service,
                desk_service,
                allowed_coverage_types,
            ),
        }

        if not event["coverages"]:
            continue

        days[day_date]["calendars"].setdefault(calendar, []).append(event)

    ordered_days = sorted(days.keys())

    return {
        "title": build_title(
            title_prefix,
            [days[d]["label"] for d in ordered_days],
        ),
        "days": days,
        "ordered_days": ordered_days,
        "calendar_order": CALENDAR_ORDER,
    }


def get_filtered_coverages(item, planning_service, desk_service, allowed_types):
    user_service = get_resource_service("users")
    formatted = []
    lang_map = {"nl": "N", "n": "N", "fr": "F", "f": "F"}

    planning_ids = item.get("planning_ids") or [item.get("_id")]

    for pid in planning_ids:
        planning_item = planning_service.find_one(req=None, _id=pid)
        if not planning_item:
            continue

        for coverage in planning_item.get("coverages", []):
            planning_info = coverage.get("planning") or {}
            cov_type = (
                planning_info.get("g2_content_type")
                or coverage.get("g2_content_type")
                or ""
            ).lower()

            if cov_type not in allowed_types:
                continue

            cov_status = (
                coverage.get("news_coverage_status", {}).get("label") or "ON MERIT"
            ).upper()

            desk_language = "N"
            desk_name = ""
            username = ""

            desk_id = planning_info.get("desk")
            if desk_id:
                desk = desk_service.find_one(req=None, _id=desk_id)
                if desk:
                    desk_name = desk.get("name", "")
                    desk_language = lang_map.get(
                        desk.get("desk_language", "").lower(), "N"
                    )

            user_id = coverage.get("assigned_to", {}).get("user")
            if user_id:
                user = user_service.find_one(req=None, _id=user_id)
                if user:
                    username = user.get("sign_off") or user.get("username")

            display = format_coverage_label(cov_type, desk_language, cov_status)

            if username:
                display = f"{display} BY {username.upper()}"
            elif desk_name:
                display = f"{display} BY {desk_name.upper()}"

            formatted.append({"display": display})

    return formatted


def build_title(prefix, days):
    if not days:
        return prefix
    if len(days) == 1:
        return f"{prefix} {days[0]}"
    return f"{prefix} {', '.join(days[:-1])} and {days[-1]}"
