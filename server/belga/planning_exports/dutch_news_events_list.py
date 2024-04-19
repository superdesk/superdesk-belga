from .common import set_metadata, get_sort_date, get_subject, format_datetime
from babel.dates import format_date
from typing import List, Dict, Any


def format_event_dutch(event_data: List[Dict[str, Any]]):
    events_list: List[Dict[str, Any]] = []

    sorted_events = sorted(event_data, key=lambda x: x["dates"]["start"])

    current_date = None
    for event in sorted_events:
        formatted_event = {
            "subject": ",".join(get_subject(event, "nl")),
        }
        set_metadata(formatted_event, event)

        if formatted_event["local_date_str"] != current_date:
            current_date = formatted_event["local_date_str"]
            formatted_current_date = format_datetime(
                get_sort_date(event), "nl", "EEEE d MMMM"
            )
            events_list.append({"date": formatted_current_date, "events": []})
        events_list[-1]["events"].append(formatted_event)

    return {
        "events_list": events_list,
        "start_date": format_datetime(sorted_events[0], "nl", "EEEE d"),
        "end_date": format_datetime(sorted_events[-1], "nl", "EEEE d"),
        "month": format_datetime(sorted_events[0], "nl", "MMMM"),
    }
