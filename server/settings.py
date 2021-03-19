#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import copy
from flask import json
from pathlib import Path
from superdesk.default_settings import INSTALLED_APPS, env

ABS_PATH = str(Path(__file__).resolve().parent)

init_data = Path(ABS_PATH) / 'data'
if init_data.exists():
    INIT_DATA_PATH = init_data

INSTALLED_APPS.extend([
    'analytics',
    'apps.languages',
    'planning',
    'belga.search_providers',
    'belga.io',
    'belga.command',
    'belga.publish',
    'belga.macros',
    'belga.signals'
])

SECRET_KEY = env('SECRET_KEY', '')

DEFAULT_TIMEZONE = "Europe/Brussels"

DEFAULT_LANGUAGE = 'nl'
LANGUAGES = [
    {'language': 'nl', 'label': 'Dutch', 'source': True, 'destination': True},
    {'language': 'fr', 'label': 'French', 'source': True, 'destination': True},
    {'language': 'en', 'label': 'English', 'source': False, 'destination': False},
    {'language': 'de', 'label': 'German', 'source': False, 'destination': False},
    {'language': 'ja', 'label': 'Japanese', 'source': False, 'destination': False},
    {'language': 'es', 'label': 'Spanish', 'source': False, 'destination': False},
    {'language': 'ru', 'label': 'Russian', 'source': False, 'destination': False}
]

TIMEZONE_CODE = {
    'aus': 'America/Chicago',
    'bat': 'Asia/Manila',
    'bgl': 'Asia/Kolkata',
    'cav': 'Asia/Manila',
    'cat': 'Europe/Rome',
    'chb': 'Asia/Bangkok',
    'chd': 'America/Phoenix',
    'chm': 'America/New_York',
    'cos': 'America/Denver',
    'cpn': 'America/Chicago',
    'cri': 'America/New_York',
    'dal': 'America/Chicago',
    'dlf': 'Europe/Amsterdam',
    'drs': 'Europe/Berlin',
    'ftc': 'America/Denver',
    'gdh': 'Asia/Kolkata',
    'grn': 'Europe/Paris',
    'hlb': 'America/Los_Angeles',
    'hrt': 'America/Chicago',
    'irv': 'America/Los_Angeles',
    'ist': 'Asia/Istanbul',
    'kws': 'Asia/Tokyo',
    'lac': 'Europe/Paris',
    'lee': 'America/New_York',
    'mbf': 'America/New_York',
    'mfn': 'America/Los_Angeles',
    'nwb': 'Europe/London',
    'pav': 'Europe/Rome',
    'rlh': 'America/New_York',
    'roz': 'Europe/Rome',
    'shg': 'Asia/Shanghai',
    'sjc': 'America/Los_Angeles',
    'ssk': 'Asia/Seoul',
    'svl': 'America/Los_Angeles',
    'tai': 'Asia/Taipei',
    'ups': 'Europe/Vienna',
    'wst': 'America/Indiana/Indianapolis'
}

# Default value for Source to be set for manually created items
DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES = "Belga"

# Generating short GUID for items
GENERATE_SHORT_GUID = True

# This value gets injected into NewsML 1.2 and G2 output documents.
NEWSML_PROVIDER_ID = 'belga.be'
ORGANIZATION_NAME = env('ORGANIZATION_NAME', 'Belga')
ORGANIZATION_NAME_ABBREVIATION = env('ORGANIZATION_NAME_ABBREVIATION', 'Belga')

# publishing of associated and related items
PUBLISH_ASSOCIATED_ITEMS = True

PUBLISH_QUEUE_EXPIRY_MINUTES = 60 * 24 * 10  # 10d

