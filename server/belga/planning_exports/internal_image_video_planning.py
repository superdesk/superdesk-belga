from .internal_belga_image_planning import (
    format_image_planning,
    format_image_planning_event_ids_json,
)


def format_internal_image_video_planning(items):
    return format_image_planning(
        planning_data=items,
        allowed_coverage_types={"video"},
        title_prefix="Belga Image Video Planning",
        group_by_calendar=False,
    )


def format_internal_image_video_planning_event_ids_json(items):
    return format_image_planning_event_ids_json(
        planning_data=items,
        allowed_coverage_types={"video"},
    )
