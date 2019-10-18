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


class BelgaKyodoNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific Kyodo NewsML."""

    NAME = 'belga_kyodo_newsml12'
    label = 'Belga specific Kyodo News ML 1.2 Parser'

    def can_parse(self, xml):
        return xml.tag == 'NewsML'


register_feed_parser(BelgaKyodoNewsMLOneFeedParser.NAME, BelgaKyodoNewsMLOneFeedParser())
