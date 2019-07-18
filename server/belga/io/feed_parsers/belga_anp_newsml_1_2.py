# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

from superdesk.io.registry import register_feed_parser
from superdesk import get_resource_service
from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser
import pytz


class BelgaANPNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific ANP NewsML."""

    NAME = 'belga_anp_newsml12'
    label = 'Belga specific ANP News ML 1.2 Parser'

    # anp related logic goes here
    def parser_newsmanagement(self, item, manage_el):
        super().parser_newsmanagement(item, manage_el)
        item['firstcreated'] = item['firstcreated'].astimezone(pytz.utc)
        item['versioncreated'] = item['versioncreated'].astimezone(pytz.utc)

    def parse(self, xml, provider=None):
        items = super().parse(xml, provider)
        vocabularies = get_resource_service('vocabularies').find_one(req=None, _id='categories').get('items', [])
        categories = {cat['qcode']: cat['name'] for cat in vocabularies}
        for item in items:
            news_products = []
            for subject in item['subject']:
                if subject.get('scheme', '') == 'genre':
                    qcode = subject.get('name')
                    category = categories.get(qcode, 'GENERAL')
                    item.setdefault('anpa_category', []).append({'qcode': qcode})
                    news_products.append({
                        'name': category,
                        'qcode': category,
                        'scheme': 'news_products',
                    })
            item['subject'].extend(news_products)
        return items


register_feed_parser(BelgaANPNewsMLOneFeedParser.NAME, BelgaANPNewsMLOneFeedParser())
