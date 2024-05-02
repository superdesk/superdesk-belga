from .france_news_event_list import format_event_french
from .dutch_news_events_list import format_event_dutch
from .format_news_events_tommorow import format_event_for_tommorow


def init_app(app):
    app.jinja_env.globals.update(
        format_event_french=format_event_french
    )
    app.jinja_env.globals.update(
        format_event_dutch=format_event_dutch
    )
    app.jinja_env.globals.update(
        format_event_for_tommorow=format_event_for_tommorow
    )
