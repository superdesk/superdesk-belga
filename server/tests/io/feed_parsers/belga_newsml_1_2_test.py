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
from io import BytesIO
from unittest.mock import MagicMock
from lxml import etree

from superdesk import get_resource_service
from belga.io.feed_parsers.belga_newsml_1_2 import BelgaNewsMLOneFeedParser
from tests import TestCase


class BelgaNewsMLOneTestCase(TestCase):
    filename = 'belga_newsml_1_2.xml'

    def setUp(self):
        super().setUp()

        self.users = [
            {'username': 'DWM', 'display_name': 'DWM'},
        ]

        self.app.data.insert('users', self.users)

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
        self.assertEquals(item['authors'], [
            {
                '_id': [str(self.users[0]['_id']), 'AUTHOR'],
                'name': 'AUTHOR',
                'parent': str(self.users[0]['_id']),
                'role': 'AUTHOR',
                'sub_label': 'DWM',
            },
        ])
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
        self.assertEqual(item['firstcreated'], datetime.datetime(2019, 1, 29, 11, 45, 50, tzinfo=pytz.utc))
        self.assertEqual(item["guid"], "98055801")
        self.assertEqual(item["headline"], "Mediawatch dinsdag 29/01/2019 - VTM Nieuws - 13 uur")
        self.assertEqual(item["item_id"], "98055798")
        self.assertEqual(item['language'], 'nl')
        self.assertEqual(item['priority'], 3)
        self.assertEqual(item['urgency'], 3)
        self.assertEqual(item['provider_id'], 'belga.be')
        self.assertEqual(item['public_identifier'], 'urn:newsml:www.belga.be')
        self.assertEqual(item['pubstatus'], 'usable')
        self.assertEqual(item['slugline'], 'BelgaService')
        self.assertEqual(item['ednote'], "Qu'y a-t-il écrit ici?")
        self.assertEqual(item['source'], 'BELGA')
        self.assertEqual(item['subject'], [
            {'name': 'CURRENT', 'qcode': 'CURRENT', 'scheme': 'genre'},
            {'name': 'ATTENTION USERS',
             'qcode': 'ATTENTION USERS',
             'scheme': 'belga-keywords',
             'translations': {'name': {'fr': 'ATTENTION USERS',
                                       'nl': 'ATTENTION USERS'}}},
            {'name': 'PRESS',
             'qcode': 'PRESS',
             'scheme': 'belga-keywords',
             'translations': {'name': {'fr': 'Press', 'nl': 'PRESS'}}},
            {'name': 'TV',
             'qcode': 'TV',
             'scheme': 'belga-keywords',
             'translations': {'name': {'fr': 'TV', 'nl': 'TV'}}},
            {'name': 'BELGA',
             'qcode': 'BELGA',
             'scheme': 'sources'},
            {'name': 'BIN/ALG',
             'parent': 'BIN',
             'qcode': 'BIN/ALG',
             'scheme': 'services-products'},
            {'name': 'BIN/ECO',
             'parent': 'BIN',
             'qcode': 'BIN/ECO',
             'scheme': 'services-products'},
            {'name': 'NEWS/CULTURE_LIFESTYLE',
             'parent': 'NEWS',
             'qcode': 'NEWS/CULTURE_LIFESTYLE',
             'scheme': 'services-products'},
            {'name': 'Belgium',
             'qcode': 'bel',
             'scheme': 'countries',
             'translations': {'name': {'fr': 'Belgique', 'nl': 'België'}}},
        ])
        self.assertEqual(item['type'], 'text')
        self.assertEqual(item['version'], 4)
        self.assertEqual(item['versioncreated'], datetime.datetime(2019, 1, 29, 12, 34, tzinfo=pytz.utc))


