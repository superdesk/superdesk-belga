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
        if not country_code:
            return []

        countries = get_resource_service('vocabularies').get_items(
            _id='countries',
            qcode=country_code.lower()
        )
        return countries

    def _get_keywords(self, data):
        if not data:
            return []

        _belga_keyword_list = get_resource_service('vocabularies').get_items(
            _id='belga-keywords',
            qcode=data.upper()
        )
        return (
            _belga_keyword_list
            if len(_belga_keyword_list) > 0
            else [{"name": data, "qcode": data, "scheme": "original-metadata"}]
        )
