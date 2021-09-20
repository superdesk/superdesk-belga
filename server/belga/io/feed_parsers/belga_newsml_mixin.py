# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import get_resource_service


class BelgaNewsMLMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._countries = []

    def _get_country(self, country_code):
        if not self._countries:
            self._countries = get_resource_service('vocabularies').find_one(req=None, _id='country').get('items', [])

        return [
            {'name': c['name'], 'qcode': c['qcode'], 'translations': c['translations'], 'scheme': 'country'}
            for c in self._countries
            if c.get('qcode') == 'country_' + country_code.lower() and c.get('is_active')
        ]

    def _get_countries(self, country_code):
        countries = get_resource_service('vocabularies').find_one(req=None, _id='countries').get('items', [])

        return [
            {'name': c['name'], 'qcode': c['qcode'], 'translations': c['translations'], 'scheme': 'countries'}
            for c in countries
            if c.get('qcode') == country_code.lower() and c.get('is_active')
        ]