class BelgaRemoteNewsMLOneTestCase(TestCase):
    filename = 'belga_remote_newsml_1_2.xml'
    media_file = 'belga_remote_newsml_1_2.jpeg'

    def setUp(self):
        super().setUp()
        self.users = [{"username": "COR360", "display_name": "John Doe"}]
        get_resource_service("users").create(self.users)
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        media_fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.media_file))
        provider = {'name': 'test', 'config': {'path': os.path.join(dirname, '../fixtures')}}
        parser = BelgaNewsMLOneFeedParser()
        with open(media_fixture, 'rb') as f:
            parser._get_file = MagicMock(return_value=BytesIO(f.read()))
        with open(fixture, 'rb') as f:
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaNewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertEqual(item["provider_id"], "belga.be")
        self.assertEqual(item["date_id"], "20190603T160217")
        self.assertEqual(item["item_id"], "0")
        self.assertEqual(item["version"], 1)
        self.assertEqual(item["public_identifier"], "urn:newsml:www.belga.be")
        self.assertEqual(item["subject"], [{'name': 'MOBILITY',
                                            'qcode': 'MOBILITY',
                                            'scheme': 'belga-keywords',
                                            'translations': {'name': {'fr': 'Mobilité', 'nl': 'Mobiliteit'}}},
                                           {'name': 'TRAFFIC',
                                            'qcode': 'TRAFFIC',
                                            'scheme': 'belga-keywords',
                                            'translations': {'name': {'fr': 'Circulation', 'nl': 'Verkeer'}}},
                                           {'name': 'INFRASTRUCTURE',
                                            'qcode': 'INFRASTRUCTURE',
                                            'scheme': 'belga-keywords',
                                            'translations': {'name': {'fr': 'Infrastructure',
                                                                      'nl': 'Infrastructuur'}}},
                                           {'name': 'CITIES',
                                            'qcode': 'CITIES',
                                            'scheme': 'belga-keywords',
                                            'translations': {'name': {'fr': 'Villes', 'nl': 'Steden'}}},
                                           {'name': 'BRIEF',
                                            'qcode': 'BRIEF',
                                            'scheme': 'belga-keywords',
                                            'translations': {'name': {'fr': 'BRIEF', 'nl': 'BRIEF'}}},
                                           {'name': 'BELGA',
                                            'qcode': 'BELGA',
                                            'scheme': 'sources'},
                                           {'name': 'ANP',
                                            'qcode': 'ANP',
                                            'scheme': 'sources'},
                                           {'name': 'BIN/ALG',
                                            'parent': 'BIN',
                                            'qcode': 'BIN/ALG',
                                            'scheme': 'services-products'},
                                           {'name': 'S1', 'qcode': 'S1', 'scheme': 'label'}])
        self.assertEqual(str(item["firstcreated"]), "2019-06-03 14:02:17+00:00")
        self.assertEqual(str(item["versioncreated"]), "2019-06-03 14:02:17+00:00")
        self.assertEqual(item["pubstatus"], "usable")
        self.assertEqual(item["language"], "nl")
        self.assertEqual(item["byline"], "BELGA")
        self.assertEqual(item["headline"], "Knooppunt Schijnpoort in Antwerpen hele zomervakantie afgesloten")
        self.assertEqual(item["copyrightholder"], "Belga")
        self.assertEqual(item["line_type"], "1")
        self.assertEqual(item["administrative"], {'foreign_id': '0'})
        self.assertEqual(item["authors"], [{
            'name': 'CORRESPONDENT',
            'role': 'CORRESPONDENT',
            'sub_label': 'John Doe',
            'parent': str(self.users[0]['_id']),
            '_id': [str(self.users[0]['_id']), 'CORRESPONDENT'],
        }])
        self.assertEqual(item["priority"], 3)
        self.assertEqual(item["urgency"], 3)
        self.assertEqual(item["source"], "ANP/BELGA")
        self.assertEqual(item["extra"], {'city': 'ANTWERPEN'})
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


