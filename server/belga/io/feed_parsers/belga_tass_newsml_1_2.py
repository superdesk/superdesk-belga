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
from superdesk.utc import local_to_utc


class BelgaTASSNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific TASS NewsML."""

    NAME = 'belga_tass_newsml12'
    label = 'Belga specific TASS News ML 1.2 Parser'

    MAPPING_PRODUCTS = {
        'POLITICS': 'POLITICS',
        'ECONOMY': 'ECONOMY',
    }

    def can_parse(self, xml):
        # TODO clarify version
        return xml.tag == 'NewsML' and xml.get('Version', '1.2') == '1.2'

    def parser_newsmanagement(self, item, manage_el):
        super().parser_newsmanagement(item, manage_el)
        tz = 'Europe/Moscow'
        item['firstcreated'] = local_to_utc(tz, item['firstcreated'])
        item['versioncreated'] = local_to_utc(tz, item['firstcreated'])

    def parser_newsitem(self, item, newsitem_el):
        super().parser_newsitem(item, newsitem_el)
        # mapping news products from keywords
        product = {}
        if item.get('keywords'):
            for keyword in item['keywords']:
                qcode = self.MAPPING_PRODUCTS.get(keyword)
                if qcode:
                    product = {
                        'name': qcode,
                        'qcode': qcode,
                        'scheme': 'news_products',
                    }
                    break
        if not product:
            product = {'name': 'GENERAL', 'qcode': 'GENERAL', 'scheme': 'news_products'}
        item.setdefault('subject', []).append(product)
        # service is always equal NEWS
        service = {"name": 'NEWS', "qcode": 'NEWS', "scheme": "news_services"}
        item.setdefault('subject', []).append(service)

    def parser_newscomponent(self, item, newscomponent_el):
        """
        Example:
        <NewsComponent Duid="03AE4325838900396A95" Essential="no" EquivalentsList="no">
            NewsComponent Duid="03AE4325838900396A95">
                <NewsComponent xml:lang="en"><Role FormalName="Main" />
                    ....
                </NewsComponent>
            </NewsComponent>
        </NewsComponent>
        :param item:
        :param newscomponent_el:
        :return:
        """
        third_newscomponent_el = newscomponent_el.find('NewsComponent/NewsComponent')
        if third_newscomponent_el is not None:
            super().parser_newscomponent(item, third_newscomponent_el)
        if newscomponent_el.attrib.get('Duid') is not None:
            item['guid'] = newscomponent_el.attrib.get('Duid', '')
        # Essential is CV
        essential = newscomponent_el.attrib.get('Essential')
        if essential:
            item.setdefault('subject', []).append({
                "name": essential,
                "qcode": essential,
                "scheme": "essential"
            })

        # EquivalentsList is CV
        equivalents_list = newscomponent_el.attrib.get('EquivalentsList')
        if equivalents_list:
            item.setdefault('subject', []).append({
                "name": equivalents_list,
                "qcode": equivalents_list,
                "scheme": "equivalents_list"
            })


register_feed_parser(BelgaTASSNewsMLOneFeedParser.NAME, BelgaTASSNewsMLOneFeedParser())
