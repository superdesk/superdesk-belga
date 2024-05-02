from .common import (
    set_metadata,
    get_subject,
    format_datetime,
    get_formatted_contacts,
    get_coverages,
)
from typing import List, Dict, Any
from superdesk.utc import utc_to_local


def format_event_for_tommorow(event_data: List[Dict[str, Any]]):
    events_list: List[Dict[str, Any]] = []

    sorted_events = sorted(
        event_data,
        key=lambda x: x["calendars"][0]["qcode"] if x.get("calendars") else "",
    )

    calendar = None
    for event in sorted_events:
        formatted_event = {
            "subject": ",".join(get_subject(event, "fr")),
            "calendars": event["calendars"][0]["name"]
            if event.get("calendars")
            else "",
            "contacts": get_formatted_contacts(event),
            "coverages": get_coverages(event),
        }
        set_metadata(formatted_event, event)
        dates = formatted_event["dates"]
        formatted_event[
            "time"
        ] = f"{utc_to_local(dates['tz'], dates['start']).strftime('%Hu%M')} - {utc_to_local(dates['tz'], dates['end']).strftime('%Hu%M')}"
        if formatted_event["calendars"] != calendar:
            calendar = formatted_event["calendars"]
            events_list.append({"calendar": calendar, "events": []})
        events_list[-1]["events"].append(formatted_event)

    return events_list
