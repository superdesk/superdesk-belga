# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

from superdesk import get_resource_service
from superdesk.io.registry import register_feed_parser

from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser


class BelgaEFENewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific EFE NewsML."""

    NAME = 'belga_efe_newsml12'
    label = 'Belga specific EFE News ML 1.2 Parser'

    # efe related logic goes here
    def parser_contentitem(self, item, content_el):
        super().parser_contentitem(item, content_el)
        categoria = content_el.find('DataContent/nitf/head/meta[@name="categoria"]')
        qcode = categoria.attrib.get('content') if categoria is not None else 'GENERAL'

        vocabularies = get_resource_service('vocabularies').find_one(req=None, _id='categories').get('items', [])
        categories = {cat['qcode']: cat['name'] for cat in vocabularies}
        item.setdefault('anpa_category', []).append({'qcode': qcode})
        item.setdefault('subject', []).append({
            'qcode': categories.get(qcode, 'GENERAL'),
            'name': categories.get(qcode, 'GENERAL'),
            'scheme': 'news_products',
        })


register_feed_parser(BelgaEFENewsMLOneFeedParser.NAME, BelgaEFENewsMLOneFeedParser())
