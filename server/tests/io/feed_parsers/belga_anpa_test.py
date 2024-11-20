import os

import settings
from superdesk import config

from belga.io.feed_parsers.belga_anpa import BelgaANPAFeedParser
from tests import TestCase


class BaseBelgaANPAFeedParserTestCase(TestCase):
    def setUp(self):
        for key in dir(settings):
            if key.isupper():
                setattr(config, key, getattr(settings, key))
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, "../fixtures", self.filename))
        provider = {"name": "test"}
        parser = BelgaANPAFeedParser()
        self.item = parser.parse(fixture, provider)


class KyodoBelgaFeedParserTestCase(BaseBelgaANPAFeedParserTestCase):
    filename = "kyodo.txt"

    def test_content(self):
        item = self.item
        self.assertEqual(item["language"], "en")
        self.assertEqual(item["slugline"], None)
        self.assertEqual(item["keywords"], [])
        self.assertEqual(item["anpa_take_key"], "'s-Cup")
        self.assertEqual(item["word_count"], 344)
        self.assertEqual(item["firstcreated"].isoformat(), "2018-12-09T12:18:00+00:00")
        self.assertEqual(
            item["headline"],
            "Soccer: Urawa Reds claim 7th Emperor's Cup by beating Vegalta Sendai",
        )
        self.assertEqual(
            item["versioncreated"].isoformat(), "2018-12-09T12:18:00+00:00"
        )
        self.assertEqual(item["priority"], 2)
        self.assertEqual(item["anpa_category"], [{"qcode": "S"}])
        self.assertEqual(item["format"], "preserved")
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["extra"], {"city": "SAITAMA"})
        self.assertListEqual(
            item["subject"],
            [
                {
                    "name": "NEWS/SPORTS",
                    "parent": "NEWS",
                    "qcode": "NEWS/SPORTS",
                    "scheme": "services-products",
                },
                {"name": "KYODO", "qcode": "KYODO", "scheme": "sources"},
                {"name": "default", "qcode": "default", "scheme": "distribution"},
            ],
        )
        self.assertEqual(item["priority"], 2)
        expected_body = (
            "<p>     SAITAMA, Japan, Dec. 9 Kyodo - Urawa Reds claimed their seventh </p><p>E"
            "mperor's Cup on Sunday after defeating fellow J-League top division </p><p>side "
            "Vegalta Sendai 1-0 at Saitama Stadium.</p><p>     Midfielder Tomoya Ugajin score"
            "d the only goal of the night in </p><p>the 13th minute to lead Urawa to their fi"
            "rst title in 12 tournaments, </p><p>as well as an automatic qualification for th"
            "e 2019 Asian Champions </p><p>League group stage.</p><p>     Both sides fought a"
            "ggressively from beginning to end, but </p><p>Vegalta failed to make use of the "
            "several chances they had and were </p><p>unable to take home their first major t"
            "itle.</p><p>     Following a corner kick, the 30-year-old Ugajin drove in the </"
            "p><p>winner from outside the penalty area following a headed clearance </p><p>fr"
            'om Vegalta forward Gakuto Notsuda.</p><p>     "We have been training for that si'
            "tuation over and over so I'm </p><p>relieved I was able to score. I want to comp"
            'liment myself for that," </p><p>Ugajin said.</p><p>     Urawa had won back-to-ba'
            "ck Emperor's Cup titles in 2005 and </p><p>2006, but lost to Gamba Osaka in 2015"
            " when they made their most </p><p>recent appearance in a final. The 2017 Asian C"
            "hampions League winners </p><p>had finished fifth in the J-League this season.</"
            "p><p>     \"I'm delighted to be able to win in front of our fans here. I </p><p>w"
            'anted to give a present to the supporters," said Urawa head coach </p><p>Oswaldo'
            " Oliveira, who took the job this season.</p><p>     Sendai, playing in their fir"
            "st Emperor's Cup final, had several </p><p>chances to equalize but were unable t"
            "o take them in front of the </p><p>sellout crowd.</p><p>     The side, who finis"
            "hed 11th in J1, had not won a league match </p><p>against the Reds since 2015, a"
            "nd has never won against them at </p><p>Urawa's home Saitama Stadium.</p><p>    "
            " Notsuda shot over the crossbar from a free kick in the 60th </p><p>minute, and "
            "Urawa keeper Shusaku Nishikawa caught Kazuki Oiwa's shot </p><p>in the 77th and "
            "saved another effort from Notsuda four minutes later.</p><p>     Three Urawa pla"
            "yers -- midfielder Takuya Aoki and forwards </p><p>Shinzo Koroki and Yuki Muto -"
            "- returned to the starting lineup to </p><p>lead the team's attack. They came of"
            "f during Wednesday's semifinal </p><p>against Kashima Antlers when they sustaine"
            "d injuries.</p>"
        )
        self.assertEqual(item["body_html"], expected_body)
