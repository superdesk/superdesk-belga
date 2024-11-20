"""This macro adds a prefix string 'TIP' to headline and sets urgency to 5 of the item"""

from superdesk import get_resource_service


def change_headline_and_urgency(item, **kwargs):
    if "headline" in item:
        item["headline"] = "TIP " + item.get("headline", "")

    if "urgency" in item:
        item["urgency"] = 5

    content_profile = get_resource_service("content_types").find_one(
        req=None, label="TIP"
    )
    if content_profile:
        item["profile"] = content_profile.get("_id")

    return item


name = "TIPS ingest macro"
label = "TIPS ingest macro"
callback = change_headline_and_urgency
access_type = "backend"
action_type = "direct"
