"""This macro adds a prefix string 'BELG' to headline of the item"""


def add_prefix_to_headline(item, **kwargs):
    """Add a prefix string to headline"""

    if "headline" in item:
        item["headline"] = "BELG " + item.get("headline", "")

    return item


name = "Add prefix BELG to headline macro"
label = "Add prefix BELG to headline"
callback = add_prefix_to_headline
access_type = "backend"
action_type = "direct"
