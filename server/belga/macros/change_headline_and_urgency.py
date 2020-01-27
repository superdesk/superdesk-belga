"""This macro adds a prefix string 'TIPS ingest macro' to headline and sets urgency to 5 of the item"""


def change_headline_and_urgency(item, **kwargs):
    if 'headline' in item:
        item['headline'] = 'TIPS ingest macro ' + item.get('headline', '')

    if 'urgency' in item:
        item['urgency'] = 5

    return item


name = 'Change Headline and Urgency Macro'
label = 'Add prefix TIPS ingest macro to headline and set urgency to 5'
callback = change_headline_and_urgency
access_type = 'backend'
action_type = 'direct'
