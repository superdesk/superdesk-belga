from superdesk.utc import utc_to_local
from flask import current_app as app
from typing import List, Dict, Any, TypedDict
from babel.dates import format_date
from superdesk import get_resource_service
from typing import Union as _Union
from datetime import date as _date_type, datetime as _datetime_type

ADVISORY_TIMEZONE = "Europe/Brussels"
COVERAGE_PREFIX = "BELGA"

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


class FormattedContact(TypedDict):
    name: str
    organisation: str
    email: List[str]
    phone: List[str]
    mobile: List[str]
    website: str
    job_title: str


def set_item_title(item: Dict[str, Any], event: Dict[str, Any]):
    """Set the item's title

    Prioritise the Event's slugline/name before Planning item's
    """

    item["title"] = event.get("name") or event.get("slugline") or ""


def set_item_description(item: Dict[str, Any], event: Dict[str, Any]):
    """Set the item's description

    Prioritise the Event's description before Planning item's
    """

    description = (
        event.get("definition_long")
        or event.get("description_text")
        or event.get("definition_short")
        or ""
    ).rstrip()
    item["description"] = description


def set_item_dates(item: Dict[str, Any], event: Dict[str, Any]):
    """Set the item's dates to be used for sorting"""
    dates = event.get("dates") or {}
    start = dates.get("start")
    end = dates.get("end")
    tz = dates.get("tz") or app.config.get("DEFAULT_TIMEZONE")

    item["dates"] = {"start": start, "end": end, "tz": tz}

    if not start:
        item["local_time"] = ""
        item["local_date_time"] = ""
        return

    try:
        start_local = utc_to_local(tz, start)
    except ValueError:
        item["local_time"] = ""
        item["local_date_time"] = ""
        return

    item["local_time"] = start_local.strftime("%H:%M")
    item["local_date_time"] = start_local.strftime("%Y%m%d")


def format_coverage_label(cov_type: str, language_code: str, status: str) -> str:
    """
    Return a coverage label prefixed with BELGA.
    Examples:
      BELGA TEXT N (PLANNED)
      BELGA PICTURE (PLANNED)
      BELGA VIDEO (ON MERIT)
    """
    ct = (cov_type or "").strip().upper()
    if ct == "TEXT":
        lang = (language_code or "").strip().upper() or "N"
        return f"{COVERAGE_PREFIX} TEXT {lang} ({status})"
    return f"{COVERAGE_PREFIX} {ct} ({status})"


def get_item_location(
    event: Dict[str, Any], locale: str, is_only_city_and_country: bool = False
) -> str:
    """Set the location to be used for sorting / displaying"""
    location = event.get("location")
    if not location:
        return ""

    event_lang = event.get("language") or locale
    location_name = location[0].get("name", "")

    # find location on DB and then extract translation Name
    if location[0].get("qcode") and event_lang:
        location_data = get_resource_service("locations").find_one(
            req=None, guid=location[0].get("qcode")
        )

        if location_data:
            translated_name = (
                location_data.get("translations", {})
                .get("name", {})
                .get(f"name:{event_lang}")
            )
            location_name = translated_name or location_name

    # Build location_items based on is_only_city_and_country flag
    location_items = []
    if not is_only_city_and_country:
        address = location[0].get("address", {})
        address_lines = address.get("line") or []
        address_line = address_lines[0] if address_lines else ""

        # Check if name and address line are identical, and skip address if they are
        if location_name.lower() != address_line.lower():
            location_items.append(reorder_address(location_name))
            location_items.append(reorder_address(address_line))
        else:
            location_items.append(reorder_address(location_name))

        location_items.extend(
            [
                f'{address.get("postal_code", "")} {address.get("city") or address.get("area", "")}',
                address.get("country", ""),
            ]
        )
    else:
        location_items.extend(
            [
                location[0].get("address", {}).get("city")
                or location[0].get("address", {}).get("area"),
                location[0].get("address", {}).get("country"),
            ]
        )

    # Filter and join non-empty location items
    filtered_items = [
        item.strip() for item in location_items if item and not item.isspace()
    ]
    return ", ".join(filtered_items)


def get_language_name(item: Dict[str, Any], language: str):
    return ((item.get("translations") or {}).get("name") or {}).get(
        language
    ) or item.get("name")


def get_subjects(event: Dict[str, Any], language: str):
    subjects = event.get("subject")
    filter_subj = []
    if subjects:
        for subj in subjects:
            if subj.get("scheme") == "belga-keywords":
                filter_subj.append(get_language_name(subj, language))
        return filter_subj
    return []


