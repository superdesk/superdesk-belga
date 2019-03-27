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


class BelgaEFENewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific EFE NewsML."""

    NAME = 'belga_efe_newsml12'
    label = 'Belga specific EFE News ML 1.2 Parser'

    # efe related logic goes here


register_feed_parser(BelgaEFENewsMLOneFeedParser.NAME, BelgaEFENewsMLOneFeedParser())
