# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.tests import TestCase
from lxml import etree
import os
from belga.io.feed_parsers.belga_newsml_1_2 import BelgaNewsMLOneFeedParser


class BaseBelgaNewsMLParserTestCase(TestCase):
    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test'}
        with open(fixture, 'rb') as f:
            parser = BelgaNewsMLOneFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)


class AFPBelgaNewsMLTestCase(BaseBelgaNewsMLParserTestCase):
    filename = 'afp_belga.xml'

    def test_can_parse(self):
        self.assertTrue(BelgaNewsMLOneFeedParser().can_parse(self.xml_root))

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
        self.assertEqual(item["item_type"], "News")
        self.assertEqual(item["line_text"], "(Croquis d'audience+Photo+Video)")
        self.assertEqual(item["line_type"], "ProductLine")
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["products"], ["DAB", "AMW", "ELU", "EUA", "MOA", "FEUA"])
        self.assertEqual(item["provider_id"], "afp.com", )
        self.assertEqual(item["service"], "DGTE")
        self.assertEqual(item["pubstatus"], "Usable")


class ANPBelgaNewsMLTestCase(BaseBelgaNewsMLParserTestCase):
    filename = 'anp_belga.xml'

    def test_can_parse(self):
        self.assertTrue(BelgaNewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]

        self.assertEqual(item["item_type"], "News")
        self.assertEqual(item["firstcreated"].isoformat(), "2018-12-10T09:35:49+01:00")
        self.assertEqual(item["pubstatus"], "usable")
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["versioncreated"].isoformat(), "2018-12-10T12:37:31+01:00")
        self.assertEqual(item["guid"], "urn:newsml:anp.nl:20181210:ANPX-101218-041:2")
        self.assertEqual(item["location"], {'country': 'NL', 'how_present_el': 'Origin', 'city': 'UTRECHT'})
        self.assertEqual(item["format"], "NITF")
        self.assertEqual(item["ingest_provider_sequence"], "20181210123731041")
        self.assertEqual(item["date_id"], "20181210")
        self.assertEqual(item["dateline"], {})
        self.assertEqual(item["urgency"], "3")
        self.assertEqual(item["headline"], "FNV staat alleen met acties bij PostNL (2)")
        self.assertEqual(item["item_id"], "ANPX-101218-041-v2")
        self.assertEqual(item["sentfrom"], {'party': 'Algemeen Nederlands Persbureau', 'comment': 'News Provider'})
        self.assertEqual(item["administrative"], {'provider': 'ANP'})
        self.assertEqual(item["products"], ['ANP Nieuws'])
        self.assertEqual(item["language"], "nl-nl")
        self.assertEqual(item["news_component_equivalentslist"], "no")
        self.assertEqual(item["date_label"], "10 december 2018")
        self.assertEqual(item["genre"], [{'name': 'ECO'}])
        self.assertEqual(item["version"], "2")
        self.assertEqual(item["news_component_essential"], "no")
        self.assertEqual(item["provider_id"], "ANP")
        self.assertEqual(item["characteristics"],
                         {'characters': '1043', 'word_count': '177', 'creator': 'redsys v4.30'})
        self.assertEqual(item["label"], None)
        self.assertEqual(item["subject"], [{'name': '', 'scheme': '', 'qcode': 'ECO'}])
        self.assertEqual(item["priority"], "3")
        self.assertEqual(item["keywords"], ['POST-CAO'])
        expected_body = \
            (
                '\n\t\t\t\t\t\t\t\t<p>N i e u w bericht, vervangt: FNV staat alleen met ultimatum aan Post'
                'NL</p>\n\t\t\t\t\t\t\t\t<p>UTRECHT (ANP) - FNV kondigt werkonderbrekingen aan bij PostNL,'
                ' nadat de post- en pakketbezorger maandag niet inging op een ultimatum voor toez'
                'eggingen over een nieuwe cao. De drie andere bonden die met PostNL onderhandelen'
                ' over een nieuwe cao, zien niets in actievoeren.</p>\n\t\t\t\t\t\t\t\t<p>FNV overlegt nog'
                ' met leden over de precieze omvang en lengte van de stakingen. Later deze week w'
                'ordt bekend waar postbezorgers het werk neerleggen.</p>\n\t\t\t\t\t\t\t\t<p>Andere betrok'
                'ken bonden vinden het nog te vroeg voor stakingen. ,,Het is veel te snel om na v'
                "ijf uur onderhandelen naar het actiemiddel te grijpen'', zei Anselma Zwaagstra v"
                'an CNV. Ook BVPP en VHP2 zien meer heil in een hervatting van het overleg met Po'
                'stNL aanstaande woensdag.</p>\n\t\t\t\t\t\t\t\t<p>De drie bonden vinden het ook een brug '
                'te ver om juist in de drukke periode rond kerst en oud en nieuw acties te organi'
                'seren. Die kunnen PostNL dusdanig hard raken dat ook de werkgelegenheid bij het '
                'bedrijf in gevaar komt, waarschuwen ze in een gezamenlijke brief aan hun leden.<'
                '/p>\n\t\t\t\t\t\t\t\n\t\t\t\t\t\t'

            )
        self.assertEqual(item["body_html"], expected_body)


