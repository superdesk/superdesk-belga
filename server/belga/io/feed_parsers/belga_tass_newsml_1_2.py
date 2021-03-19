# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

from pytz import utc
from superdesk.io.registry import register_feed_parser
from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser


class BelgaTASSNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific TASS NewsML."""

    NAME = 'belga_tass_newsml12'
    label = 'Belga specific TASS News ML 1.2 Parser'

    MAPPING_PRODUCTS = {
        'POLITICS': 'NEWS/POLITICS',
        'ECONOMY': 'NEWS/ECONOMY',
    }

    def can_parse(self, xml):
        # TODO clarify version
        return xml.tag == 'NewsML' and xml.get('Version', '1.2') == '1.2'

    def parse_newsmanagement(self, item, manage_el):
        super().parse_newsmanagement(item, manage_el)
        item['firstcreated'] = item['firstcreated'].replace(tzinfo=utc)
        item['versioncreated'] = item['firstcreated']

    def parse_newsitem(self, item, newsitem_el):
        super().parse_newsitem(item, newsitem_el)
        # mapping news services-products from keywords
        if item.get('keywords'):
            for keyword in item['keywords']:
                qcode = [self.MAPPING_PRODUCTS.get(k) for k in self.MAPPING_PRODUCTS if k in keyword]
                if qcode:
                    item.setdefault('subject', []).append({
                        'name': qcode[0],
                        'qcode': qcode[0],
                        'parent': 'NEWS',
                        'scheme': 'services-products'
                    })
                    break
            else:
                item.setdefault('subject', []).append({
                    'name': 'NEWS/GENERAL',
                    'qcode': 'NEWS/GENERAL',
                    'parent': 'NEWS',
                    'scheme': 'services-products'
                })
        # source is TASS
        credit = {"name": 'TASS', "qcode": 'TASS', "scheme": "sources"}
        item['subject'].append(credit)

    def parse_newscomponent(self, item, newscomponent_el):
        """
        Example:
        <NewsComponent Duid="03AE4325838900396A95" Essential="no" EquivalentsList="no">
            NewsComponent Duid="03AE4325838900396A95">
                <NewsComponent xml:lang="en">
                    <Role FormalName="Main" />
                    ....
                </NewsComponent>
            </NewsComponent>
        </NewsComponent>
        :param item:
        :param newscomponent_el:
        :return:
        """
        super().parse_newscomponent(item, newscomponent_el.find('NewsComponent/NewsComponent'))
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
