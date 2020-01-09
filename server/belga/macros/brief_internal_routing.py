
import superdesk

from flask import current_app as app
from datetime import timedelta
from superdesk.metadata.item import CONTENT_STATE, PUBLISH_SCHEDULE, SCHEDULE_SETTINGS
from superdesk.macros.internal_destination_auto_publish import internal_destination_auto_publish
from apps.archive.common import update_schedule_settings


CREDITS = 'credits'
BRIEF_CREDIT = 'BELGA/AG'


def _get_brief_profile():
    profile = superdesk.get_resource_service('content_types').find_one(req=None, label='Brief')
    if profile:
        return profile['_id']


def _get_brief_subject(item):
    subject = item.get('subject') or []
    try:
        credit = next((subj for subj in subject if subj.get('scheme') == CREDITS))
        if 'BELGA' not in credit.get('qcode'):
            credit['name'] = credit['qcode'] = BRIEF_CREDIT
    except StopIteration:
        subject.append({
            'name': BRIEF_CREDIT,
            'qcode': BRIEF_CREDIT,
            'scheme': CREDITS,
        })
    return subject


def brief_internal_routing(item, **kwargs):
    item['urgency'] = 2
    item['profile'] = _get_brief_profile()
    item['subject'] = _get_brief_subject(item)
    item['status'] = CONTENT_STATE.SCHEDULED
    item['operation'] = 'publish'

    # schedule +30m
    item[PUBLISH_SCHEDULE] = item['versioncreated'] + timedelta(minutes=30)
    item[SCHEDULE_SETTINGS] = {'time_zone': None}
    update_schedule_settings(item, PUBLISH_SCHEDULE, item[PUBLISH_SCHEDULE])

    # publish
    internal_destination_auto_publish(item)


name = 'Brief internal routing'
label = 'Brief internal routing'
callback = brief_internal_routing
access_type = 'backend'
action_type = 'direct'
