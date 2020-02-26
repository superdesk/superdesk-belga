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
from unittest.mock import MagicMock
from io import BytesIO
from superdesk import get_resource_service
from lxml import etree
from superdesk.tests import TestCase
from belga.io.feed_parsers.belga_remote_newsml_1_2 import BelgaRemoteNewsMLOneFeedParser


class BelgaRemoteNewsMLOneTestCase(TestCase):
    filename = 'belga_remote_newsml_1_2.xml'
    media_file = 'belga_remote_newsml_1_2.jpeg'

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        media_fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.media_file))
        provider = {'name': 'test', 'config': {'path': os.path.join(dirname, '../fixtures')}}
        parser = BelgaRemoteNewsMLOneFeedParser()
        with open(media_fixture, 'rb') as f:
            parser._get_file = MagicMock(return_value=BytesIO(f.read()))
        with open(fixture, 'rb') as f:
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaRemoteNewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertEqual(item["provider_id"], "belga.be")
        self.assertEqual(item["date_id"], "20190603T160217")
        self.assertEqual(item["item_id"], "0")
        self.assertEqual(item["version"], 1)
        self.assertEqual(item["public_identifier"], "urn:newsml:www.belga.be")
        self.assertEqual(item["subject"], [{'name': 'NEWS', 'qcode': 'NEWS', 'scheme': 'news_item_types'},
                                           {'name': 'BIN/ALG', 'qcode': 'BIN/ALG', 'scheme': 'services-products',
                                            'parent': 'BIN'},
                                           {'name': 'S1', 'qcode': 'S1', 'scheme': 'label'}])
        self.assertEqual(str(item["firstcreated"]), "2019-06-03 14:02:17+00:00")
        self.assertEqual(str(item["versioncreated"]), "2019-06-03 14:02:17+00:00")
        self.assertEqual(item["pubstatus"], "usable")
        self.assertEqual(item["guid"], "d7131990f7f288f4ca0981d2d7530b64")
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
            item['abstract'],
            'In Antwerpen zal het kruispunt van de Schijnpoortweg met de Noordersingel en Sla'
            'chthuislaan in juli en augustus volledig afgesloten worden voor nutswerken. Er w'
            'orden waterleidingen en gasleidingen onder het kruispunt geplaatst en de afwater'
            'ing van de Antwerpse ring en de Schijn-Scheldeverbinding krijgen nieuwe kokers, '
            'zo meldt de Beheersmaatschappij Antwerpen Mobiel (BAM) vrijdag. Na die werken wo'
            'rdt bovendien ook het kruispunt zelf heraangelegd. De BAM hoopt de hinder zoveel'
            ' mogelijk te beperken door de werken in de zomermaanden uit te voeren, wanneer e'
            'r sowieso minder verkeer is en bovendien de naburige concertzalen geen evenement'
            'en organiseren.'
        )
        self.assertEqual(
            item['body_html'],
            '<p>In Antwerpen zal het kruispunt van de Schijnpoortweg met de Noordersingel en '
            'Slachthuislaan in juli en augustus volledig afgesloten worden voor nutswerken. E'
            'r worden waterleidingen en gasleidingen onder het kruispunt geplaatst en de afwa'
            'tering van de Antwerpse ring en de Schijn-Scheldeverbinding krijgen nieuwe koker'
            's, zo meldt de Beheersmaatschappij Antwerpen Mobiel (BAM) vrijdag. Na die werken'
            ' wordt bovendien ook het kruispunt zelf heraangelegd. De BAM hoopt de hinder zov'
            'eel mogelijk te beperken door de werken in de zomermaanden uit te voeren, wannee'
            'r er sowieso minder verkeer is en bovendien de naburige concertzalen geen evenem'
            'enten organiseren.</p>'
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

        self.assertEqual(item['ednote'], 'The story has 1 attachment(s)')

        attachment_id = item['attachments'][0]['attachment']
        data = get_resource_service('attachments').find_one(req=None, _id=attachment_id)
        self.assertEqual(data["title"], "belga_remote_newsml_1_2.jpeg")
        self.assertEqual(data["filename"], "belga_remote_newsml_1_2.jpeg")
        self.assertEqual(data["description"], "belga remote attachment")
        self.assertEqual(data["mimetype"], "image/jpeg")
        self.assertEqual(data["length"], 4680)
