from belga.io.feed_parsers.belga_stt import BelgaSTTFeedParser
import os
from lxml import etree
from tests import TestCase


class BelgaSTTTestCase(TestCase):
    filename = "stt_belga.xml"

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, "../fixtures", self.filename))
        provider = {"name": "test"}
        with open(fixture, "rb") as f:
            parser = BelgaSTTFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_can_parse(self):
        self.assertTrue(BelgaSTTFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        item["subject"].sort(key=lambda i: i["scheme"])
        expected_subjects = [
            {"qcode": "14", "name": "Ulkomaat", "scheme": "sttdepartment"},
            {"qcode": "5", "scheme": "sttversion", "name": "Loppuversio"},
        ]
        expected_subjects.sort(key=lambda i: i["scheme"])
        self.assertEqual(item["subject"], expected_subjects)
        self.assertEqual(item["guid"], "urn:newsml:stt.fi::104917454:1")
        self.assertEqual(item["version"], "1")
        self.assertEqual(item["type"], "text")
        self.assertEqual(str(item["firstcreated"]), "2022-05-09 21:30:33+00:00")
        self.assertEqual(str(item["versioncreated"]), "2022-05-09 21:31:02+00:00")
        self.assertEqual(item["uri"], "urn:newsml:stt.fi::104917454")
        self.assertEqual(item["urgency"], 3)
        self.assertEqual(
            item["headline"],
            (
                "According to the Pentagon, Ukrainians have been transporte"
                "d to Russia against their will*** TRANSLATED ***"
            ),
        )
        self.assertEqual(item["slugline"], "")
        self.assertEqual(
            item["abstract"],
            (
                "The President of Ukraine has been saying for some time that Ukra"
                "inians have been taken to Russia.*** TRANSLATED ***"
            ),
        )
        self.assertEqual(item["uri"], "urn:newsml:stt.fi::104917454")
        self.assertEqual(item["genre"], [{"qcode": "1", "name": "Pääjuttu"}])
        self.assertEqual(item["authors"], [])
        self.assertEqual(item["source"], "STT")
        self.assertEqual(str(item["firstpublished"]), "2022-05-09 21:31:02+00:00")

        self.assertEqual(
            item["body_html"],
            (
                "<pre>According to the US Department of Defense, there hav"
                "e been indications in Ukraine that Ukrainians have been f"
                "orcibly deported to Russia. John Kirby, a spokesman for t"
                "he Pentagon, spoke about the matter.Kirby did not tell re"
                "porters how many possible Ukrainian camps are being talke"
                "d about. However, according to Kirby, there is evidence t"
                "hat the Ukrainians were transported to Russia against the"
                "ir will.Moscow has had 75 days to treat Ukrainians cruell"
                "y. Every time you think they can’t sink even lower anymor"
                "e, they prove you’re wrong, Kirby said.Ukrainian Presiden"
                "t Volodymyr Zelenskyi said as early as April that thousan"
                "ds of Ukrainians would have been deported to Russia. Accor"
                "ding to Ukrainian Ombudsman Lyudmyla Denisova, the number o"
                "f Ukrainians deported to Russia would have risen to more th"
                "an 1.19 million since the start of the war. The figure inclu"
                "des at least 200,000 children.</pre>"
            ),
        )
