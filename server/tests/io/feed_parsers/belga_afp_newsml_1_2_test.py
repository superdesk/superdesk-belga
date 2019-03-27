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
from belga.io.feed_parsers.belga_afp_newsml_1_2 import BelgaAFPNewsMLOneFeedParser


class BelgaAFPNewsMLOneTestCase(TestCase):
    filename = 'afp_belga.xml'

    def setUp(self):
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
        self.assertEqual(item["priority"], "4")
        self.assertEqual(item["language"], "fr")
        expected_body = \
            (
                "\n<p>Le procès de deux anciens fonctionnaires de la police aux frontières (PAF) de l'aéropo"
                "rt parisien Roissy-Charles de Gaulle, accusés d'avoir facilité l'importation de cocaïne de"
                " retour de République dominicaine, s'est ouvert lundi devant un tribunal à Paris. </p>\n<p>"
                'Clément Geisse, 42 ans, et Christophe Peignelin, 56 ans, comparaissent notamment pour impo'
                'rtation de stupéfiants en bande organisée - un crime passible de trente ans de réclusion -'
                " et corruption passive, devant la cour d'assises spéciale, composée de magistrats professi"
                "onnels, sans jury. </p>\n<p>Les deux hommes aux cheveux bruns coupés courts, l'un la mâchoi"
                "re carrée, l'autre le visage émacié, ont pénétré dans le box des accusés, déclinant d'un t"
                'on grave leur identité et leur ancienne profession.</p>\n<p>Ils ont reconnu avoir permis se'
                'pt à neuf passages de "mules" aux valises chargées de cocaïne en les aidant à contourner l'
                "es contrôles de l'aéroport de Roissy, entre 2010 et le 25 janvier 2015, date de leur inter"
                'pellation. Ils venaient de tenter de faire sortir deux valises contenant chacune 20 kilos '
                "de drogue. </p>\n<p>A l'autre extrémité du box, figure Kamel Berkaoui, 43 ans, patron présu"
                'mé du réseau démantelé à la suite d\'une enquête dénommée "Excédent bagage", menée par l\'Of'
                'fice central pour la répression du trafic illicite des stupéfiants (Ocrtis). </p>\n<p>Neuf '
                'membres présumés de son organisation sont également jugés par la cour. </p>\n<p>Les enquête'
                "urs n'ont pas réussi à déterminer quelle quantité de drogue avait pu être importée depuis "
                'Punta Cana en République dominicaine. </p>\n<p>Les ex-policiers auraient empoché au total e'
                'ntre 540.000 et 620.000 euros, à raison de 40.000 euros par "mule" récupérée, selon une es'
                'timation fournie en interrogatoire par Clément Geisse. </p>\n<p>Le verdict est attendu le 7'
                ' février. </p>\n<p>asl/tib/pid/cac</p>\n\n'
            )
        self.assertEqual(item["body_html"], expected_body)
        self.assertEqual(item["guid"], "urn:newsml:afp.com:20190121T104233Z:TX-PAR-RHO61:1")
        self.assertEqual(item["format"], "NITF3.1")
        self.assertEqual(item["ingest_provider_sequence"], "0579")
        self.assertEqual(item["urgency"], "4")
        self.assertEqual(item["keywords"], ["France", "procès", "assises", "drogues", "police"])
        self.assertEqual(item["firstcreated"].isoformat(), "2019-01-21T10:42:33+00:00")
        self.assertEqual(item["version"], "1")
        self.assertEqual(item["headline"], "France: deux ex-policiers aux frontières devant la justice pour trafic de "
                                           "cocaïne")
        self.assertEqual(item["versioncreated"].isoformat(), "2019-01-21T10:42:33+00:00")
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["OfInterestTo"],
                         ["DAB-TFG-1=DAB", "AMN-TFG-1=AMW", "ARC-TFG-1=ELU", "EUA-TFG-1=EUA", "MOA-TFG-1=MOA"])
        self.assertEqual(item["date_id"], "20190121T104233Z")
        self.assertEqual(item["generator_software"], "libg2")
        self.assertEqual(item["item_id"], "TX-PAR-RHO61")
        self.assertEqual(item["news_item_type"], "News")
        self.assertEqual(item["line_text"], "(Croquis d'audience+Photo+Video)")
        self.assertEqual(item["line_type"], "ProductLine")
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["products"], ["DAB", "AMW", "ELU", "EUA", "MOA", "FEUA"])
        self.assertEqual(item["provider_id"], "afp.com", )
        self.assertEqual(item["service"], "DGTE")
        self.assertEqual(item["pubstatus"], "Usable")
