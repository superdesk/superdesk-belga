from .internal_belga_image_planning import (
    format_image_planning,
    format_image_planning_event_ids_json,
)


def format_internal_image_photo_planning(items):
    return format_image_planning(
        planning_data=items,
        allowed_coverage_types={"picture"},
        title_prefix="Belga Image Photo Planning",
        group_by_calendar=True,
        sports_first=True,
    )


def format_internal_image_photo_planning_event_ids_json(items):
    return format_image_planning_event_ids_json(
        planning_data=items,
        allowed_coverage_types={"picture"},
    )
