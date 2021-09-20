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
        'SPO': 'NEWS/SPORTS',
        'ECO': 'NEWS/ECONOMY',
    }

    # anp related logic goes here
    def parse_newsmanagement(self, item, manage_el):
        super().parse_newsmanagement(item, manage_el)
        item['firstcreated'] = item['firstcreated'].astimezone(pytz.utc)
        item['versioncreated'] = item['versioncreated'].astimezone(pytz.utc)

    def parse_newsitem(self, item, newsitem_el):
        super().parse_newsitem(item, newsitem_el)
        for genre in self._get_genre(item):
            qcode = self.MAPPING_PRODUCTS.get(genre.get('name'), 'NEWS/GENERAL')
            item.setdefault('subject', []).append({
                'name': qcode,
                'qcode': qcode,
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
        # Source is ANP
        credit = {"name": 'ANP', "qcode": 'ANP', "scheme": "sources"}
        item.setdefault('subject', []).append(credit)
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

register_feed_parser(BelgaANPNewsMLOneFeedParser.NAME, BelgaANPNewsMLOneFeedParser())