# noqa
PLANNING_EXPORT_BODY_TEMPLATE = '''
{% for item in items %}
{% set pieces = [
    item.get('planning_date') | format_datetime(date_format='%H:%M'),
    item.get('slugline'),
    item.get('name'),
] %}
<h2>{{ pieces|select|join(' - ') }}</h2>
{% if item.coverages %}<p>{{ item.coverages | join(' - ') }}</p>{% endif %}
{% if item.get('description_text') or item.get('links') %}
<p>{{ item.description_text }}{% if item.get('links') %} URL: {{ item.links | join(' ') }}{% endif %}</p>
{% endif %}
{% if item.contacts %}{% for contact in item.contacts %}
<p>{{ contact.honorific }} {{ contact.first_name }} {{ contact.last_name }}{% if contact.contact_email %} - {{ contact.contact_email|join(' - ') }}{% endif %}{% if contact.contact_phone %} - {{ contact.contact_phone|selectattr('public')|join(' - ', attribute='number') }}{% endif %}</p>
{% endfor %}{% endif %}
{% if item.event and item.event.location %}
<p>{{ item.event.location|join(', ', attribute='name') }}</p>
{% endif %}
{% endfor %}
'''

PLANNING_EVENT_TEMPLATES_ENABLED = True

KEYWORDS_ADD_MISSING_ON_PUBLISH = True

ARCHIVE_AUTOCOMPLETE = True
ARCHIVE_AUTOCOMPLETE_DAYS = 5

WORKFLOW_ALLOW_MULTIPLE_UPDATES = True

CELERY_WORKER_LOG_FORMAT = '%(asctime)s %(message)s level=%(levelname)s process=%(processName)s'
CELERY_WORKER_TASK_LOG_FORMAT = '{} task=%(task_name)s task_id=%(task_id)s'.format(CELERY_WORKER_LOG_FORMAT)

with Path(__file__).parent.joinpath('picture-profile.json').open() as f:
    picture_profile = json.load(f)

video_profile = copy.deepcopy(picture_profile)
video_profile['schema']['headline']['required'] = True
video_profile['editor']['headline']['required'] = True

audio_profile = copy.deepcopy(video_profile)

graphic_profile = copy.deepcopy(picture_profile)
graphic_profile['editor'].update({
    'bcoverage': {
        'order': 5,
        'section': 'content',
    },
})
graphic_profile['schema'].update({
    'bcoverage': {
        'type': 'string',
    },
})

EDITOR = {
    'picture': picture_profile['editor'],
    'video': video_profile['editor'],
    'audio': audio_profile['editor'],
    'graphic': graphic_profile['editor'],
}
SCHEMA = {
    'picture': picture_profile['schema'],
    'video': video_profile['schema'],
    'audio': audio_profile['schema'],
    'graphic': graphic_profile['schema'],
}

SCHEMA_UPDATE = {
    'archive': {
        'extra': {
            'type': 'dict',
            'schema': {},
            'mapping': {
                'type': 'object',
                'properties': {
                    'DueBy': {
                        'type': 'date',
                        'format': 'strict_date_optional_time'
                    },
                    'belga-url': {
                        'properties': {
                            'description': {
                                'type': 'string'
                            },
                            'guid': {
                                'type': 'string'
                            },
                            'id': {
                                'type': 'string'
                            },
                            'url': {
                                'type': 'string'
                            }
                        }
                    },
                    'city': {
                        'type': 'string'
                    }
                }
            },
            'allow_unknown': True,
        }
    }
}

VALIDATOR_MEDIA_METADATA = {}
ALLOW_UPDATING_SCHEDULED_ITEMS = True

GRAMMALECTE_CONFIG = {
    # disable typographic apostrophes (SDBELGA-326)
    "apos": False,
    # disable typographic quotation marks (SDBELGA-326)
    "ignore_rules": {
        "typo_guillemets_typographiques_doubles_ouvrants",
        "typo_guillemets_typographiques_doubles_fermants",
    },
}

# Suffix used in belga URN schema generation for Belga NewsMl output
# SDBELGA-355
OUTPUT_BELGA_URN_SUFFIX = env('OUTPUT_BELGA_URN_SUFFIX', 'dev')

GOOGLE_LOGIN = False
