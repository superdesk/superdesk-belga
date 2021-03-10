# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
import logging
from superdesk import get_resource_service


logger = logging.getLogger(__name__)
SUBJECT_SCHEMES = ('services-products', 'distribution')


def get_default_content_template(item, **kwargs):
    if 'dest_desk_id' in kwargs:
        desk = None
        desk_id = kwargs['dest_desk_id']
    elif 'desk' in kwargs:
        desk = kwargs['desk']
        desk_id = kwargs['desk']['_id']
    elif 'task' in item and 'desk' in item['task']:
        desk = None
        desk_id = item['task'].get('desk')
    else:
        logger.warning("Can't set default data, no desk identifier found")
        return

    if desk is None:
        desk = get_resource_service('desks').find_one(req=None, _id=desk_id)
    if not desk:
        logger.warning('Can\'t find desk with id "{desk_id}"'.format(desk_id=desk_id))
        return

    content_template_id = desk.get("default_content_template")
    if not content_template_id:
        logger.warning("No default content template set for {desk_name}".format(
            desk_name=desk.get('name', desk_id)))
        return
    content_template = get_resource_service("content_templates").find_one(req=None, _id=content_template_id)
    if not content_template:
        logger.warning('Can\'t find content_template with id "{content_template_id}"'.format(
            content_template_id=content_template_id))
        return

    return content_template


def set_default_metadata(item, **kwargs):
    """Replace some metadata from default content template

    The following metadata: ``Packages (services-products)``, ``News Services``, ``News
    Products``, ``Language``, ``Distribution``, and ``Storytags (keywords)`` will be
    replaced (or created if they don't already exist) by the value set in desk's default
    content template
    """
    content_template = get_default_content_template(item, **kwargs)
    if not content_template:
        return

    data = content_template['data']

    item['language'] = data.get('language')

    if kwargs.get('overwrite_keywords', True):
        item['keywords'] = data.get('keywords')

    # subject contains remaining metadata to copy
    subject = item.setdefault('subject', [])

    # we first remove conflicting metadata, if any
    to_delete = []
    for s in subject:
        if s.get('scheme') in SUBJECT_SCHEMES:
            to_delete.append(s)
    for s in to_delete:
        subject.remove(s)

    # and now we add the new one
    subject.extend([i for i in data.get('subject', []) if i.get('scheme') in SUBJECT_SCHEMES])

    return item


name = 'Set Default Metadata'
label = name
callback = set_default_metadata
access_type = 'backend'
action_type = 'direct'
