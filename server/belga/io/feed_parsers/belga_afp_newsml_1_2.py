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
from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser
from superdesk import get_resource_service


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
        def add_unique_item_to_list(data, list):
            if data not in list:
                list.append(data)

        items = super().parse(xml, provider)
        # mapping data follow xsl file
        for item in items:
            # mapping from keyword
            for keyword in item.get('keywords', []):
                product = {}
                for product_code, keywords in self.MAPPING_KEYWORDS.items():
                    if keyword.strip('/').upper() in keywords:
                        product = {
                            "name": product_code,
                            "qcode": product_code,
                            "scheme": "news_products"
                        }
                        add_unique_item_to_list(product, item.get('subject', []))
                if not product:
                    product = {
                        "name": 'GENERAL',
                        "qcode": 'GENERAL',
                        "scheme": "news_products"
                    }
                    add_unique_item_to_list(product, item.get('subject', []))
            # mapping from anpa_category
            for category in item.get('anpa_category', []):
                qcode = category.get('qcode')
                if qcode in self.MAPPING_CATEGORY:
                    product = {
                        "name": self.MAPPING_CATEGORY[qcode],
                        "qcode": self.MAPPING_CATEGORY[qcode],
                        "scheme": "news_products"
                    }
                    add_unique_item_to_list(product, item.get('subject', []))
                else:
                    product = {
                        "name": 'GENERAL',
                        "qcode": 'GENERAL',
                        "scheme": "news_products"
                    }
                    add_unique_item_to_list(product, item.get('subject', []))
        return items


register_feed_parser(BelgaAFPNewsMLOneFeedParser.NAME, BelgaAFPNewsMLOneFeedParser())
