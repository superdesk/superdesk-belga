import logging
from typing import Dict
from datetime import timedelta

import superdesk
from superdesk.utc import utcnow, utc_to_local
from superdesk.metadata.item import (
    PUBLISH_SCHEDULE,
    SCHEDULE_SETTINGS,
    CONTENT_STATE,
    GUID_FIELD,
)
from apps.archive.common import update_schedule_settings
from apps.publish.content.common import ITEM_PUBLISH


logger = logging.getLogger(__name__)


def autopublish_in_30_sec(item: Dict, **kwargs) -> Dict:
    guid = item.get(GUID_FIELD)
    logger.info("macro started item=%s", guid)
    item[SCHEDULE_SETTINGS] = {"time_zone": superdesk.app.config["DEFAULT_TIMEZONE"]}
    item[PUBLISH_SCHEDULE] = utc_to_local(
        superdesk.app.config["DEFAULT_TIMEZONE"], utcnow() + timedelta(seconds=30)
    )
    update_schedule_settings(item, PUBLISH_SCHEDULE, item[PUBLISH_SCHEDULE])
    item[PUBLISH_SCHEDULE] = item[PUBLISH_SCHEDULE].replace(tzinfo=None)
    item["operation"] = ITEM_PUBLISH
    item["status"] = item["state"] = CONTENT_STATE.SCHEDULED

    return item


name = "Autopublish in 30 seconds"
label = name
callback = autopublish_in_30_sec
access_type = "backend"
action_type = "direct"
