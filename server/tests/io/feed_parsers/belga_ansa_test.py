from belga.io.feed_parsers.belga_ansa import BelgaANSAFeedParser
import os
from lxml import etree
from tests import TestCase


class BelgaANSATestCase(TestCase):
    filename = "ansa_belga.xml"

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, "../fixtures", self.filename))
        provider = {"name": "test"}
        with open(fixture, "rb") as f:
            parser = BelgaANSAFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaANSAFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item
        item["subject"].sort(key=lambda i: i["scheme"])
        expected_subjects = [
            {
                "qcode": "04000000",
                "name": "economy, business and finance",
                "scheme": "iptc_subject_codes",
            },
            {
                "name": "English Media Service",
                "qcode": "English Media Service",
                "parent": "NEWS",
                "scheme": "services-products",
            },
        ]
        expected_subjects.sort(key=lambda i: i["scheme"])
        self.assertEqual(item["subject"], expected_subjects)
        self.assertEqual(item["guid"], "XAM22192010243_AMZ_X083")
        self.assertEqual(item["priority"], 5)
        self.assertEqual(item["keywords"], ["Gazprom cut its flow of gas into Italy"])
        self.assertEqual(item["type"], "text")
        self.assertEqual(str(item["firstcreated"]), "2022-07-11 18:33:00+01:00")
        self.assertEqual(str(item["versioncreated"]), "2022-07-11 18:33:00+01:00")
        self.assertEqual(item["uri"], "XAM22192010243_AMZ_X083")
        self.assertEqual(item["urgency"], 5)
        self.assertEqual(
            item["dateline"],
            {
                "located": {
                    "city_code": "ROME",
                    "city": "ROME",
                    "tz": "UTC",
                    "dateline": "city",
                }
            },
        )
        self.assertEqual(
            item["headline"], "Gazprom cuts Italy gas supplies by a third"
        ),
        self.assertEqual(
            item["byline"], "Situation serious, ready for all scenarios says EC"
        )
        self.assertEqual(item["abstract"], "")
        self.assertEqual(item["word_count"], "9912")
        self.assertEqual(
            item["authors"],
            [
                {
                    "_id": ["GEE", "AUTHOR"],
                    "role": "AUTHOR",
                    "name": "AUTHOR",
                    "sub_label": "GEE",
                },
                {
                    "_id": ["", "WRITER"],
                    "role": "WRITER",
                    "name": "WRITER",
                    "sub_label": "",
                },
            ],
        )
        self.assertEqual(item["source"], "ANSA")
        self.assertEqual(item["anpa_category"], [{"qcode": "ALR", "name": "ALR"}])

        expected_body = (
            "<p>\n                    \n                    (ANSA) - ROME, JUL 11 - "
            "Russian energy giant Gazprom on\n                    Monday cut its gas sup"
            "plies to Italy by a third, Italian fuels\n                    giant Eni said."
            "\n                </p>"
        )
        self.assertEqual(item["body_html"], expected_body)