def format_datetime(event: Dict[str, Any], locale: str, format: str):
    tz = event.get("dates", {}).get("tz") or app.config.get("DEFAULT_TIMEZONE")
    start_time = event.get("dates", {}).get("start")
    if not start_time:
        return ""
    try:
        return format_date(utc_to_local(tz, start_time), format, locale=locale)
    except ValueError:
        return ""


def set_metadata(formatted_event: Dict[str, Any], event: Dict[str, Any], locale: str):
    formatted_event["links"] = event.get("links", "")
    set_item_dates(formatted_event, event)
    set_event_translations_value(event, locale)
    set_item_title(formatted_event, event)
    set_item_description(formatted_event, event)


def get_formatted_contacts(event: Dict[str, Any]) -> List[FormattedContact]:
    contacts = event.get("event_contact_info", [])
    formatted_contacts: List[FormattedContact] = []

    for contact_id in contacts:
        contact_details = get_resource_service("contacts").find_one(
            req=None, _id=contact_id
        )
        if contact_details:
            formatted_contact: FormattedContact = {
                "name": " ".join(
                    [
                        c
                        for c in [
                            contact_details.get("first_name", ""),
                            contact_details.get("last_name", ""),
                        ]
                        if c
                    ]
                ),
                "organisation": contact_details.get("organisation", ""),
                "email": contact_details.get("contact_email", []),
                "phone": [
                    c.get("number", "")
                    for c in contact_details.get("contact_phone", [])
                    if c.get("public")
                ],
                "mobile": [
                    c.get("number", "")
                    for c in contact_details.get("mobile", [])
                    if c.get("public")
                ],
                "website": contact_details.get("website", ""),
                "job_title": contact_details.get("job_title", ""),
            }
            formatted_contacts.append(formatted_contact)

    return formatted_contacts


def get_coverages(event: Dict[str, Any], locale: str):
    formatted_coverages = []
    planning_ids = event.get("planning_ids", [])
    planning_service = get_resource_service("planning")
    for id in planning_ids:
        planning_item = planning_service.find_one(req=None, _id=id)
        if not planning_item:
            continue
        for coverage in planning_item.get("coverages", []):
            cov_planning = coverage.get("planning", {})
            cov_type = cov_planning.get("g2_content_type", "").upper()
            cov_status = (
                coverage.get("news_coverage_status", {}).get("label", "").upper()
            )

            if cov_planning.get("language", locale) == locale:
                formatted_coverages.append(f"{cov_type} ({cov_status})")

    return formatted_coverages


def set_event_translations_value(event: Dict[str, Any], locale: str):
    """
    set event translations value based on locale
    """
    translations = event.get("translations")
    translated_value = {}
    if translations is not None:
        translated_value.update(
            {
                entry.get("field"): entry.get("value")
                for entry in translations or []
                if entry.get("language") == locale and entry.get("field")
            }
        )
        event.update(
            {
                key: val
                for key, val in translated_value.items()
                if key
                in (
                    "description_text",
                    "name",
                    "slugline",
                    "definition_long",
                    "definition_short",
                )
            }
        )


def reorder_address(address: str) -> str:
    """
    Reorder an address string by moving the leading number (if present)
    to the end of the string.
    """
    parts = address.split(" ", 1)
    if parts[0].isdigit() and len(parts) == 2:
        return f"{parts[1]} {parts[0]}"
    return address


def format_advisory_weekday_date(d: _Union[_date_type, _datetime_type]) -> str:
    """
    Format date for Belga advisories: WEEKDAY D MONTH YYYY (no leading zero).
    """
    if isinstance(d, _datetime_type):
        d = d.date()

    weekday = d.strftime("%A").upper()
    day = d.day
    month_year = d.strftime("%B %Y").upper()

    return f"{weekday} {day} {month_year}"


def get_advisory_date_from_events(
    event_data: List[Dict[str, Any]], default_tz: str = ADVISORY_TIMEZONE
) -> str:
    """
    Determine the advisory header date from a list of events:
    - Converts event start datetimes to local dates using each event's tz (or default_tz)
    - Picks the earliest local date and returns it formatted via format_advisory_weekday_date()
    - Returns empty string if no valid dates found
    """
    if not event_data:
        return ""

    local_dates = []
    for ev in event_data:
        dates = ev.get("dates") or {}
        start = dates.get("start")
        if not start:
            continue
        tz = dates.get("tz") or default_tz
        try:
            local_dt = utc_to_local(tz, start)
        except ValueError:
            continue
        local_dates.append(local_dt.date())

    if not local_dates:
        return ""

    return format_advisory_weekday_date(min(local_dates))


