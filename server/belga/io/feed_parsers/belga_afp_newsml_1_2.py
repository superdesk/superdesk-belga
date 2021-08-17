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
from superdesk.text_utils import get_text
from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser
import logging
from superdesk import get_resource_service

logger = logging.getLogger(__name__)


class BelgaAFPNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific AFP NewsML."""

    NAME = 'belga_afp_newsml12'
    label = 'Belga specific AFP News ML 1.2 Parser'
    MAPPING_KEYWORDS = {
        'ECONOMY': ['BOURSE', 'ECONOMIE', 'CONOMIE', 'MARCHES', 'FINANCE', 'BANQUE'],
        'SPORTS': ['HIPPISME', 'SPORT', 'SPORTS']
    }
    MAPPING_CATEGORY = {
        'SPO': 'NEWS/SPORTS',
        'POL': 'NEWS/POLITICS',
        'ECO': 'NEWS/ECONOMY'
    }

    def parse_newsitem(self, item, newsitem_el):
        super().parse_newsitem(item, newsitem_el)
        # mapping services-products from category, and have only one product
        matching = False
        for category in item.get('anpa_category', []):
            qcode = self.MAPPING_CATEGORY.get(category.get('qcode'), 'NEWS/GENERAL')
            item.setdefault('subject', []).append({
                'name': qcode,
                'qcode': qcode,
                'parent': 'NEWS',
                'scheme': 'services-products'
            })
            matching = True
        if not matching:
            item.setdefault('subject', []).append({
                'name': 'NEWS/GENERAL',
                'qcode': 'NEWS/GENERAL',
                'parent': 'NEWS',
                'scheme': 'services-products'
            })

        # add content for headline when it is empty
        if item.get('urgency') in (1, 2) and not item.get('headline'):
            for line in get_text(item.get('body_html', ''), lf_on_block=True).split('\n'):
                if line.strip():
                    item['headline'] = 'URGENT: ' + line.strip()
                    break
        # Label must be empty
        item['subject'] = [i for i in item['subject'] if i.get('scheme') != 'label']
        # Source is AFP
        credit = {"name": 'AFP', "qcode": 'AFP', "scheme": "sources"}
        item.setdefault('subject', []).append(credit)

        if item.get('urgency') == 4:
            item['urgency'] = 3

        return item

    def parse_descriptivemetadata(self, item, descript_el):
        super().parse_descriptivemetadata(item, descript_el)

        location_el = descript_el.find('Location')
        if location_el is not None:
            for element in location_el.findall('Property'):
                # country
                if element.attrib.get('FormalName', '') == 'Country' and element.attrib.get('Value'):
                    countries = get_resource_service('vocabularies').get_items(
                        _id='countries',
                        qcode=element.attrib.get('Value').lower()
                    )
                    try:
                        item.setdefault('subject', []).append(countries[0])
                    except (StopIteration, IndexError) as e:
                        logger.error(e)

        elements = descript_el.findall('Property')
        for element in elements:
            # belga keywords
            if element.attrib.get('FormalName', '') == 'Keyword' and element.attrib.get('Value'):
                belga_keywords = get_resource_service('vocabularies').get_items(
                    _id='belga-keywords',
                    qcode=element.attrib.get('Value').upper()
                )
                try:
                    item.setdefault('subject', []).append(belga_keywords[0])
                except (StopIteration, IndexError) as e:
                    logger.error(e)


register_feed_parser(BelgaAFPNewsMLOneFeedParser.NAME, BelgaAFPNewsMLOneFeedParser())
