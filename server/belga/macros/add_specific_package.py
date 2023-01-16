"""This macro update the package if fetched item contain language is French or Dutch"""

from apps.archive.common import CONTENT_STATE
from belga.macros.set_default_metadata import set_default_metadata
import logging

logger = logging.getLogger(__name__)


def update_package(item, **kwargs):

    item = set_default_metadata(item, **kwargs)

    if item.get("state") == CONTENT_STATE.FETCHED and item.get("language") in (
        "fr",
        "de",
    ):
        subject = item.get("subject")
        for i in subject:
            if i.get("scheme") == "services-products":
                subject.remove(i)

        data = (
            {
                "name": "EXT/ECO",
                "qcode": "EXT/ECO",
                "parent": "EXT",
                "scheme": "services-products",
            }
            if item["language"] == "fr"
            else {
                "name": "BTL/ECO",
                "qcode": "BTL/ECO",
                "parent": "BTL",
                "scheme": "services-products",
            }
        )

        item.setdefault("subject", []).append(data)

    return item


name = "Add specific package"
label = "Add specific package"
callback = update_package
access_type = "frontend"
action_type = "direct"
