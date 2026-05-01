from .format_news_events_week import format_event_for_week
from .format_news_events_tommorow import format_event_for_tommorow
from .format_planning_for_tomorrow import format_planning_for_tomorrow
from .format_planning_for_tomorrow_bilingual import (
    format_planning_for_tomorrow_bilingual,
)
from .format_news_events_tommorow_bilingual import (
    format_event_for_tommorow_bilingual,
)
from .internal_bilingual_events_advisory_tomorrow import (
    format_event_for_tommorow_bilingual_internal,
)

from .internal_bilingual_planning_advisory_tomorrow import (
    format_planning_for_tomorrow_bilingual_internal,
    format_planning_for_tomorrow_bilingual_internal_event_ids_json,
)

from .internal_image_photo_planning import (
    format_internal_image_photo_planning,
    format_internal_image_photo_planning_event_ids_json,
)
from .internal_image_video_planning import (
    format_internal_image_video_planning,
    format_internal_image_video_planning_event_ids_json,
)


def init_app(app):
    app.jinja_env.globals.update(format_event_for_week=format_event_for_week)
    app.jinja_env.globals.update(format_event_for_tommorow=format_event_for_tommorow)
    app.jinja_env.globals.update(
        format_planning_for_tomorrow=format_planning_for_tomorrow
    )
    app.jinja_env.globals.update(
        format_planning_for_tomorrow_bilingual=format_planning_for_tomorrow_bilingual
    )
    app.jinja_env.globals.update(
        format_event_for_tommorow_bilingual=format_event_for_tommorow_bilingual
    )
    app.jinja_env.globals.update(
        format_event_for_tommorow_bilingual_internal=format_event_for_tommorow_bilingual_internal
    )

    app.jinja_env.globals.update(
        format_planning_for_tomorrow_bilingual_internal=format_planning_for_tomorrow_bilingual_internal
    )
    app.jinja_env.globals.update(
        format_planning_for_tomorrow_bilingual_internal_event_ids_json=format_planning_for_tomorrow_bilingual_internal_event_ids_json
    )
    app.jinja_env.globals.update(
        format_internal_image_photo_planning=format_internal_image_photo_planning
    )
    app.jinja_env.globals.update(
        format_internal_image_video_planning=format_internal_image_video_planning
    )
    app.jinja_env.globals.update(
        format_internal_image_photo_planning_event_ids_json=format_internal_image_photo_planning_event_ids_json
    )
    app.jinja_env.globals.update(
        format_internal_image_video_planning_event_ids_json=format_internal_image_video_planning_event_ids_json
    )
