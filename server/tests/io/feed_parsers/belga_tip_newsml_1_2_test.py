# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import os
from lxml import etree

from belga.io.feed_parsers.belga_tip_newsml_1_2 import BelgaTipNewsMLOneFeedParser
from tests import TestCase


class BelgaTipNewsMLOneTestCase(TestCase):
    filename = "belga_tip_newsml_1_2.xml"

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, "../fixtures", self.filename))
        provider = {"name": "test"}
        with open(fixture, "rb") as f:
            parser = BelgaTipNewsMLOneFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaTipNewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertEqual(item["provider_id"], "belga.be")
        self.assertEqual(item["date_id"], "20190928T074132")
        self.assertEqual(item["item_id"], None)
        self.assertEqual(item["version"], 1)
        self.assertEqual(item["public_identifier"], "urn:newsml:www.belga.be")
        self.assertEqual(
            item["subject"],
            [
                {
                    "name": "BIN/ALG",
                    "qcode": "BIN/ALG",
                    "scheme": "services-products",
                    "parent": "BIN",
                }
            ],
        )
        self.assertEqual(str(item["firstcreated"]), "2019-09-28 05:41:32+00:00")
        self.assertEqual(str(item["versioncreated"]), "2019-09-28 05:41:32+00:00")
        self.assertEqual(item["pubstatus"], "usable")
        self.assertEqual(item["guid"], "f0d56ae3bcf30abfdf064b943c52fbe5")
        self.assertEqual(item["language"], "NL")
        self.assertEqual(item["byline"], "BELGA")
        self.assertEqual(item["headline"], "cor 446 - BRAND GEBOUW, hemiksem")
        self.assertEqual(item["body_html"], "cor 446 - BRAND GEBOUW, hemiksem")
        self.assertEqual(item["copyrightholder"], "Belga")
        self.assertEqual(item["line_type"], "1")
        self.assertEqual(item["keywords"], ["SMS"])
        self.assertEqual(item["administrative"], {"provider": "belga.be"})
        self.assertEqual(item["priority"], 3)
        self.assertEqual(item["urgency"], 3)
        self.assertEqual(item["source"], "BELGA")
        self.assertEqual(item["type"], "text")
