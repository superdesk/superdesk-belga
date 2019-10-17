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
    filename_belga_remote = 'belga_remote_newsml_1_2.xml'

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test'}
        parser = BelgaNewsMLOneFeedParser()
        with open(fixture, 'rb') as f:
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)
        # belga remote
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename_belga_remote))
        with open(fixture, 'rb') as f:
            self.xml_root_belga_remote = etree.parse(f).getroot()
            self.item_belga_remote = parser.parse(self.xml_root_belga_remote, provider)

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
            {'name': 'BIN', 'qcode': 'BIN', 'scheme': 'news_services'},
            {'name': 'ALG', 'qcode': 'ALG', 'scheme': 'news_products'},
            {'name': 'INT', 'qcode': 'INT', 'scheme': 'news_services'},
            {'name': 'GEN', 'qcode': 'GEN', 'scheme': 'news_products'}
        ])
        self.assertEqual(item['type'], 'text')
        self.assertEqual(item['version'], 4)
        self.assertEqual(item['versioncreated'], datetime.datetime(2019, 1, 29, 12, 34, tzinfo=pytz.utc))

    def test_content_belga_remote(self):
        item = self.item_belga_remote[0]
        self.assertEqual(item["provider_id"], "belga.be")
        self.assertEqual(item["date_id"], "20190603T160217")
        self.assertEqual(item["item_id"], "0")
        self.assertEqual(item["version"], 0)
        self.assertEqual(item["public_identifier"], "urn:newsml:www.belga.be")
        self.assertEqual(item["subject"], [{'name': 'NEWS', 'qcode': 'NEWS', 'scheme': 'news_item_types'}, {'name': 'BIN', 'qcode': 'BIN', 'scheme': 'news_services'}, {
                         'name': 'ALG', 'qcode': 'ALG', 'scheme': 'news_products'}, {'name': 'S1', 'qcode': 'S1', 'scheme': 'label'}])
        self.assertEqual(str(item["firstcreated"]), "2019-06-03 14:02:17+00:00")
        self.assertEqual(str(item["versioncreated"]), "2019-06-03 14:02:17+00:00")
        self.assertEqual(item["pubstatus"], "usable")
        self.assertEqual(item["guid"], "0")
        self.assertEqual(item["language"], "nl")
        self.assertEqual(item["byline"], "BELGA")
        self.assertEqual(item["headline"], "Knooppunt Schijnpoort in Antwerpen hele zomervakantie afgesloten")
        self.assertEqual(item["copyrightholder"], "Belga")
        self.assertEqual(item["line_type"], "1")
        self.assertEqual(item["keywords"], ['BELGIUM', 'MOBILITEIT', 'VERKEER', 'INFRASTRUCTUUR', 'STEDEN', 'BRIEF'])
        self.assertEqual(item["administrative"], {'foreign_id': '0'})
        self.assertEqual(item["authors"], [{'name': 'COR 360', 'role': 'CORRESPONDENT'}])
        self.assertEqual(item["priority"], 3)
        self.assertEqual(item["urgency"], 3)
        self.assertEqual(item["source"], "BELGA")
        self.assertEqual(item["extra"], {'city': 'ANTWERPEN', 'country': 'BELGIUM'})
        self.assertEqual(item["type"], "text")
        self.assertEqual(
            item['body_html'],
            '<p>Auto&#x27;s, vrachtverkeer en het openbaar vervoer zullen het kruispunt twee '
            'maanden lang niet kunnen passeren, fietsers en voetgangers wel via een gemengde '
            'doorgang langs de werf. Lokaal verkeer kan de Noordersingel en Slachthuislaan in'
            'rijden maar zal een keerbeweging moeten maken aan het kruispunt. Vanop de snelwe'
            'g zal je via de afrit Deurne wel richting Deurne of Merksem kunnen rijden, maar '
            'niet naar de binnenstad. De afrit Borgerhout is een alternatief voor het oosteli'
            'jke deel van het stadscentrum, de afrit Merksem voor het noordelijke. De oprit a'
            'an het Sportpaleis zal eveneens enkel bereikbaar zijn vanuit Deurne en Merksem.<'
            '/p><p> De werken kaderen in de grote heraanleg van de Noordersingel, volgens het'
            ' beeld van de zuidelijke Singel. In elke rijrichting zullen er nog twee rijstrok'
            'en zijn met een groene berm ertussenin. Aan beide zijden komt een breed fietspad'
            ' dat afgescheiden is van de rijweg door een groenstrook of vergroende parkeerstr'
            'ook. Ook de kruispunten worden veiliger gemaakt.</p>'
        )
