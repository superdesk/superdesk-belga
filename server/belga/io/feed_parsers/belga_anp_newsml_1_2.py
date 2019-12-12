# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

import pytz

from superdesk.io.registry import register_feed_parser

from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser


class BelgaANPNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific ANP NewsML."""

    NAME = 'belga_anp_newsml12'
    label = 'Belga specific ANP News ML 1.2 Parser'

    MAPPING_PRODUCTS = {
        'SPO': 'SPORTS',
        'ECO': 'ECONOMY',
    }

    # anp related logic goes here
    def parser_newsmanagement(self, item, manage_el):
        super().parser_newsmanagement(item, manage_el)
        item['firstcreated'] = item['firstcreated'].astimezone(pytz.utc)
        item['versioncreated'] = item['versioncreated'].astimezone(pytz.utc)

    def parser_newsitem(self, item, newsitem_el):
        super().parser_newsitem(item, newsitem_el)
        product = {}
        for subject in item.get('subject', []):
            if subject.get('scheme', '') == 'genre':
                qcode = self.MAPPING_PRODUCTS.get(subject.get('name'))
                product = {'name': qcode, 'qcode': qcode, 'scheme': 'news_products'} if qcode else None
                item.setdefault('subject', []).append(product)
                break
        # Credits is ANP
        credit = {"name": 'ANP', "qcode": 'ANP', "scheme": "credits"}
        item.setdefault('subject', []).append(credit)
        item['slugline'] = ''
        return item


register_feed_parser(BelgaANPNewsMLOneFeedParser.NAME, BelgaANPNewsMLOneFeedParser())
