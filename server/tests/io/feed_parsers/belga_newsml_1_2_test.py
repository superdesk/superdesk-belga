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
import pytz
import datetime
from lxml import etree
from superdesk.tests import TestCase
from belga.io.feed_parsers.belga_newsml_1_2 import BelgaNewsMLOneFeedParser


class BelgaNewsMLOneTestCase(TestCase):
    filename = 'belga_newsml_1_2.xml'

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test'}
        with open(fixture, 'rb') as f:
            parser = BelgaNewsMLOneFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaNewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]

        self.assertEqual(
            item['administrative']['foreign_id'],
            'BIN118'
        )
        self.assertEqual(
            item['administrative']['validation_date'],
            '20190129T133356'
        )
        self.assertEqual(
            item['administrative']['validator'],
            'dwm'
        )
        self.assertEquals(item['authors'], [{'name': 'DWM', 'role': 'AUTHOR'}])
        self.assertEqual(
            item['body_html'],
            '<p>Steven &lt;b&gt;Van Geel&lt;/b&gt; gaf zich op 31 mei 2014 aan bij de politie van zijn '
            'thuisstad Leuven.</p>'
            '<p> Praesent sapien massa, convallis a pellentesque nec, egestas non nisi.</p>'
        )
        self.assertEqual(item['byline'], 'BELGA')
        self.assertEqual(item['copyrightholder'], 'Belga')
        self.assertEqual(item['date_id'], '20190129T133400')
        self.assertEqual(item['extra']['city'], 'BRUSSEL')
        self.assertEqual(item['extra']['country'], 'België')
        self.assertEqual(item['firstcreated'], datetime.datetime(2019, 1, 29, 11, 45, 50, tzinfo=pytz.utc))
        self.assertEqual(item["guid"], "98055801")
        self.assertEqual(item["headline"], "Mediawatch dinsdag 29/01/2019 - VTM Nieuws - 13 uur")
        self.assertEqual(item["item_id"], "98055798")
        self.assertEqual(item["keywords"], ['ATTENTION USERS', 'PRESS', 'TV', 'MEDIA'])
        self.assertEqual(item['language'], 'nl')
        self.assertEqual(item['priority'], 3)
        self.assertEqual(item['urgency'], 3)
        self.assertEqual(item['provider_id'], 'belga.be')
        self.assertEqual(item['public_identifier'], 'urn:newsml:www.belga.be')
        self.assertEqual(item['pubstatus'], 'usable')
        self.assertEqual(item['slugline'], 'BelgaService')
        self.assertEqual(item['source'], 'BELGA')
        self.assertEqual(item['subject'], [
            {'name': 'NEWS', 'qcode': 'NEWS', 'scheme': 'news_item_types'},
            {'name': 'CURRENT', 'qcode': 'CURRENT', 'scheme': 'genre'},
            {'name': 'BIN/ALG', 'qcode': 'BIN/ALG', 'scheme': 'services-products', 'parent': 'BIN'},
            {'name': 'BIN/ECO', 'qcode': 'BIN/ECO', 'scheme': 'services-products', 'parent': 'BIN'},
            {'name': 'NEWS/CULTURE_LIFESTYLE', 'qcode': 'NEWS/CULTURE_LIFESTYLE', 'scheme': 'services-products',
             'parent': 'NEWS'},

        ])
        self.assertEqual(item['type'], 'text')
        self.assertEqual(item['version'], 4)
        self.assertEqual(item['versioncreated'], datetime.datetime(2019, 1, 29, 12, 34, tzinfo=pytz.utc))
