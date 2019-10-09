# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

from lxml import etree

from superdesk.io.registry import register_feed_parser

from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser


class BelgaAFPNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific AFP NewsML."""

    NAME = 'belga_afp_newsml12'
    label = 'Belga specific AFP News ML 1.2 Parser'
    MAPPING_KEYWORDS = {
        'ECONOMY': ['BOURSE', 'ECONOMIE', 'CONOMIE', 'MARCHES', 'FINANCE', 'BANQUE'],
        'SPORTS': ['HIPPISME', 'SPORT', 'SPORTS']
    }
    MAPPING_CATEGORY = {
        'SPO': 'SPORT',
        'POL': 'POLITICS',
    }

    def parse(self, xml, provider=None):
        def add_unique_item_to_list(data, _list):
            if data not in _list:
                _list.append(data)

        items = super().parse(xml, provider)
        # mapping data follow xsl file
        for item in items:
            # mapping from keyword
            for keyword in item.get('keywords', []):
                keyword = keyword.strip('/').upper()
                product_code = [k if keyword in v else 'GENERAL' for k, v in self.MAPPING_KEYWORDS.items()][0]
                product = {
                    "name": product_code,
                    "qcode": product_code,
                    "scheme": "news_products"
                }
                add_unique_item_to_list(product, item.get('subject', []))
            # mapping from anpa_category
            for category in item.get('anpa_category', []):
                qcode = category.get('qcode')
                product = {
                    "name": self.MAPPING_CATEGORY.get(qcode, 'GENERAL'),
                    "qcode": self.MAPPING_CATEGORY.get(qcode, 'GENERAL'),
                    "scheme": "news_products"
                }
                add_unique_item_to_list(product, item.get('subject', []))
            # add content for headline when it is empty
            if item.get('urgency') in ('1', '2') and not item.get('headline'):
                first_line = item.get('body_html', '').strip().split('\n')[0]
                first_line = etree.fromstring(first_line).text
                headline = 'URGENT: ' + first_line.strip()
                item['headline'] = headline
        return items


register_feed_parser(BelgaAFPNewsMLOneFeedParser.NAME, BelgaAFPNewsMLOneFeedParser())