class EFEBelgaNewsMLTestCase(BaseBelgaNewsMLParserTestCase):
    filename = 'efe_belga.xml'

    def test_can_parse(self):
        self.assertTrue(BelgaNewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertEqual(item["location"], {'how_present_el': 'Event', 'country': 'IND'})
        self.assertEqual(item["pubstatus"], "Usable")
        self.assertEqual(item["efe_regional"], "")
        self.assertEqual(item["administrative"], {'provider': 'Agencia EFE', 'creator': 'daa/mt/msr'})
        self.assertEqual(item["efe_pais"], "IND")
        self.assertEqual(item["headline"], "Leones matan a un joven que se coló en un zoológico de la India")
        self.assertEqual(item["comment"], {'version': '1.0.1', 'name': 'EfeNewsMLVersion'})
        self.assertEqual(item["duid"], "text_25413502")
        self.assertEqual(item["firstcreated"].isoformat(), "2019-01-21T10:36:00+00:00")
        self.assertEqual(item["item_type"], "News")
        self.assertEqual(item["item_id"], "25413502")
        self.assertEqual(item["role"], "Main")
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["format"], "NITF")
        self.assertEqual(item["products"], ['Texto internacional general para España'])
        self.assertEqual(item["efe_complemento"], "")
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["sentfrom"], {'organization': 'Agencia EFE', 'party': 'EFE'})
        self.assertEqual(item["versioncreated"].isoformat(), "2019-01-21T10:36:00+00:00")
        self.assertEqual(item["version"], "1")
        self.assertEqual(item["language"], "es-ES")
        self.assertEqual(item["tesauro"],
                         "TRI:JUSTICIA-INTERIOR-SUCESOS,SUCESOS;CYT:CIENCIA-TECNOLOGIA,AMBIENTE-NATURALEZA")
        self.assertEqual(item["guid"], "text_25413502.text")
        self.assertEqual(item["subject"],
                         [{'qcode': '06002001', 'name': 'endangered species', 'scheme': 'IptcSubjectCodes'},
                          {'qcode': '02001000', 'name': 'crime', 'scheme': 'IptcSubjectCodes'}])
        self.assertEqual(item["mime_type"], "text/vnd.IPTC.NITF")
        self.assertEqual(item["provider_id"], "texto.efeservicios.com")
        self.assertEqual(item["urgency"], "5")
        self.assertEqual(item["date_id"], "20190121T103600+0000")
        self.assertEqual(item["genre"], [])

        expected_body = \
            (
                '\n<p>Nueva Delhi, 21 ene (EFE).- Una pareja de leones asiáticos hirieron mortalme'
                'nte a un joven de unos 26 años de edad que se coló en un área restringida de un '
                'zoológico cercano a la ciudad de Chandigarh, en el norte de la India, informó ho'
                'y a Efe una fuente oficial.</p>\n<p>El hombre, cuya identidad continúa siendo un '
                'misterio, trató de entrar al parque el domingo saltando un muro trasero de casi '
                'cinco metros de altura y fue a parar directamente a un recinto ocupado por dos l'
                'eones adultos, dijo el secretario adjunto del departamento forestal de Punjab, R'
                'oshan Sunkaria.</p>\n<p>"Una patrulla se encontraba cerca de la zona mientras est'
                'aba saltando y le gritó que no lo hiciera, pero hizo caso omiso y se lanzó al re'
                'cinto", añadió.</p>\n<p>En cuestión de minutos uno de los leones atacó al hombre,'
                ' según la fuente.</p>\n<p>"El equipo se adentró con un vehículo en la zona y le r'
                'escató. En ese momento seguía con vida y le llevó al hospital. Desafortunadament'
                'e cuando llegaron ya había muerto", lamentó Sunkaria.</p>\n<p>El joven no llevaba'
                ' consigo documentos identificativos ni un teléfono móvil, pero el funcionario es'
                'timó que tendría unos 26 años.</p>\n<p>"No sé lo que estaba haciendo, pero cierta'
                'mente no se encontraba en sus cabales", declaró, antes de añadir que por el mome'
                'nto nadie ha reclamado el cuerpo y que quizá la autopsia dirá si el hombre estab'
                'a borracho.</p>\n<p>Un suceso similar ocurrió en 2014 en el zoológico de Nueva De'
                'lhi, cuando un tigre blanco mató a un joven que cayó dentro del recinto del anim'
                'al.</p>\n<p>El león asiático es una especie amenazada en la India, cuyo principal'
                ' santuario se encuentra en el entorno del parque Gir y, según los datos del Fond'
                'o Mundial para la Naturaleza (WWF), en la actualidad el país cuenta con una pobl'
                'ación de unos 500 ejemplares. EFE</p>\n\n'
            )
        self.assertEqual(item["body_html"], expected_body)


