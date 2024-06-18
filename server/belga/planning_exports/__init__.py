from .format_news_events_week import format_event_for_week
from .format_news_events_tommorow import format_event_for_tommorow


def init_app(app):
    app.jinja_env.globals.update(format_event_for_week=format_event_for_week)
    app.jinja_env.globals.update(format_event_for_tommorow=format_event_for_tommorow)
