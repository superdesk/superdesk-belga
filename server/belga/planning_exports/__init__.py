from .france_news_event_list import format_event_french
from .dutch_news_events_list import format_event_dutch


def init_app(app):
    app.jinja_env.globals.update(
        format_event_french=format_event_french
    )
    app.jinja_env.globals.update(
        format_event_dutch=format_event_dutch
    )
