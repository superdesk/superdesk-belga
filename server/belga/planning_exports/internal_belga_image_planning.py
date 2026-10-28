from typing import List, Dict, Any
import datetime
from datetime import date
from markupsafe import Markup
from superdesk.utc import utc_to_local
from superdesk.core import json
from superdesk import get_resource_service
from planning.utils import get_related_event_ids_for_planning

from .common import (
    get_item_location,
    get_item_coverages,
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
        try:
            event_id = get_related_event_ids_for_planning(planning, "primary")[0]
        except IndexError:
            event_id = None

        if not event_id or event_id in seen_ids:
            continue

        elif not has_allowed_coverage(
            planning.get("coverages", []), allowed_coverage_types
        ):
            continue

        seen_ids.add(event_id)
        event_ids.append(event_id)

    return Markup(json.dumps(event_ids))


async def format_image_planning(
    event_data: List[Dict[str, Any]],
    allowed_coverage_types: set,
    title_prefix: str,
    group_by_calendar: bool = True,
    sports_first: bool = False,
) -> Dict[str, Any]:

    desk_service = get_resource_service("desks")

    days: Dict[date, Dict[str, Any]] = {}

    for event in event_data:
        if is_editorial_calendar(event):
            continue

        calendar = ""
        if event.get("calendars"):
            calendar = event["calendars"][0]["qcode"].capitalize()
            if sports_first and calendar != "Sports":
                calendar = "General"

        event_nl = event.copy()
        event_fr = event.copy()
        set_event_translations_value(event_nl, "nl")
        set_event_translations_value(event_fr, "fr")

        location = await get_item_location(event, "nl")

        scheduled, display_dates, tz = get_planning_schedule_info(event_item=event)

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

        times = get_display_times(display_dates, default_tz=ADVISORY_TIMEZONE)

        formatted_event = {
            "calendar": calendar,
            "scheduled": scheduled,
            "time": times.get("time", ""),
            "display_time": times.get("display_time", ""),
            "location": location,
            "links": event.get("links") or [],
            "title_nl": event_nl.get("name") or event_nl.get("slugline") or "",
            "title_fr": event_fr.get("name") or event_fr.get("slugline") or "",
            "coverages": await get_filtered_coverages(
                event,
                desk_service,
                allowed_coverage_types,
            ),
        }

        if not formatted_event["coverages"]:
            continue

        if day_date not in days:
            days[day_date] = {
                "label": format_advisory_weekday_date(local_dt),
                "calendars": {},
            }

        days[day_date]["calendars"].setdefault(calendar, []).append(formatted_event)

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


async def get_filtered_coverages(item, desk_service, allowed_types):
    user_service = get_resource_service("users")
    formatted = []

    for coverage in await get_item_coverages(item):
        planning_info = coverage.get("planning") or {}
        cov_type = (
            planning_info.get("g2_content_type")
            or coverage.get("g2_content_type")
            or ""
        ).lower()

        if cov_type not in allowed_types:
            continue

        cov_status = (
            (coverage.get("news_coverage_status") or {}).get("label") or "ON MERIT"
        ).upper()

        desk_name = ""
        username = ""

        desk_id = planning_info.get("desk") or (coverage.get("assigned_to") or {}).get(
            "desk"
        )
        if desk_id:
            desk = await desk_service.find_one_async(req=None, _id=desk_id)
            if desk:
                desk_name = desk.get("name", "")

        user_id = (coverage.get("assigned_to") or {}).get("user")
        if user_id:
            user = await user_service.find_one_async(req=None, _id=user_id)
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
