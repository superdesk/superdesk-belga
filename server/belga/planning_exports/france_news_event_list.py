from .common import set_metadata, get_sort_date, get_subject
from babel.dates import format_date
from typing import List, Dict, Any


def format_event_french(event_data: List[Dict[str, Any]]):
    events_list: List[Dict[str, Any]] = []

    sorted_events = sorted(event_data, key=lambda x: x["dates"]["start"])

    current_date = None
    for event in sorted_events:
        formatted_event = {
            "subject": ",".join(get_subject(event, "fr")),
        }
        set_metadata(formatted_event, event)
        if formatted_event["local_date_str"] != current_date:
            current_date = formatted_event["local_date_str"]
            formatted_current_date = format_date(
                get_sort_date(event), "EEEE d MMMM", locale="fr"
            ).capitalize()
            events_list.append({"date": formatted_current_date, "events": []})
        events_list[-1]["events"].append(formatted_event)

    first_event = sorted_events[0]
    last_event = sorted_events[-1]

    intro_text = {
        "title": f"Calendrier sportif international du {first_event['dates']['start'].strftime('%A %d.%m.%Y')} au {last_event['dates']['end'].strftime('%A %d.%m.%Y')} {first_event['dates']['start'].strftime('%B')}",
        "subtitle": f"Principaux événements inscrits au calendrier sportif international du {first_event['dates']['start'].strftime('%A %d.%m.%Y')} au {last_event['dates']['end'].strftime('%A %d.%m.%Y')} {first_event['dates']['start'].strftime('%B')}:",
    }
    return {"intro": intro_text, "events": events_list}
