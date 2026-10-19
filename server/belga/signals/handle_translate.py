from apps.archive.common import validate_schedule
from superdesk.errors import SuperdeskApiError

from superdesk.metadata.item import (
    CONTENT_STATE,
    CONTENT_TYPE,
    ITEM_STATE,
    PUBLISH_SCHEDULE,
    SCHEDULE_SETTINGS,
)


def handle_duplicate(sender, item, original, operation):
    if operation == "translate":
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
