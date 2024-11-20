from copy import deepcopy
from apps.archive.common import validate_schedule
from superdesk.errors import SuperdeskApiError

from superdesk.metadata.item import (
    CONTENT_STATE,
    CONTENT_TYPE,
    ITEM_STATE,
    PUBLISH_SCHEDULE,
    SCHEDULE_SETTINGS,
)


def is_belga_archive(item):
    return item.get("type") == CONTENT_TYPE.TEXT and item.get("extra", {}).get(
        "bcoverage"
    )


def is_video(item):
    return item.get("type") == CONTENT_TYPE.VIDEO


def handle_duplicate(sender, item, original, operation):
    if operation == "translate":
        # remove all belga-archive-360/video associations
        for k, v in deepcopy(item.get("associations", {})).items():
            if v is not None and (is_belga_archive(v) or is_video(v)):
                del item.get("associations", {})[k]

        # keep schedule settings if still valid
        if original.get(ITEM_STATE) == CONTENT_STATE.SCHEDULED and original.get(
            PUBLISH_SCHEDULE
        ):
            try:
                validate_schedule(
                    original.get(SCHEDULE_SETTINGS, {}).get(
                        "utc_{}".format(PUBLISH_SCHEDULE)
                    )
                )
                item[SCHEDULE_SETTINGS] = original[SCHEDULE_SETTINGS]
                item[PUBLISH_SCHEDULE] = original[PUBLISH_SCHEDULE]
            except (SuperdeskApiError, KeyError):
                pass