class BelgaNewsMLOneVideoIngestTestCase(TestCase):
    filename = 'belga_newsml_1_2_video.xml'

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test', 'config': {'path': os.path.join(dirname, '../fixtures')}}
        parser = BelgaNewsMLOneFeedParser()

        def get_file_side_effect(value):
            media_path = os.path.normpath(os.path.join(dirname, '../fixtures', value))
            with open(media_path, 'rb') as f:
                return BytesIO(f.read())

        parser._get_file = MagicMock(side_effect=get_file_side_effect)

        with open(fixture, 'rb') as f:
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_video_ingest(self):
        item = self.item[0]

        self.assertEqual(
            item['administrative'],
            {
                'foreign_id': 'INT126',
                'validation_date': '20200609T152302',
                'validator': 'mwe'
            }
        )
        self.assertEqual(item['pubstatus'], 'usable')
        self.assertEqual(item['language'], 'fr')
        self.assertEqual(item['byline'], 'BELGA')
        self.assertEqual(item['copyrightholder'], 'Belga')
        self.assertEqual(item['version'], 12)
        self.assertEqual(
            item['description_text'],
            '<p>TRADE UNIONS FGTB ABVV CHAIRMAN DEBATE</p><p> '
            '00:00:00:00 - 00:00:32:04 ABVV/FGTB socialist union '
            'general secretary Miranda Ulens talks in French during a '
            'press conference after a meeting of the top of the '
            'FGTB-ABVV socialist trade union, regarding the fate of '
            'their chairman Vertenueil, Tuesday 09 June 2020 at the '
            'headquarters in Brussels. Yesterday the party members '
            'voted no confidence in Vertenueil, after he had a '
            'meeting with president of MR liberals Bouchez. BELGA '
            'VIDEO MAARTEN WEYNANTS.</p>'
        )
        self.assertEqual(
            item['extra'],
            {'city': 'BRUXELLES'}
        )
        self.assertEqual(
            item['headline'],
            '"Nous avons la confiance de l\'ensemble des centrales et '
            'régionales" (Miranda Ulens)'
        )
        self.assertEqual(item['line_type'], '1')
        self.assertEqual(item['priority'], 3)
        self.assertEqual(item['type'], 'video')
        self.assertEqual(item['urgency'], 3)
        self.assertEqual(item['type'], 'video')
        self.assertEqual(
            item['subject'],
            [{'name': 'UNIONS',
              'qcode': 'UNIONS',
              'scheme': 'belga-keywords',
              'translations': {'name': {'fr': 'Syndicats', 'nl': 'Vakbonden'}}},
             {'name': 'BELGAINSERT',
              'qcode': 'BELGAINSERT',
              'scheme': 'belga-keywords',
              'translations': {'name': {'fr': 'BelgaInsert', 'nl': 'BelgaInsert'}}},
             {'name': 'BELGA',
              'qcode': 'BELGA',
              'scheme': 'sources'},
             {'name': 'INT/ECO',
              'parent': 'INT',
              'qcode': 'INT/ECO',
              'scheme': 'services-products'},
             {'name': 'Belgium',
              'qcode': 'bel',
              'scheme': 'countries',
              'translations': {'name': {'fr': 'Belgique', 'nl': 'België'}}}]
        )
        self.assertIn('href', item['renditions']['original'])
        self.assertIn('media', item['renditions']['original'])
        self.assertEqual(item['renditions']['original']['mimetype'], 'video/mp4')
        self.assertIn('href', item['renditions']['thumbnail'])
        self.assertIn('media', item['renditions']['thumbnail'])
        self.assertEqual(item['renditions']['thumbnail']['mimetype'], 'image/jpeg')


class BelgaNewsMLOneAudioIngestTestCase(TestCase):
    filename = 'belga_newsml_1_2_audio.xml'

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test', 'config': {'path': os.path.join(dirname, '../fixtures')}}
        parser = BelgaNewsMLOneFeedParser()

        def get_file_side_effect(value):
            media_path = os.path.normpath(os.path.join(dirname, '../fixtures', value))
            with open(media_path, 'rb') as f:
                return BytesIO(f.read())

        parser._get_file = MagicMock(side_effect=get_file_side_effect)

        with open(fixture, 'rb') as f:
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_audio_ingest(self):
        item = self.item[0]

        self.assertIn('href', item['renditions']['original'])
        self.assertIn('media', item['renditions']['original'])
        self.assertEqual(item['renditions']['original']['mimetype'], 'audio/mpeg')
