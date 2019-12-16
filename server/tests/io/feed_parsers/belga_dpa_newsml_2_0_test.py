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
from belga.io.feed_parsers.belga_dpa_newsml_2_0 import BelgaDPANewsMLTwoFeedParser
from . import BelgaTestCase


class BelgaDPANewsMLTwoTestCase(BelgaTestCase):
    filename = 'dpa_newsml_2_0_belga.xml'

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test'}
        with open(fixture, 'rb') as f:
            parser = BelgaDPANewsMLTwoFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaDPANewsMLTwoFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertEqual(item["guid"], "urn:newsml:dpa.com:20090101:190603-99-492251:3")
        self.assertEqual(item["uri"], "urn:newsml:dpa.com:20090101:190603-99-492251")
        self.assertEqual(item["version"], "3")
        self.assertEqual(item["type"], "text")
        self.assertEqual(str(item["versioncreated"]), "2019-06-03 13:00:01+00:00")
        self.assertEqual(item["pubstatus"], "usable")
        expected_ednote = \
            (
                '\nNotizblock'
                '\nRedaktionelle Hinweise'
                '\n Migranten sind nach Definition der Internationalen Organisation ‎für Migration (IOM) alle Menschen,'
                ' die ihren Wohnort verlassen – egal ‎aus welchen Gründen, wie lange oder ob freiwillig oder '
                '‎unfreiwillig. Flüchtlinge dagegen suchen Schutz vor Krieg oder vor ‎drohender Verfolgung, etwa '
                'wegen ihrer Religion, Nationalität oder ‎ihrer politischen Überzeugung. Damit sind Flüchtlinge '
                'auch Migranten‎, aber nicht alle Migranten Flüchtlinge.'
                '\n Internet'
                '\nKüstenwache Mitteilungen'
                '\nOrte'
                '\n [Alexandroupolis](Alexandroupolis 681 00, Griechenland)'
                '\n[Kleininsel Agathonisi](Agathonisi, Griechenland)'
                '\n Die folgenden Informationen sind nicht zur Veröffentlichung bestimmt'
                '\nKontakte'
                '\n Autor: Takis Tsafos (Athen), +30 6944 33 24 77, <tsafos.takis@dpa.com>'
                '\ndpa tt xx n1\n'
            )
        self.assertEqual(item["ednote"], expected_ednote)
        self.assertEqual(item["urgency"], 4)
        self.assertEqual(item["headline"], "Mehr als 200 Migranten in der Ägäis aufgegriffen")
        self.assertEqual(item["slugline"], "")
        self.assertEqual(item["language"], "de")
        item["subject"].sort(key=lambda i: i['name'])
        expected_subjects = [
            {'qcode': '11017000', 'name': 'Migration', 'scheme': 'iptc_subject_code'},
            {'qcode': '11011000', 'name': 'Flüchtling, Asyl', 'scheme': 'iptc_subject_code'},
            {'name': 'NEWS/POLITICS', 'qcode': 'NEWS/POLITICS', 'parent': 'NEWS', 'scheme': 'services-products'},
            {'name': 'DPA', 'qcode': 'DPA', 'scheme': 'credits'},
            {'name': 'default', 'qcode': 'default', 'scheme': 'distribution'}
        ]
        expected_subjects.sort(key=lambda i: i['name'])
        self.assertEqual(item["subject"], expected_subjects)
        self.assertEqual(item["extra"], {'city': 'Athen', 'country': 'Griechenland'})
        self.assertEqual(item["genre"], [])
        self.assertEqual(item["authors"], [{'uri': None, 'role': 'tsafos'}])
        self.assertEqual(item["dateline"], {'text': 'Athen (dpa) - '})
        self.assertEqual(item["credit_line"], "dpa")
        self.assertEqual(item["usageterms"], "Nutzung nur nach schriftlicher Vereinbarung mit dpa")
        self.assertEqual(item["renditions"], {})
        self.assertEqual(item["word_count"], 152)
        self.assertEqual(str(item["firstcreated"]), "2019-06-03 13:00:01+00:00")
        expected_body = \
            (
                '<p>Athen (dpa) - Ungeachtet der EU-Vereinbarung mit der Türkei kommen weiterhin Migranten '
                'über die Ägäis in die Europäische Union. Zwischen Samstag- und Montagmorgen setzten nach A'
                'ngaben der griechischen Küstenwache 234 Migranten aus der Türkei nach Griechenland über.</'
                'p><p>Vor den Inseln Lesbos und Agathonisi wurden 118 Migranten von der Küstenwache und den'
                ' Besatzungen von Schiffen der europäischen Grenzschutzagentur (Frontex) aufgegriffen.\xa0Vor '
                'der nordgriechischen Hafenstadt Alexandroupolis entdeckte die Küstenwache am Wochenende we'
                'itere 116 Migranten. Die Registrierlager (sogenannte Hotspots) auf den Inseln Lesbos, Chio'
                's, Samos, Leros und Kos sind überfüllt.</p><p>Der im März 2016 geschlossenen Flüchtlingspa'
                'kt EU-Türkei sieht vor, dass die EU alle Migranten, die illegal über die Türkei auf die gr'
                'iechischen Inseln kommen, zurückschicken kann. Im Gegenzug nehmen EU-Staaten der Türkei sc'
                'hutzbedürftige Flüchtlinge aus Syrien ab und finanzieren Hilfen für in der Türkei lebende '
                'Flüchtlinge. Auf dem Höhepunkt der Flüchtlingskrise 2015 hatte es Tage gegeben, an denen 7'
                '000 Migranten über die Türkei griechische Inseln erreichten.</p>'

            )
        self.assertEqual(item["body_html"], expected_body)