class TASSBelgaNewsMLTestCase(BaseBelgaNewsMLParserTestCase):
    filename = 'tass_belga.xml'

    def test_can_parse(self):
        self.assertTrue(BelgaNewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertEqual(item["role"], "Main")
        self.assertEqual(item["slug_line"], "URGENT")
        self.assertEqual(item["dateline"], {'text': 'January 21'})
        self.assertEqual(item["genre"], [])
        self.assertEqual(item["item_type"], "News")
        self.assertEqual(item["products"], ['FILE_MROUTER'])
        self.assertEqual(item["news_component_essential"], "no")
        self.assertEqual(item["guid"], "03AE4325838900396A95")
        self.assertEqual(item["date_line"], "January 21")
        self.assertEqual(item["language"], "en")
        self.assertEqual(item["news_component_equivalentslist"], "no")
        self.assertEqual(item["headline"], "Kremlin has 'negative reaction' to upcoming EU sanctions")
        self.assertEqual(item["link_type"], "normal")
        self.assertEqual(item["location"], {'how_present_el': 'Origin', 'city': 'MOSCOW'})
        self.assertEqual(item["subject"], [])
        self.assertEqual(item["item_keywords"], ['itartassrubric_URGENT', 'URGENT'])
        self.assertEqual(item["mime_type"], "text/vnd.IPTC.NITF")
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["urgency"], "")
        self.assertEqual(item["pubstatus"], "Usable")
        self.assertEqual(item["provider_id"], "\nwww.itar-tass.com\n")
        self.assertEqual(item["versioncreated"].isoformat(), "2019-01-21T10:27:08")
        self.assertEqual(item["firstcreated"].isoformat(), "2019-01-21T10:27:08")
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
