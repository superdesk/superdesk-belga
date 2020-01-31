# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

import re

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
        'SPO': 'NEWS/SPORTS',
        'POL': 'NEWS/POLITICS',
        'ECO': 'NEWS/ECONOMY'
    }

    def parser_newsitem(self, item, newsitem_el):
        super().parser_newsitem(item, newsitem_el)
        # mapping services-products from category, and have only one product
        for category in item.get('anpa_category', []):
            qcode = self.MAPPING_CATEGORY.get(category.get('qcode'), 'NEWS/GENERAL')
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
        # add content for headline when it is empty
        if item.get('urgency') in ('1', '2') and not item.get('headline'):
            first_line = ''
            # remove trailing whitespace in p or h2 tag and empty tag
            body = re.sub(r'(>)(\s*)(.*?)(\s*)(<)', r'\1\3\5', item.get('body_html', ''))
            body = body.replace('<p></p>', '').replace('<h2></h2>', '')
            # Get inner html of the first <p> or <h2> tag which its children is not <br> tag
            # e.g.
            #   <p><b>abc</b></p> => <b>abc</b>
            #   <p><br></p><p>empty line at beginning of the body</p> => empty line at beginning of the body
            result = re.search(r'<(?:p|h2)>(?!<br/>|<br>)(.*?)</(?:p|h2)>', body)
            if result:
                first_line = result.group(1)
            headline = 'URGENT: ' + first_line.strip()
            item['headline'] = headline
        # Label must be empty
        item['subject'] = [i for i in item['subject'] if i.get('scheme') != 'label']
        # Credits is AFP
        credit = {"name": 'AFP', "qcode": 'AFP', "scheme": "credits"}
        item.setdefault('subject', []).append(credit)

        return item


register_feed_parser(BelgaAFPNewsMLOneFeedParser.NAME, BelgaAFPNewsMLOneFeedParser())
