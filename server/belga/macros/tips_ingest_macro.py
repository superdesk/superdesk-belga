"""This macro adds a prefix string 'TIP' to headline and sets urgency to 5 of the item"""


def change_headline_and_urgency(item, **kwargs):
    if 'headline' in item:
        item['headline'] = 'TIP ' + item.get('headline', '')

    if 'urgency' in item:
        item['urgency'] = 5

    return item


name = 'TIPS ingest macro'
label = 'TIPS ingest macro'
callback = change_headline_and_urgency
access_type = 'backend'
action_type = 'direct'
