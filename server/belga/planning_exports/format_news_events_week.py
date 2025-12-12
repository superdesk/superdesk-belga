from .common import (
    set_metadata,
    get_subjects,
    format_datetime,
    get_item_location,
    get_display_times,
)
from typing import List, Dict, Any


def format_event_for_week(event_data: List[Dict[str, Any]], locale: str):
    events_list: List[Dict[str, Any]] = []

    if not event_data:
        return {
            "events_list": [],
            "start_date": "",
            "end_date": "",
            "month": "",
            "headline": "",
        }

    sorted_events = sorted(event_data, key=lambda x: x["dates"]["start"])

    current_date = None
    for event in sorted_events:
        subjects = get_subjects(event, locale)
        formatted_event = {
            "subject": subjects[0] if len(subjects) != 0 else "",
            "location": get_item_location(event, locale, True),
        }
        set_metadata(formatted_event, event, locale)

        times = get_display_times(event.get("dates", {}))
        formatted_event["local_time"] = times.get("display_time", "") or ""

        if formatted_event["local_date_time"] != current_date:
            current_date = formatted_event["local_date_time"]
            formatted_current_date = format_datetime(event, locale, "EEEE d MMMM")
            events_list.append({"date": formatted_current_date, "subjects": {}})

        subject = formatted_event["subject"]
        if subject not in events_list[-1]["subjects"]:
            events_list[-1]["subjects"][subject] = []
        events_list[-1]["subjects"][subject].append(formatted_event)

    start_date = format_datetime(sorted_events[0], locale, "EEEE d")
    end_date = format_datetime(sorted_events[-1], locale, "EEEE d")
    month = format_datetime(sorted_events[0], locale, "MMMM")

    if locale and locale.startswith("nl"):
        headline = (
            f"Internationale sportkalender van {start_date} tot {end_date} {month}"
        )
    elif locale and locale.startswith("fr"):
        headline = (
            f"Calendrier sportif international du {start_date} au {end_date} {month}"
        )
    else:
        headline = f"{start_date} - {end_date} {month}"

    return {
        "events_list": events_list,
        "start_date": start_date,
        "end_date": end_date,
        "month": month,
        "headline": headline,
    }
