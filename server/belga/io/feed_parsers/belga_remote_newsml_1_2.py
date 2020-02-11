# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

from .belga_newsml_1_2 import BelgaNewsMLOneFeedParser, SkipItemException
import hashlib
from xml.etree import ElementTree
from superdesk.io.registry import register_feed_parser


class BelgaRemoteNewsMLOneFeedParser(BelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific AFP NewsML."""

    NAME = 'belga_remote_newsml12'

    label = 'Belga Remote News ML 1.2 Parser'

    SUPPORTED_ASSET_TYPES = ('ALERT', 'SHORT', 'TEXT', 'BRIEF', 'ORIGINAL')

    def parser_newsitem(self, newsitem_el):
        """
        Parse Newsitem element.
        Example:
         <NewsItem xml:lang="fr">
            <Identification>
                ....
            </Identification>
            <NewsManagement>
                ....
            </NewsManagement>
            <NewsComponent>
                ....
            </NewsComponent>
          </NewsItem>
        :param newsitem_el:
        :return:
        """
        # Identification
        self._item_seed.update(
            self.parser_identification(newsitem_el.find('Identification'))
        )

        # NewsManagement
        self._item_seed.update(
            self.parser_newsmanagement(newsitem_el.find('NewsManagement'))
        )

        # NewsComponent
        news_component_1 = newsitem_el.find('NewsComponent')
        if news_component_1 is not None:
            # Genre from NewsComponent 1st level
            for element in news_component_1.findall('DescriptiveMetadata/Genre'):
                if element.get('FormalName'):
                    # genre CV
                    self._item_seed.setdefault('subject', []).append({
                        "name": element.get('FormalName'),
                        "qcode": element.get('FormalName'),
                        "scheme": "genre"
                    })

            # NewsComponent 2nd level
            # NOTE: each NewsComponent of 2nd level is a separate item with unique GUID
            for news_component_2 in news_component_1.findall('NewsComponent'):
                # create an item
                salt = hashlib.md5(ElementTree.tostring(news_component_2)).hexdigest()
                item = {**self._item_seed, 'guid': salt}

                # NewsComponent
                try:
                    self.parser_newscomponent(item, news_component_2)
                except SkipItemException:
                    continue

                # type
                self.populate_fields(item)

                self._items.append(item)


register_feed_parser(BelgaRemoteNewsMLOneFeedParser.NAME, BelgaRemoteNewsMLOneFeedParser())
