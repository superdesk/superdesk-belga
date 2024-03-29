"""This macro update the package if fetched item contain language is French or Dutch"""

from apps.archive.common import CONTENT_STATE
from belga.macros.set_default_metadata import set_default_metadata
import logging
from superdesk import get_resource_service

logger = logging.getLogger(__name__)


def update_package(item, **kwargs):
    item = set_default_metadata(item, **kwargs)

    language = kwargs.get("desk", {}).get("desk_language", item.get("language"))

    if item.get("state") == CONTENT_STATE.INGESTED and language in (
        "fr",
        "nl",
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
            if language == "fr"
            else {
                "name": "BTL/ECO",
                "qcode": "BTL/ECO",
                "parent": "BTL",
                "scheme": "services-products",
            }
        )

        item.setdefault("subject", []).append(data)

    macro_service = get_resource_service("macros")
    desk_routing_macro = macro_service.get_macro_by_name("desk_routing")
    desk_routing_macro["callback"](item, **kwargs)


name = "Add specific package"
label = "Add specific package"
callback = update_package
access_type = "backend"
action_type = "direct"
