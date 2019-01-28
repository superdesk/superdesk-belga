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
    'belga.io'
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

# This value gets injected into NewsML 1.2 and G2 output documents.
NEWSML_PROVIDER_ID = 'belga.be'
ORGANIZATION_NAME = env('ORGANIZATION_NAME', 'Belga')
ORGANIZATION_NAME_ABBREVIATION = env('ORGANIZATION_NAME_ABBREVIATION', 'Belga')

PUBLISH_QUEUE_EXPIRY_MINUTES = 60 * 24 * 30  # 30d
