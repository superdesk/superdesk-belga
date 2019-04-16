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
from superdesk.tests import TestCase
from belga.io.feed_parsers.belga_tass_newsml_1_2 import BelgaTASSNewsMLOneFeedParser


class BelgaTASSNewsMLOneTestCase(TestCase):
    filename = 'tass_belga.xml'

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test'}
        with open(fixture, 'rb') as f:
            parser = BelgaTASSNewsMLOneFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaTASSNewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertEqual(item["subject"], [{'name': 'FILE_MROUTER', 'qcode': 'FILE_MROUTER', 'scheme': 'news_product'},
                                           {'name': 'News', 'qcode': 'News', 'scheme': 'news_item_type'},
                                           {'name': '', 'qcode': '', 'scheme': 'essential'},
                                           {'name': '', 'qcode': '', 'scheme': 'equivalents_list'},
                                           {'name': '', 'qcode': '', 'scheme': 'essential'},
                                           {'name': '', 'qcode': '', 'scheme': 'equivalents_list'}])
        self.assertEqual(item["original_source"], "\nwww.itar-tass.com\n")
        self.assertEqual(str(item["firstcreated"]), "2019-01-21 07:27:08+00:00")
        self.assertEqual(str(item["versioncreated"]), "2019-01-21 04:27:08+00:00")
        self.assertEqual(item["pubstatus"], "usable")
        self.assertEqual(item["urgency"], 2)
        self.assertEqual(item["role"], "Main")
        self.assertEqual(item["dateline"], {'text': 'January 21'})
        self.assertEqual(item["headline"], "Kremlin has 'negative reaction' to upcoming EU sanctions")
        self.assertEqual(item["slugline"], "URGENT")
        self.assertEqual(item["language"], "en")
        self.assertEqual(item["descriptive_guid"], "16AAC34CE1C503AE4325838900396A95")
        self.assertEqual(item["extra"], {'how_present': 'Origin', 'city': 'MOSCOW'})
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["mimetype"], "text/vnd.IPTC.NITF")
        self.assertEqual(item["keywords"], ['itartassrubric_URGENT', 'URGENT'])
        self.assertEqual(item["guid"], "03AE4325838900396A95")
        expected_body = \
            (
                '\n<p>MOSCOW, January 21. /TASS/. The Kremlin does not support the EU?s decision t'
                'o introduce sanctions against Russia, namely due to the Skripal incident. "It is'
                ' negative," Kremlin Spokesman Dmitry Peskov stated, when asked to describe Russi'
                'a?s reaction to the decision.</p><p>In response to a question informing that the'
                ' EU is planning to introduce sanctions against several people, including Alexand'
                'er Petrov and Ruslan Boshirov, accused of an attempt on the life of Sergei Skrip'
                'al and his daughter, Russian presidential spokesman stressed that "they are susp'
                'ected without any basis, there has been no proof so far."</p><p>"We are all fami'
                'liar with the infamous photographs of these two citizens in the UK. But at the s'
                'ame time, there are many photos of Russian citizens in the UK, and they do not s'
                'erve as direct proof. We are not aware of any more substantive and specific proo'
                'f, which is why we have a negative reaction to such decisions," Peskov said.</p>'
                '\n'
            )
        self.assertEqual(item["body_html"], expected_body)