def get_display_times(
    dates: Dict[str, Any], default_tz: str = ADVISORY_TIMEZONE
) -> Dict[str, str]:
    """
    Return time strings, hiding all-day and no-time events but showing real timed ranges.
    """

    if not dates:
        return {"time": "", "display_time": ""}

    tz = dates.get("tz") or default_tz
    start = dates.get("start")
    end = dates.get("end")

    if not start or not end:
        return {"time": "", "display_time": ""}

    try:
        start_local = utc_to_local(tz, start)
        end_local = utc_to_local(tz, end)
    except ValueError:
        return {"time": "", "display_time": ""}

    is_all_day = (
        start_local.hour == 0
        and start_local.minute == 0
        and end_local.hour == 23
        and end_local.minute == 59
    )
    if is_all_day:
        return {"time": "", "display_time": ""}

    if (
        start_local.hour == 0
        and start_local.minute == 0
        and not (start_local == end_local)
    ):
        return {"time": "", "display_time": ""}

    if start_local == end_local:
        single = start_local.strftime("%H:%M")
        return {"time": single, "display_time": single}

    time_range = f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')}"
    display_time = start_local.strftime("%H:%M")
    return {"time": time_range, "display_time": display_time}


def is_editorial_calendar(item):
    calendars = item.get("calendars", [])

    for cal in calendars:
        qcode = (cal.get("qcode") or "").lower()
        name = (cal.get("name") or "").lower()

        if "editorial" in qcode or "editorial" in name:
            return True

    return False


def get_advisory_weekday_date(planning_item, planning_service=None, event_service=None):
    """Get weekday/date of planning, preferring linked event date."""
    if event_service is None:
        event_service = get_resource_service("events")
    if planning_service is None:
        planning_service = get_resource_service("planning")

    event_item = None
    if planning_item.get("event_item"):
        event_item = event_service.find_one(req=None, _id=planning_item["event_item"])

    planning_item = planning_service.find_one(req=None, _id=planning_item["_id"])
    if not planning_item:
        return ""

    scheduled, _, tz = get_planning_schedule_info(planning_item, event_item)

    if scheduled:
        try:
            local_dt = utc_to_local(tz, scheduled)
        except ValueError:
            try:
                local_dt = utc_to_local(ADVISORY_TIMEZONE, scheduled)
            except ValueError:
                return ""
        return format_advisory_weekday_date(local_dt)

    return ""


def get_coverages_bilingual(item, include_assignee=False):
    """Get coverages formatted for bilingual output.

    Works for both event items (uses planning_ids field) and planning items
    (falls back to _id). If include_assignee=True, appends BY <USER/DESK>
    to the display string and includes username/desk_name in the result.
    """
    planning_service = get_resource_service("planning")
    desk_service = get_resource_service("desks")
    user_service = get_resource_service("users") if include_assignee else None
    lang_map = {"nl": "N", "n": "N", "fr": "F", "f": "F", "de": "N"}
    planning_ids = item.get("planning_ids") or [item.get("_id")]
    formatted_coverages = []
    desk_cache = {}
    user_cache = {}

    for planning_id in planning_ids:
        planning_item = planning_service.find_one(req=None, _id=planning_id)
        if not planning_item:
            continue

        for coverage in planning_item.get("coverages", []):
            if not isinstance(coverage, dict):
                continue

            planning_info = coverage.get("planning") or {}
            cov_type = (
                planning_info.get("g2_content_type")
                or coverage.get("g2_content_type")
                or ""
            ).lower()
            cov_status = (
                coverage.get("news_coverage_status", {}).get("label") or "ON MERIT"
            ).upper()

            desk_language_code = "N"
            desk_name = ""
            desk_id = (
                planning_info.get("desk")
                or coverage.get("assigned_to", {}).get("desk")
                or item.get("task", {}).get("desk")
            )
            if desk_id:
                if desk_id not in desk_cache:
                    desk_cache[desk_id] = desk_service.find_one(req=None, _id=desk_id)
                desk_item = desk_cache[desk_id]
                if desk_item:
                    desk_name = desk_item.get("name", "")
                    if desk_item.get("desk_language"):
                        desk_language_code = lang_map.get(
                            desk_item["desk_language"].lower(), "N"
                        )

            coverage_display = format_coverage_label(
                cov_type, desk_language_code, cov_status
            )

            username = ""
            if include_assignee:
                assigned_user_id = coverage.get("assigned_to", {}).get("user")
                if assigned_user_id and user_service:
                    if assigned_user_id not in user_cache:
                        user_item = user_service.find_one(
                            req=None, _id=assigned_user_id
                        )
                        user_cache[assigned_user_id] = (
                            (user_item.get("sign_off") or user_item.get("username"))
                            if user_item
                            else ""
                        )
                    username = user_cache[assigned_user_id]
                if username:
                    coverage_display = f"{coverage_display} BY {username.upper()}"
                elif desk_name:
                    coverage_display = f"{coverage_display} BY {desk_name.upper()}"

            entry = {
                "display": coverage_display,
                "type": cov_type,
                "status": cov_status,
                "language": desk_language_code,
            }
            if include_assignee:
                entry["username"] = username
                entry["desk_name"] = desk_name

            formatted_coverages.append(entry)

    return formatted_coverages


