
from superdesk import get_resource_service
from superdesk.signals import item_rewrite

TEXT = 'TEXT'
ALERT = 'ALERT'

DISTRIBUTION_ID = 'distribution'


def handle_update(sender, item, original, **kwargs):
    profile_service = get_resource_service('content_types')
    alert = profile_service.find_one(req=None, label=ALERT)
    if alert and str(item.get('profile')) == str(alert['_id']):
        text = profile_service.find_one(req=None, label=TEXT)
        if text:
            item['profile'] = text['_id']
            item['urgency'] = 3
            item.setdefault('subject', [])
            subject = [subj for subj in item['subject'] if subj.get('scheme') != DISTRIBUTION_ID]
            subject.append({
                'name': 'default',
                'qcode': 'default',
                'scheme': DISTRIBUTION_ID,
            })
            item['subject'] = subject


def init_app(app_):
    item_rewrite.connect(handle_update)
