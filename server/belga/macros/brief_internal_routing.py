
import superdesk

from flask import current_app as app
from datetime import timedelta
from superdesk.metadata.item import CONTENT_STATE, PUBLISH_SCHEDULE, SCHEDULE_SETTINGS
from superdesk.macros.internal_destination_auto_publish import internal_destination_auto_publish
from superdesk.editor_utils import replace_text, filter_blocks
from apps.archive.common import update_schedule_settings


CREDITS = 'credits'
COUNTRY = 'country'
PRODUCTS = 'services-products'

BRIEF_CREDIT = 'BELGA/AG'
DEFAULT_PRODUCT = 'NEWS/GENERAL'
PRODUCT_MAPPING = {
    'NEWS/SPORTS': ('SPN/', 'SPF/'),
    'NEWS/POLITICS': ('/POL', ),
    'NEWS/ECONOMY': ('/ECO', ),
}


def _get_brief_profile():
    profile = superdesk.get_resource_service('content_types').find_one(req=None, label='Brief')
    if profile:
        return profile['_id']
    return None


def _find_subj(subject: list, scheme: str):
    return next((subj for subj in subject if subj.get('scheme') == scheme), None)


def _get_brief_subject(subject: list):
    if not subject:
        subject = []
    credit = _find_subj(subject, CREDITS)
    if credit and 'BELGA' not in credit.get('qcode'):
        credit['name'] = credit['qcode'] = BRIEF_CREDIT
    elif not credit:
        subject.append({
            'name': BRIEF_CREDIT,
            'qcode': BRIEF_CREDIT,
            'scheme': CREDITS,
        })
    return subject


def _get_product_subject(subject: list):
    if not subject:
        subject = []
    product = _find_subj(subject, PRODUCTS)
    if product:
        name = product.get('name') or ''
        next_value = DEFAULT_PRODUCT
        for value, items in PRODUCT_MAPPING.items():
            if any([item for item in items if item in name]):
                next_value = value
                break
        product['name'] = product['qcode'] = next_value
        if name.startswith(('BIN/', 'INT/')):
            subject = [subj for subj in subject if subj.get('scheme') != COUNTRY]
            subject.append({
                'name': 'Belgium',
                'qcode': 'country_bel',
                'scheme': COUNTRY,
            })
    return subject


def _fix_headline(item):
    for old in (' BELGANIGHT', 'BELGANIGHT ', 'BELGANIGHT'):
        replace_text(item, 'headline', old, '', is_html=False)


class BlockFilter():

    filtered = False

    def __call__(self, block):
        if not self.filtered and any([pattern in block.text for pattern in ('Disclaimer:', 'ATTENTION USERS')]):
            self.filtered = True
        return not self.filtered


def _fix_body_html(item):
    filter_blocks(item, 'body_html', BlockFilter())


def brief_internal_routing(item: dict, **kwargs):
    item.setdefault('subject', [])
    item['urgency'] = 2
    item['profile'] = _get_brief_profile()
    item['subject'] = _get_product_subject(_get_brief_subject(item.get('subject')))
    item['status'] = CONTENT_STATE.SCHEDULED
    item['operation'] = 'publish'

    _fix_headline(item)
    _fix_body_html(item)

    # schedule +30m
    item[PUBLISH_SCHEDULE] = item['versioncreated'] + timedelta(minutes=30)
    item[SCHEDULE_SETTINGS] = {'time_zone': None}
    update_schedule_settings(item, PUBLISH_SCHEDULE, item[PUBLISH_SCHEDULE])

    # publish
    internal_destination_auto_publish(item)


name = 'Brief internal routing'
label = 'Brief internal routing'
callback = brief_internal_routing
access_type = 'frontend'
action_type = 'direct'