def sort_calendar_groups(calendar_groups):
    """Sort and merge calendar groups following CALENDAR_ORDER, timed events first."""
    events_list = []
    for calendar in CALENDAR_ORDER + sorted(
        [c for c in calendar_groups if c not in CALENDAR_ORDER]
    ):
        if calendar in calendar_groups:
            events_sorted = sorted(
                calendar_groups[calendar],
                key=lambda x: (x["time"] == "", x["time"]),
            )
            events_list.append({"calendar": calendar, "events": events_sorted})
    return events_list


def get_planning_schedule_info(
    planning,
    event_item=None,
    fallback_to_planning_if_event_dates_missing=True,
):
    """Get schedule info for planning exports.

    Returns a tuple: (scheduled, display_dates, tz)
    - If event_item has dates.start, event dates are used.
    - If event_item exists without dates.start, fallback behavior is configurable.
    - Otherwise, falls back to coverage scheduled / planning_date.
    """
    event_dates = (event_item or {}).get("dates") or {}

    if event_item:
        tz = event_dates.get("tz") or ADVISORY_TIMEZONE
        event_start = event_dates.get("start")
        if event_start:
            return (
                event_start,
                {
                    "start": event_start,
                    "end": event_dates.get("end") or event_start,
                    "tz": tz,
                },
                tz,
            )

        if not fallback_to_planning_if_event_dates_missing:
            return None, {"start": None, "end": None, "tz": tz}, tz

    scheduled = planning.get("planning_date")
    for coverage in planning.get("coverages", []):
        if not isinstance(coverage, dict):
            continue
        cov_scheduled = coverage.get("planning", {}).get("scheduled")
        if cov_scheduled:
            scheduled = cov_scheduled
            break

    tz = planning.get("dates", {}).get("tz") or ADVISORY_TIMEZONE
    return (
        scheduled,
        {"start": scheduled, "end": scheduled, "tz": tz},
        tz,
    )


def get_planning_display_times(planning, event_item=None):
    """Get (time, display_time) for a planning item, preferring linked event dates."""
    scheduled, display_dates, _ = get_planning_schedule_info(planning, event_item)
    if scheduled:
        times = get_display_times(display_dates, default_tz=ADVISORY_TIMEZONE)
        return times.get("time", ""), times.get("display_time", "")
    return "", ""


def format_bilingual_event_item(
    event, locale, include_assignee=False, calendar_fallback="Overig / Divers"
):
    """Format a single event item for bilingual advisory output.

    Returns the formatted dict ready to append to a calendar group.
    """
    event_nl = event.copy()
    event_fr = event.copy()
    set_event_translations_value(event_nl, "nl")
    set_event_translations_value(event_fr, "fr")

    calendar = (
        event["calendars"][0]["qcode"].capitalize()
        if event.get("calendars")
        else calendar_fallback
    )

    formatted_event = {
        "subject": ",".join(get_subjects(event, "nl")),
        "calendar": calendar,
        "contacts": get_formatted_contacts(event),
        "coverages": get_coverages_bilingual(event, include_assignee=include_assignee),
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

    set_metadata(formatted_event, event, locale)

    dates = event.get("dates", {})
    times = get_display_times(dates, default_tz=ADVISORY_TIMEZONE)
    formatted_event["time"] = times.get("time", "")
    formatted_event["display_time"] = times.get("display_time", "")

    return formatted_event
