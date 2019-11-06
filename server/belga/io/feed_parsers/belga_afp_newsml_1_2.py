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
import unicodedata


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

    def parser_newsitem(self, item, newsitem_el):
        super().parser_newsitem(item, newsitem_el)
        # mapping product from keyword, and have only one product
        product = {}
        for keyword in item.get('keywords', []):
            keyword = unicodedata.normalize('NFKD', keyword.strip(
                '/').upper()).encode('ascii', 'ignore').decode('utf-8')
            product_codes = [k for k, v in self.MAPPING_KEYWORDS.items() for it in v if keyword in it]
            if product_codes:
                product = {
                    "name": product_codes[0],
                    "qcode": product_codes[0],
                    "scheme": "news_products"
                }
                item.setdefault('subject', []).append(product)
                break

        # add content for headline when it is empty
        if item.get('urgency') in ('1', '2') and not item.get('headline'):
            first_line = item.get('body_html', '').strip().split('\n')[0]
            first_line = etree.fromstring(first_line).text
            headline = 'URGENT: ' + first_line.strip()
            item['headline'] = headline
        return item


register_feed_parser(BelgaAFPNewsMLOneFeedParser.NAME, BelgaAFPNewsMLOneFeedParser())
