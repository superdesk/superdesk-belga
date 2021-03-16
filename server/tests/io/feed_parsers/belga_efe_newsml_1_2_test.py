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

from belga.io.feed_parsers.belga_efe_newsml_1_2 import BelgaEFENewsMLOneFeedParser
from tests import TestCase


class BelgaEFENewsMLOneTestCase(TestCase):
    filename = 'efe_belga.xml'

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test'}
        with open(fixture, 'rb') as f:
            parser = BelgaEFENewsMLOneFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaEFENewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        item["subject"].sort(key=lambda i: i['name'])
        expected_subjects = [
            {'name': 'NEWS/POLITICS', 'qcode': 'NEWS/POLITICS', 'parent': 'NEWS', 'scheme': 'services-products'},
            {'qcode': '01026000', 'name': 'mass media', 'scheme': 'iptc_subject_codes'},
            {'name': 'EFE', 'qcode': 'EFE', 'scheme': 'sources'},
            {'name': 'default', 'qcode': 'default', 'scheme': 'distribution'},
            {'name': 'India', 'qcode': 'country_ind', 'scheme': 'country',
             'translations': {'name': {'fr': 'Inde', 'nl': 'India'}}},
        ]
        expected_subjects.sort(key=lambda i: i['name'])
        self.assertEqual(item["slugline"], None)
        self.assertEqual(item["keywords"], [])
        self.assertEqual(item["subject"], expected_subjects)
        self.assertEqual(item['anpa_category'], [{'qcode': 'POL'}])
        self.assertEqual(item["sentfrom"], {'party': 'EFE', 'organization': 'Agencia EFE'})
        self.assertEqual(item["duid"], "text_25413502")
        self.assertEqual(item["comment"], {'version': '1.0.1', 'name': 'EfeNewsMLVersion'})
        self.assertEqual(item["provider_id"], "texto.efeservicios.com")
        self.assertEqual(item["date_id"], "20190121T103600+0000")
        self.assertEqual(item["item_id"], "25413502")
        self.assertEqual(item["version"], "1")
        self.assertEqual(item["guid"], "urn:newsml:texto.efeservicios.com:20190121T103600+0000:25413502:1")
        self.assertEqual(str(item["firstcreated"]), "2019-01-21 10:36:00+00:00")
        self.assertEqual(str(item["versioncreated"]), "2019-01-21 10:36:00+00:00")
        self.assertEqual(item["pubstatus"], "usable")
        self.assertEqual(item["urgency"], 5)
        self.assertEqual(item["role"], "Main")
        self.assertEqual(item["headline"], "Leones matan a un joven que se coló en un zoológico de la India")
        self.assertEqual(item["sub_head_line"], "INDIA SUCESOS")
        self.assertEqual(item["copyright_line"],
                         "© EFE 2019. Está expresamente prohibida la redistribución y la redifusión de todo o parte "
                         "de los contenidos de los servicios de Efe, sin previo y expreso consentimiento de la "
                         "Agencia EFE S.A.")
        self.assertEqual(item["administrative"], {'provider': 'Agencia EFE', 'creator': 'daa/mt/msr'})
        self.assertEqual(item["language"], "es-ES")
        self.assertEqual(item["extra"], {'how_present': 'Event', 'country': 'IND'})
        self.assertEqual(item["tesauro"],
                         "TRI:JUSTICIA-INTERIOR-SUCESOS,SUCESOS;CYT:CIENCIA-TECNOLOGIA,AMBIENTE-NATURALEZA")
        self.assertEqual(item["efe_pais"], "IND")
        self.assertEqual(item["efe_regional"], "")
        self.assertEqual(item["efe_complemento"], "")
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["mimetype"], "text/vnd.IPTC.NITF")
        self.assertEqual(item["format"], "NITF")

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
