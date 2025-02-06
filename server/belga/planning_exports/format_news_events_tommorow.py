from .common import (
    set_metadata,
    get_subjects,
    get_formatted_contacts,
    get_coverages,
    get_item_location,
)
from typing import List, Dict, Any
from superdesk.utc import utc_to_local


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


def format_event_for_tommorow(
    event_data: List[Dict[str, Any]], locale: str
) -> List[Dict[str, Any]]:
    events_list: List[Dict[str, Any]] = []

    # Sort events by calendar if calendars exist
    sorted_events = sorted(
        event_data,
        key=lambda x: x["calendars"][0]["qcode"] if x.get("calendars") else "",
    )

    calendar = None
    for event in sorted_events:
        # Format event details
        formatted_event = {
            "subject": ",".join(get_subjects(event, "fr")),
            "calendars": (
                event["calendars"][0]["qcode"].capitalize()
                if event.get("calendars")
                else ""
            ),
            "contacts": get_formatted_contacts(event),
            "coverages": get_coverages(event, locale),
            "location": get_item_location(event, locale),
        }
        set_metadata(formatted_event, event, locale)

        # Format time in local timezone
        dates = formatted_event["dates"]
        start_local = utc_to_local(dates["tz"], dates["start"])
        end_local = utc_to_local(dates["tz"], dates["end"])
        formatted_event["time"] = (
            f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')}"
        )

        # Check if calendar has changed
        if formatted_event["calendars"] != calendar:
            calendar = formatted_event["calendars"]
            events_list.append({"calendar": calendar, "events": []})

        # Append formatted event to corresponding calendar group
        events_list[-1]["events"].append(formatted_event)

    # filter out events if calendar is not present in CALENDAR_ORDER
    filtered_data = [item for item in events_list if item["calendar"] in CALENDAR_ORDER]

    return sorted(filtered_data, key=lambda x: CALENDAR_ORDER.index(x["calendar"]))
