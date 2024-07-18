from .common import set_metadata, get_subject, format_datetime, get_item_location
from typing import List, Dict, Any


def format_event_for_week(event_data: List[Dict[str, Any]], locale: str):
    events_list: List[Dict[str, Any]] = []

    sorted_events = sorted(event_data, key=lambda x: x["dates"]["start"])

    current_date = None
    for event in sorted_events:
        formatted_event = {
            "subject": ",".join(get_subject(event, locale)),
            "location": get_item_location(event, locale, True),
        }
        set_metadata(formatted_event, event, locale)

        if formatted_event["local_date_time"] != current_date:
            current_date = formatted_event["local_date_time"]
            formatted_current_date = format_datetime(event, locale, "EEEE d MMMM")
            events_list.append({"date": formatted_current_date, "subjects": {}})

        subject = formatted_event["subject"]
        if subject not in events_list[-1]["subjects"]:
            events_list[-1]["subjects"][subject] = []
        events_list[-1]["subjects"][subject].append(formatted_event)

    return {
        "events_list": events_list,
        "start_date": format_datetime(sorted_events[0], locale, "EEEE d"),
        "end_date": format_datetime(sorted_events[-1], locale, "EEEE d"),
        "month": format_datetime(sorted_events[0], locale, "MMMM"),
    }
