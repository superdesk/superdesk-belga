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
import datetime
from lxml import etree

from belga.io.feed_parsers.belga_afp_newsml_1_2 import BelgaAFPNewsMLOneFeedParser
from tests import TestCase


class BelgaAFPNewsMLOneTestCase(TestCase):
    filename = 'afp_belga.xml'

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test'}
        with open(fixture, 'rb') as f:
            parser = BelgaAFPNewsMLOneFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaAFPNewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertEqual(item["ingest_provider_sequence"], "0579")
        item["subject"].sort(key=lambda i: i['name'])
        expected_subjects = [
            {'name': 'DAB-TFG-1=DAB', 'qcode': 'DAB-TFG-1=DAB', 'scheme': 'of_interest_to'},
            {'name': 'drug trafficking', 'qcode': '02001004', 'scheme': 'iptc_subject_codes'},
            {'name': 'trials', 'qcode': '02008000', 'scheme': 'iptc_subject_codes'},
            {'name': 'AMN-TFG-1=AMW', 'qcode': 'AMN-TFG-1=AMW', 'scheme': 'of_interest_to'},
            {'name': 'EUA-TFG-1=EUA', 'qcode': 'EUA-TFG-1=EUA', 'scheme': 'of_interest_to'},
            {'name': 'AFP', 'qcode': 'AFP', 'scheme': 'sources'},
            {'name': 'crime, law and justice', 'qcode': '02000000', 'scheme': 'iptc_subject_codes'},
            {'name': 'ARC-TFG-1=ELU', 'qcode': 'ARC-TFG-1=ELU', 'scheme': 'of_interest_to'},
            {'name': 'MOA-TFG-1=MOA', 'qcode': 'MOA-TFG-1=MOA', 'scheme': 'of_interest_to'},
            {'name': 'police', 'qcode': '02003000', 'scheme': 'iptc_subject_codes'},
            {'name': 'NEWS/ECONOMY', 'parent': 'NEWS', 'qcode': 'NEWS/ECONOMY', 'scheme': 'services-products'},
            {'name': 'NEWS/GENERAL', 'parent': 'NEWS', 'qcode': 'NEWS/GENERAL', 'scheme': 'services-products'},
            {'name': 'NEWS/SPORTS', 'parent': 'NEWS', 'qcode': 'NEWS/SPORTS', 'scheme': 'services-products'},
            {'name': 'France', 'qcode': 'country_fra', 'scheme': 'country',
             'translations': {'name': {'fr': 'France', 'nl': 'Frankrijk'}}},
            {'name': 'default', 'qcode': 'default', 'scheme': 'distribution'}
        ]
        expected_subjects.sort(key=lambda i: i['name'])
        self.assertEqual(item["subject"], expected_subjects)
        self.assertEqual(item["priority"], 4)
        self.assertEqual(item["provider_id"], "afp.com")
        self.assertEqual(item["date_id"], "20190121T104233Z")
        self.assertEqual(item["item_id"], "TX-PAR-RHO61")
        self.assertEqual(item["version"], "1")
        self.assertEqual(item["guid"], "urn:newsml:afp.com:20190121T104233Z:TX-PAR-RHO61:1")
        self.assertEqual(str(item["firstcreated"]), "2019-01-21 10:42:33+00:00")
        self.assertEqual(str(item["versioncreated"]), "2019-01-21 10:42:34+00:00")
        self.assertEqual(item["pubstatus"], "usable")
        self.assertEqual(item["urgency"], 3)
        self.assertEqual(item["associated_with"], {'item': None, 'type': ['Sketch', 'Photo', 'Video']})
        self.assertEqual(item["dateline"], {'text': 'Paris, 21 jan 2019 (AFP) -',
                                            'date': datetime.datetime(2019, 1, 21, 10, 42, 33,
                                                                      tzinfo=datetime.timezone.utc)})
        self.assertEqual(item["headline"],
                         "France: deux ex-policiers aux frontières devant la justice pour trafic de cocaïne")
        self.assertEqual(item["line_type"], "ProductLine")
        self.assertEqual(item["line_text"], "(Croquis d'audience+Photo+Video)")
        self.assertEqual(item["administrative"], {'provider': 'AFP'})
        self.assertEqual(item["language"], "fr")
        self.assertEqual(item["anpa_category"], [{'qcode': 'SPO'}, {'qcode': 'CLJ'}, {'qcode': 'ECO'}])
        self.assertEqual(item["extra"], {'how_present': 'Origin', 'country': 'FRA', 'city': 'Paris'})
        self.assertEqual(item["generator_software"], "libg2")
        self.assertEqual(item["keywords"], [])
        self.assertEqual(item["slugline"], None)
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["format"], "NITF3.1")
        self.assertEqual(item["characteristics"], {'size_bytes': '1620', 'word_count': '269'})
        expected_body = \
            (
                "\n<p><br/></p><p>   </p>"
                "\n<p> Le procès de deux anciens fonctionnaires de la police aux frontières (PAF) de l'aéroport parisie"
                "n Roissy-Charles de Gaulle, accusés d'avoir facilité l'importation de cocaïne de retour de Républiqu"
                "e dominicaine, s'est ouvert lundi devant un tribunal à Paris. </p>\n<p>Clément Geisse, 42 ans, et Chr"
                'istophe Peignelin, 56 ans, comparaissent notamment pour importation de stupéfiants en bande organisé'
                "e - un crime passible de trente ans de réclusion - et corruption passive, devant la cour d'assises s"
                'péciale, composée de magistrats professionnels, sans jury. </p>\n<p>Les deux hommes aux cheveux bruns'
                " coupés courts, l'un la mâchoire carrée, l'autre le visage émacié, ont pénétré dans le box des accus"
                "és, déclinant d'un ton grave leur identité et leur ancienne profession.</p>\n<p>Ils ont reconnu avoir"
                ' permis sept à neuf passages de "mules" aux valises chargées de cocaïne en les aidant à contourner l'
                "es contrôles de l'aéroport de Roissy, entre 2010 et le 25 janvier 2015, date de leur interpellation."
                ' Ils venaient de tenter de faire sortir deux valises contenant chacune 20 kilos de drogue. </p>\n<p>A'
                " l'autre extrémité du box, figure Kamel Berkaoui, 43 ans, patron présumé du réseau démantelé à la su"
                'ite d\'une enquête dénommée "Excédent bagage", menée par l\'Office central pour la répression du trafi'
                'c illicite des stupéfiants (Ocrtis). </p>\n<p>Neuf membres présumés de son organisation sont égalemen'
                "t jugés par la cour. </p>\n<p>Les enquêteurs n'ont pas réussi à déterminer quelle quantité de drogue "
                'avait pu être importée depuis Punta Cana en République dominicaine. </p>\n<p>Les ex-policiers auraien'
                't empoché au total entre 540.000 et 620.000 euros, à raison de 40.000 euros par "mule" récupérée, se'
                'lon une estimation fournie en interrogatoire par Clément Geisse. </p>\n<p>Le verdict est attendu le 7'
                ' février. </p>\n<p>asl/tib/pid/cac</p>\n\n'

            )
        self.assertEqual(item["body_html"], expected_body)

    def test_empty_headline(self):
        news_lines = self.xml_root.find('NewsItem/NewsComponent/NewsLines')
        headline = news_lines.find('HeadLine')
        news_lines.remove(headline)
        # set urgency
        urgency = self.xml_root.find('NewsItem/NewsManagement/Urgency')
        urgency.attrib['FormalName'] = '1'

        parser = BelgaAFPNewsMLOneFeedParser()
        item = parser.parse(self.xml_root, {'name': 'test'})
        assert item[0]['headline'] == (
            "URGENT: Le procès de deux anciens fonctionnaires de la police aux frontières (PAF) de l'aéroport parisien"
            " Roissy-Charles de Gaulle, accusés d'avoir facilité l'importation de cocaïne de retour de République "
            "dominicaine, s'est ouvert lundi devant un tribunal à Paris."
        )
