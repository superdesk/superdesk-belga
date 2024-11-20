import logging

from superdesk import get_resource_service


logger = logging.getLogger(__name__)


def unmark_user(sender, item, original):
    marked_for_user = item.get("marked_for_user", original.get("marked_for_user"))
    if not marked_for_user:
        logger.debug("mark for user is empty")
        return

    try:
        new_stage = item["task"]["stage"]
        desk = get_resource_service("desks").find_one(
            req=None, _id=item["task"]["desk"]
        )
        if desk["incoming_stage"] == new_stage:
            item["previous_marked_user"] = marked_for_user
            item["marked_for_user"] = None
            item["marked_for_sign_off"] = None
            logger.info("unmarked user on item %s", item["guid"])
    except KeyError as err:
        logger.error("key error %s", err)
        return
