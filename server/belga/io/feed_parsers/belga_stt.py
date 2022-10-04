# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.io.registry import register_feed_parser
from superdesk.io.feed_parsers.stt_newsml import STTNewsMLFeedParser


class BelgaSTTFeedParser(STTNewsMLFeedParser):
    """
    Feed Parser which can parse if the feed is in STT News Ml format.
    """

    NAME = "belga_stt_newsml"
    label = "Belga STT News ML"

    def __init__(self):
        super().__init__()
        self._provider = None

    def can_parse(self, xml):
        return xml.tag.endswith("newsItem")

    def parse(self, xml, provider=None):
        items = super().parse(xml, provider)
        for item in items:
            if item.get("abstract"):
                abstract = "<p>" + item["abstract"] + "</p>"
                item["body_html"] = abstract + item.get("body_html", "")
                item["abstract"] = ""
        return items


register_feed_parser(BelgaSTTFeedParser.NAME, BelgaSTTFeedParser())
