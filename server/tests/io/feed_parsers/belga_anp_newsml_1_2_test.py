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

from belga.io.feed_parsers.belga_anp_newsml_1_2 import BelgaANPNewsMLOneFeedParser
from tests import TestCase


class BelgaANPNewsMLOneTestCase(TestCase):
    filename = "anp_belga.xml"

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, "../fixtures", self.filename))
        provider = {"name": "test"}
        with open(fixture, "rb") as f:
            parser = BelgaANPNewsMLOneFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaANPNewsMLOneFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertEqual(item["ingest_provider_sequence"], "20181210123731041")
        item["subject"].sort(key=lambda i: i["scheme"])
        expected_subjects = [
            {
                "name": "BRIEF",
                "qcode": "BRIEF",
                "translations": {"name": {"nl": "BRIEF", "fr": "BRIEF"}},
                "scheme": "belga-keywords",
            },
            {
                "name": "TENNIS",
                "qcode": "TENNIS",
                "translations": {"name": {"nl": "TENNIS", "fr": "TENNIS"}},
                "scheme": "belga-keywords",
            },
            {
                "name": "Netherlands",
                "qcode": "nld",
                "translations": {"name": {"nl": "Nederland", "fr": "Pays-Bas"}},
                "scheme": "countries",
            },
            {
                "name": "Netherlands",
                "qcode": "country_nld",
                "translations": {"name": {"nl": "NEDERLAND", "fr": "PAYS-BAS"}},
                "scheme": "country",
            },
            {"name": "default", "qcode": "default", "scheme": "distribution"},
            {"name": "no", "qcode": "no", "scheme": "equivalents_list"},
            {"name": "no", "qcode": "no", "scheme": "essential"},
            {"name": "ECO", "qcode": "ECO", "scheme": "genre"},
            {"name": "MEDVEDEV", "qcode": "MEDVEDEV", "scheme": "original-metadata"},
            {"name": "NIEUWS", "qcode": "NIEUWS", "scheme": "original-metadata"},
            {
                "name": "NEWS/ECONOMY",
                "qcode": "NEWS/ECONOMY",
                "parent": "NEWS",
                "scheme": "services-products",
            },
            {"name": "ANP", "qcode": "ANP", "scheme": "sources"},
        ]
        expected_subjects.sort(key=lambda i: i["scheme"])
        self.assertEqual(item["subject"], expected_subjects)
        self.assertEqual(item["priority"], 3)
        self.assertEqual(
            item["sentfrom"],
            {"comment": "News Provider", "party": "Algemeen Nederlands Persbureau"},
        )
        self.assertEqual(item["provider_id"], "ANP")
        self.assertEqual(item["date_id"], "20181210")
        self.assertEqual(item["item_id"], "ANPX-101218-041-v2")
        self.assertEqual(item["version"], "2")
        self.assertEqual(item["guid"], "urn:newsml:anp.nl:20181210:ANPX-101218-041:2")
        self.assertEqual(item["date_label"], "10 december 2018")
        self.assertEqual(str(item["firstcreated"]), "2018-12-10 08:35:49+00:00")
        self.assertEqual(str(item["versioncreated"]), "2018-12-10 11:37:31+00:00")
        self.assertEqual(item["pubstatus"], "usable")
        self.assertEqual(item["urgency"], 3)
        self.assertEqual(item["dateline"], {})
        self.assertEqual(item["headline"], "FNV staat alleen met acties bij PostNL (2)")
        self.assertEqual(item["sub_head_line"], None)
        self.assertEqual(item["byline"], None)
        self.assertEqual(item["by_line_title"], None)
        self.assertEqual(
            item["copyright_line"],
            "© 2018 ANP. Alle auteursrechten en databankrechten voorbehouden. All copyrights and "
            "database rights reserved.",
        )
        self.assertEqual(item["slugline"], None)
        self.assertEqual(item["keyword_line"], "ECO/ECO10;ECO-POST-CAO")
        self.assertEqual(item["administrative"], {"provider": "ANP"})
        self.assertEqual(item["language"], "nl")
        self.assertEqual(
            item["extra"],
            {"how_present": "Origin", "country": "NLD", "city": "San Mateo"},
        )
        self.assertEqual(item["keywords"], [])
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["format"], "NITF")
        self.assertEqual(
            item["characteristics"],
            {
                "creator": "redsys v4.30",
                "word_count": "177",
                "characters": "1043",
                "format_version": "3.3",
            },
        )
        self.assertEqual(item["genre"], [{"name": "ECO", "qcode": "ECO"}])
        expected_body = (
            "\n\t\t\t\t\t\t\t\t<p>N i e u w bericht, vervangt: FNV staat alleen met ultimatum aan Post"
            "NL</p>\n\t\t\t\t\t\t\t\t<p>San Mateo (ANP) - FNV kondigt werkonderbrekingen aan bij PostNL,"
            " nadat de post- en pakketbezorger maandag niet inging op een ultimatum voor toez"
            "eggingen over een nieuwe cao. De drie andere bonden die met PostNL onderhandelen"
            " over een nieuwe cao, zien niets in actievoeren.</p>\n\t\t\t\t\t\t\t\t<p>FNV overlegt nog"
            " met leden over de precieze omvang en lengte van de stakingen. Later deze week w"
            "ordt bekend waar postbezorgers het werk neerleggen.</p>\n\t\t\t\t\t\t\t\t<p>Andere betrok"
            "ken bonden vinden het nog te vroeg voor stakingen. ,,Het is veel te snel om na v"
            "ijf uur onderhandelen naar het actiemiddel te grijpen'', zei Anselma Zwaagstra v"
            "an CNV. Ook BVPP en VHP2 zien meer heil in een hervatting van het overleg met Po"
            "stNL aanstaande woensdag.</p>\n\t\t\t\t\t\t\t\t<p>De drie bonden vinden het ook een brug "
            "te ver om juist in de drukke periode rond kerst en oud en nieuw acties te organi"
            "seren. Die kunnen PostNL dusdanig hard raken dat ook de werkgelegenheid bij het "
            "bedrijf in gevaar komt, waarschuwen ze in een gezamenlijke brief aan hun leden.<"
            "/p>\n\t\t\t\t\t\t\t\n\t\t\t\t\t\t"
        )
        self.assertEqual(item["body_html"], expected_body)

    def test_extract_city_from_body(self):
        item = {
            "body_html": "NL<p>San Mateo (ANP) - FNV kondigt werkonderbrekingen aan bij PostNL,"
        }
        city = BelgaANPNewsMLOneFeedParser().extract_city(item)
        self.assertEqual(city, "San Mateo")

        item[
            "body_html"
        ] = "NL<p>San Mateo (ANP/RTL) - FNV kondigt werkonderbrekingen aan bij PostNL,"
        city = BelgaANPNewsMLOneFeedParser().extract_city(item)
        self.assertEqual(city, "San Mateo")
