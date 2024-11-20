import logging

logger = logging.getLogger(__name__)


def callback(item, **kwargs):
    if item.get("marked_for_user"):
        orig = item.copy()
        item["previous_marked_user"] = item["marked_for_user"]
        item["marked_for_user"] = None
        item["marked_for_sign_off"] = None
        logger.info("unset marked for user for item %s", item["guid"])
    return item


action_type = "direct"
access_type = "backend"
name = "unmark_from_user"
label = "Unmark from User"
