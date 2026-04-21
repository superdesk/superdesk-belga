from .common import (
    get_advisory_date_from_events,
    is_editorial_calendar,
    sort_calendar_groups,
    format_bilingual_event_item,
)
from typing import List, Dict, Any


def format_event_for_tommorow_bilingual(
    event_data: List[Dict[str, Any]], locale: str
) -> Dict[str, Any]:
    """Format events into bilingual event list for advisory output"""
    calendar_groups: Dict[str, List[Dict[str, Any]]] = {}

    # Determine weekday and date from the event
    weekday_date = get_advisory_date_from_events(event_data)

    # Process events for both languages
    for event in event_data:
        if is_editorial_calendar(event):
            continue
        formatted_event = format_bilingual_event_item(event, locale)
        calendar = formatted_event["calendar"]
        calendar_groups.setdefault(calendar, []).append(formatted_event)

    return {
        "weekday_date": weekday_date,
        "events": sort_calendar_groups(calendar_groups),
    }
