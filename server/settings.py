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
    'belga.image',
    'belga.io',
    'belga.command',
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

# This value gets injected into NewsML 1.2 and G2 output documents.
NEWSML_PROVIDER_ID = 'belga.be'
ORGANIZATION_NAME = env('ORGANIZATION_NAME', 'Belga')
ORGANIZATION_NAME_ABBREVIATION = env('ORGANIZATION_NAME_ABBREVIATION', 'Belga')

PUBLISH_QUEUE_EXPIRY_MINUTES = 60 * 24 * 30  # 30d

# schema for images, video, audio
SCHEMA = {
    'picture': {
        'keywords': {'required': False},
        'ednote': {'required': False},
        'headline': {'required': False},
        'description_text': {'required': True},
        'byline': {'required': False},
        'copyrightnotice': {'required': False},
        'sign_off': {'required': False},
    },
    'video': {
        'keywords': {'required': False},
        'ednote': {'required': False},
        'headline': {'required': False},
        'description_text': {'required': True},
        'byline': {'required': False},
        'copyrightnotice': {'required': False},
        'sign_off': {'required': False},
    },
    'audio': {
        'keywords': {'required': False},
        'ednote': {'required': False},
        'headline': {'required': False},
        'description_text': {'required': True},
        'byline': {'required': False},
        'copyrightnotice': {'required': False},
        'sign_off': {'required': False},
    },
}

# editor for images, video, audio
EDITOR = {
    'picture': {
        'keywords': {'order': 1, 'sdWidth': 'full'},
        'ednote': {'order': 2, 'sdWidth': 'full'},
        'headline': {'order': 3, 'sdWidth': 'full'},
        'description_text': {'order': 4, 'sdWidth': 'full'},
        'byline': {'order': 5, 'sdWidth': 'half'},
        'copyrightnotice': {'order': 6, 'sdWidth': 'half'},
        'sign_off': {'order': 7, 'sdWidth': 'half'},
    },
    'video': {
        'keywords': {'order': 1, 'sdWidth': 'full'},
        'ednote': {'order': 2, 'sdWidth': 'full'},
        'headline': {'order': 3, 'sdWidth': 'full'},
        'description_text': {'order': 4, 'sdWidth': 'full'},
        'byline': {'order': 5, 'sdWidth': 'half'},
        'copyrightnotice': {'order': 6, 'sdWidth': 'half'},
        'sign_off': {'order': 7, 'sdWidth': 'half'},
    },
    'audio': {
        'keywords': {'order': 1, 'sdWidth': 'full'},
        'ednote': {'order': 2, 'sdWidth': 'full'},
        'headline': {'order': 3, 'sdWidth': 'full'},
        'description_text': {'order': 4, 'sdWidth': 'full'},
        'byline': {'order': 5, 'sdWidth': 'half'},
        'copyrightnotice': {'order': 6, 'sdWidth': 'half'},
        'sign_off': {'order': 7, 'sdWidth': 'half'},
    },
}

# media required fields for upload
VALIDATOR_MEDIA_METADATA = {
    "headline": {
        "required": False,
    },
    "description_text": {
        "required": True,
    },
    "byline": {
        "required": False,
    },
    "copyrightnotice": {
        "required": False,
    },
}
