from .common import set_item_location, set_item_description, set_item_title, set_item_dates, get_sort_date, get_subject
from babel.dates import format_date


def format_event_dutch(event_data):
    events_list = []

    sorted_events = sorted(event_data, key=lambda x: x['dates']['start'])
    
    current_date = None
    for event in sorted_events:
        event_text = {
            "subject":",".join(get_subject(event, "nl")),
            "links": event.get('links', ''),
        }
        set_item_dates(event_text, event)
        set_item_title(event_text, event)
        set_item_description(event_text, event)
        set_item_location(event_text, event)
        
        if event_text["local_date_str"] != current_date:
            current_date = event_text["local_date_str"]
            formatted_current_date = format_date(
                   get_sort_date(event), "EEEE d MMMM", locale="nl"
                ).capitalize()
            events_list.append({"date": formatted_current_date, "events": []})
        events_list[-1]["events"].append(event_text)

    first_event = sorted_events[0]
    last_event = sorted_events[-1]

    intro_text = {
        "title": f"Internationale sportkalender van {first_event['dates']['end'].strftime('%A')} tot {last_event['dates']['end'].strftime('%A')} {first_event['dates']['start'].strftime('%B')}",
        "subtitle": f"De belangrijkste sportevenementen op de Belgische en internationale sportkalender van {first_event['dates']['end'].strftime('%A')} tot {last_event['dates']['end'].strftime('%A')} {first_event['dates']['start'].strftime('%B')}:",
    }

    return {
        "intro": intro_text,
        "events": events_list
    }
