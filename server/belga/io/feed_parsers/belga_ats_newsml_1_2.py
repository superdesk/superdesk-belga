# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

import logging
import pytz

from superdesk.io.registry import register_feed_parser
from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser

logger = logging.getLogger(__name__)


class BelgaATSNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser which can parse specific Belga News ML xml files."""

    NAME = "belga_ats_newsml12"

    label = "Belga specific ATS News ML 1.2 Parser"

    SUPPORTED_ASSET_TYPES = ("ALERT", "SHORT", "TEXT", "BRIEF")

    def can_parse(self, xml):
        """
        Check NewsML type for file.

        :param xml:
        :return:
        """
        return xml.tag == "NewsML"

    def parse_newsmanagement(self, item, manage_el):
        super().parse_newsmanagement(item, manage_el)
        item["firstcreated"] = item["firstcreated"].astimezone(pytz.utc)
        item["versioncreated"] = item["versioncreated"].astimezone(pytz.utc)

        if item.get("pubstatus") == "embargoed":
            item["pubstatus"] = "usable"

        # Source is ATS
        credit = {"name": "ATS", "qcode": "ATS", "scheme": "sources"}
        item.setdefault("subject", []).append(credit)

    def parse_contentitem(self, item, content_el):
        if content_el is None:
            return

        super().parse_contentitem(item, content_el)
        element = content_el.find("Comment")
        if element is not None and element.get("FormalName") == "Editorial Note":
            item["ednote"] = element.text

    def parse_newscomponent(self, item, newscomponent_el):
        """
        Parse NewsComponent in NewsItem element.

        Example:

        <NewsComponent>
          <NewsLines>
              <DateLine xml:lang="fr">Paris, 9 déc 2018 (AFP) -</DateLine>
            <HeadLine xml:lang="fr">Un an après, les fans de Johnny lui rendent hommage à Paris</HeadLine>
            <NewsLine>
              <NewsLineType FormalName="ProductLine"/>
              <NewsLineText xml:lang="fr">(Photo+Live Video+Video)</NewsLineText>
            </NewsLine>
          </NewsLines>
          <AdministrativeMetadata>
            <Provider>
              <Party FormalName="AFP"/>
            </Provider>
          </AdministrativeMetadata>
          <DescriptiveMetadata>
            ....
          </DescriptiveMetadata>
          <NewsComponent>
            <ContentItem>
                ....
            </ContentItem>
          </NewsComponent>
        </NewsComponent>

        :param item:
        :param component_el:
        :return:
        """
        super().parse_newscomponent(item, newscomponent_el)
        second_newscomponent_el = newscomponent_el.find("NewsComponent")
        if second_newscomponent_el is not None:
            content_el = second_newscomponent_el.find("ContentItem")
            if content_el is not None:
                self.parse_contentitem(item, content_el)
        return item


register_feed_parser(BelgaATSNewsMLOneFeedParser.NAME, BelgaATSNewsMLOneFeedParser())
