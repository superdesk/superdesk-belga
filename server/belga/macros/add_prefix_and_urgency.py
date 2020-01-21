"""This macro adds a prefix string 'TIP' to headline and urgency to 5 of the item"""


def add_prefix_and_urgency(item, **kwargs):
    """Add a prefix string TIP to headline"""

    if 'headline' in item:
        item['headline'] = 'TIP ' + item.get('headline', '')

    if 'urgency' in item:
        item['urgency'] = 5

    return item


name = 'Add prefix and urgency to macro'
label = 'Add prefix TIP to headline and set urgency to 5'
callback = add_prefix_and_urgency
access_type = 'backend'
action_type = 'direct'
