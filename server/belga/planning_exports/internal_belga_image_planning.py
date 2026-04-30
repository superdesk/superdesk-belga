from typing import List, Dict, Any
import json
import datetime
from datetime import date
from markupsafe import Markup
from superdesk.utc import utc_to_local
from superdesk import get_resource_service

from .common import (
    get_formatted_contacts,
    get_item_location,
    set_event_translations_value,
    ADVISORY_TIMEZONE,
    format_advisory_weekday_date,
    get_display_times,
    get_planning_schedule_info,
    is_editorial_calendar,
)

CALENDAR_ORDER_PHOTO = ["Sports", "General"]


def format_image_planning_event_ids_json(
    planning_data: List[Dict[str, Any]],
    allowed_coverage_types: set,
) -> str:
    event_ids = []
    seen_ids = set()

    for planning in planning_data:
        event_item = planning.get("event_item")
        if not event_item:
            continue

        if not has_allowed_coverage(
            planning.get("coverages", []), allowed_coverage_types
        ):
            continue

        event_id = str(event_item)
        if event_id in seen_ids:
            continue

        seen_ids.add(event_id)
        event_ids.append(event_id)

    return Markup(json.dumps(event_ids))


def format_image_planning(
    planning_data: List[Dict[str, Any]],
    allowed_coverage_types: set,
    title_prefix: str,
    group_by_calendar: bool = True,
    sports_first: bool = False,
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
                if is_editorial_calendar(event_item):
                    continue

        calendar = ""
        if event_item and event_item.get("calendars"):
            calendar = event_item["calendars"][0]["qcode"].capitalize()
            if sports_first and calendar != "Sports":
                calendar = "General"

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

        scheduled, display_dates, tz = get_planning_schedule_info(planning, event_item)

        if not scheduled:
            continue

        try:
            local_dt = utc_to_local(tz, scheduled)
        except ValueError:
            try:
                local_dt = utc_to_local(ADVISORY_TIMEZONE, scheduled)
            except ValueError:
                continue
        day_date = local_dt.date()

        if day_date not in days:
            days[day_date] = {
                "label": format_advisory_weekday_date(local_dt),
                "calendars": {},
            }

        times = get_display_times(display_dates, default_tz=ADVISORY_TIMEZONE)

        event = {
            "calendar": calendar,
            "scheduled": scheduled,
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

    if group_by_calendar:
        calendar_order = CALENDAR_ORDER_PHOTO if sports_first else None
        return {
            "title": build_title(
                title_prefix,
                [days[d]["label"] for d in ordered_days],
            ),
            "days": days,
            "ordered_days": ordered_days,
            "calendar_order": calendar_order,
            "group_by_calendar": True,
        }
    else:
        for day in ordered_days:
            day_calendars = days[day]["calendars"]
            all_day_events = []
            for cal in day_calendars:
                all_day_events.extend(day_calendars[cal])
            all_day_events.sort(
                key=lambda e: e.get("scheduled")
                or datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)
            )
            days[day]["events"] = all_day_events
        return {
            "title": build_title(
                title_prefix,
                [days[d]["label"] for d in ordered_days],
            ),
            "days": days,
            "ordered_days": ordered_days,
            "group_by_calendar": False,
        }


def has_allowed_coverage(coverages, allowed_types) -> bool:
    for cov in coverages:
        if isinstance(cov, dict):
            cov_type = (
                (cov.get("planning") or {}).get("g2_content_type")
                or cov.get("g2_content_type")
                or ""
            )
        else:
            cov_type = cov or ""
        if cov_type.lower() in allowed_types:
            return True
    return False


def get_filtered_coverages(item, planning_service, desk_service, allowed_types):
    user_service = get_resource_service("users")
    formatted = []

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

            desk_name = ""
            username = ""

            desk_id = planning_info.get("desk")
            if desk_id:
                desk = desk_service.find_one(req=None, _id=desk_id)
                if desk:
                    desk_name = desk.get("name", "")

            user_id = coverage.get("assigned_to", {}).get("user")
            if user_id:
                user = user_service.find_one(req=None, _id=user_id)
                if user:
                    username = user.get("sign_off") or user.get("username")

            if username:
                display = username.upper()
            elif desk_name:
                display = desk_name.upper()
            else:
                display = cov_status

            formatted.append({"display": display})

    return formatted


def build_title(prefix, days):
    if not days:
        return prefix
    if len(days) == 1:
        return f"{prefix} {days[0]}"
    return f"{prefix} {', '.join(days[:-1])} and {days[-1]}"
