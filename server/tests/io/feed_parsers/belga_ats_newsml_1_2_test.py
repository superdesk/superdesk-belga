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

from belga.io.feed_parsers.belga_ats_newsml_1_2 import BelgaATSNewsMLOneFeedParser
from tests import TestCase


class BelgaATSNewsMLOneTestCase(TestCase):
    filename = 'ats_newsml_1_2_belga.xml'

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test'}
        with open(fixture, 'rb') as f:
            parser = BelgaATSNewsMLOneFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaATSNewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        item["subject"].sort(key=lambda i: i['name'])
        expected_subjects = [
            {'name': 'Current', 'qcode': 'Current', 'scheme': 'genre'},
            {'name': 'default', 'qcode': 'default', 'scheme': 'distribution'},
            {'qcode': '08000000', 'name': 'human interest', 'scheme': 'iptc_subject_codes'},
            {'name': 'NEWS/GENERAL', 'qcode': 'NEWS/GENERAL', 'parent': 'NEWS', 'scheme': 'services-products'},
            {'qcode': '04007000', 'name': 'consumer goods', 'scheme': 'iptc_subject_codes'},
            {'qcode': '04001000', 'name': 'agriculture', 'scheme': 'iptc_subject_codes'},
            {'qcode': '04000000', 'name': 'economy, business and finance', 'scheme': 'iptc_subject_codes'},
            {'name': 'ATS', 'qcode': 'ATS', 'scheme': 'sources'}
        ]
        expected_subjects.sort(key=lambda i: i['name'])
        self.assertEqual(item["slugline"], None)
        self.assertEqual(item["keywords"], [])
        self.assertEqual(item["subject"], expected_subjects)
        self.assertEqual(item["priority"], 4)
        self.assertEqual(item["provider_id"], "www.sda-ats.ch")
        self.assertEqual(item["date_id"], "20190603")
        self.assertEqual(item["item_id"], "bsf153")
        self.assertEqual(item["version"], "1")
        self.assertEqual(item["guid"], "urn:newsml:www.sda-ats.ch:20190603:bsf153:1N")
        self.assertEqual(str(item["firstcreated"]), "2019-06-03 15:47:29+00:00")
        self.assertEqual(str(item["versioncreated"]), "2019-06-03 15:47:29+00:00")
        self.assertEqual(item["pubstatus"], "usable")
        self.assertEqual(item["urgency"], 4)
        self.assertEqual(item["dateline"], {'text': 'Landquart GR'})
        self.assertEqual(item["headline"], "Un taureau entre dans un magasin à Landquart (GR)")
        self.assertEqual(item["line_type"], "CatchWord")
        self.assertEqual(item["line_text"], "Animaux")
        self.assertEqual(item["administrative"], {'provider': 'ats', 'source': 'ats'})
        self.assertEqual(item["language"], "FR")
        self.assertEqual(item["extra"], {'how_present': '', 'country': 'CH', 'country_area': 'KGR'})
        self.assertEqual(item["format"], "NITF")
        self.assertEqual(item["characteristics"], {'format_version': '3.0'})
        self.assertEqual(item["type"], "text")
        self.assertIsNone(item.get("authors"))
        expected_body = \
            (
                '\n                  <p lede="true">Un taureau âgé d\'un an est entré dans un magasin Denner lundi à La'
                "ndquart (GR). L'animal, qui s'était échappé de son enclos peu après 11h00, est ressorti par l'autre "
                "côté du bâtiment. Il n'y a pas eu de blessé.</p>\n                  <p>L'animal est entré dans le mag"
                'asin et en est sorti rapidement, a indiqué Anita Senti, porte-parole de la police cantonale des Gris'
                'ons. Elle confirme une information du site en ligne de 20Minuten.</p>\n                  <p>Le jeune '
                "taureau s'est ensuite dirigé vers Maienfeld (GR). Avec l'aide du propriétaire de l'animal, deux patr"
                'ouilles de police ont réussi à le diriger vers un champ peu avant midi. Il a ensuite été transporté '
                'dans son enclos.</p>\n                \n              '

            )
        self.assertEqual(item["body_html"], expected_body)
