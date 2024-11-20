import os

from belga.io.feed_parsers.belga_iptc7901 import BelgaIPTC7901FeedParser
from tests import TestCase


class BaseBelgaIPTC7901FeedParserTestCase(TestCase):
    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, "../fixtures", self.filename))
        provider = {"name": "test"}
        parser = BelgaIPTC7901FeedParser()
        self.assertTrue(BelgaIPTC7901FeedParser().can_parse(fixture))
        self.item = parser.parse(fixture, provider)


class DPABelgaFeedParserTestCase(BaseBelgaIPTC7901FeedParserTestCase):
    filename = "dpa.txt"

    def test_content(self):
        item = self.item
        self.assertEqual(item["word_count"], 510)
        self.assertEqual(
            item["headline"],
            "Top EU court: Britain can unilaterally reverse Brexit decision\n",
        )
        self.assertEqual(item["original_source"], "eca")
        self.assertEqual(item["ingest_provider_sequence"], "00075")
        self.assertEqual(item["priority"], 3)
        self.assertEqual(item["anpa_take_key"], "2ND LEAD 3RD NET")
        self.assertEqual(item["slugline"], None)
        self.assertEqual(item["keywords"], [])
        self.assertEqual(item["anpa_category"], [{"qcode": "I"}])
        self.assertListEqual(
            item["subject"],
            [
                {
                    "name": "NEWS/POLITICS",
                    "parent": "NEWS",
                    "qcode": "NEWS/POLITICS",
                    "scheme": "services-products",
                },
                {"name": "DPA", "qcode": "DPA", "scheme": "sources"},
                {"name": "default", "qcode": "default", "scheme": "distribution"},
            ],
        )
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["byline"], "Helen Maguire, dpa")
        expected_body = (
            "<p> </p><p>Britain could unilaterally decide not to leave the</p><p>European Uni"
            "on, the bloc's top court ruled on Monday, one day before</p><p>British lawmakers"
            " are due to vote on the Brexit deal London has</p><p>struck with Brussels.</p><p"
            "></p><p>British politicians campaigning for a second referendum on Brexit</p><p>"
            "hailed the ruling as a boost for their cause, while some commentators</p><p>said"
            " it could help Conservative Prime Minister Theresa May in her bid</p><p>to scare"
            " rebel lawmakers away from voting against her deal.</p><p></p><p>The decision to"
            ' reverse Brexit would be a "sovereign" choice, the</p><p>European Court of Justi'
            "ce (ECJ) argued. Subjecting it to the approval</p><p>of other member states coul"
            'd end up forcing Britain to leave "against</p><p>its will," the court said in a '
            "statement.</p><p></p><p>British Foreign Secretary Jeremy Hunt dismissed the ruli"
            "ng, but</p><p>co-litigant Alyn Smith, a Scottish National Party (SNP) member of "
            'the</p><p>European Parliament, hailed it as a "huge win."</p><p></p><p>"I think '
            "it's irrelevant because just imagine how the 52 per cent of</p><p>the country wh"
            "o voted for Brexit would feel if any British government</p><p>were to delay leav"
            'ing the EU on March 29," Hunt told reporters in</p><p>Brussels.</p><p></p><p>"I '
            "think people would be shocked and very angry and it's certainly</p><p>not the in"
            'tention of the government," Hunt said.</p><p></p><p>Smith said taking the case t'
            'o the ECJ had "worked better than [the</p><p>SNP] could have hoped for."</p><p><'
            '/p><p>"A bright light has switched on above an exit sign," he said.</p><p></p><p'
            ">Joanna Cherry, an SNP member of the British parliament, said she was</p><p>plea"
            'sed that the ECJ had "provided this lifeline to the UK parliament</p><p>at this '
            'moment of crisis."</p><p></p><p>Liberal Democrat Brexit spokesman Tom Brake, who'
            " helped bring the</p><p>case, said the ruling enabled the government to prevent "
            'a "chaotic</p><p>no-deal" Brexit and helped bring the possibility of a second</p'
            '><p>referendum "closer than ever."</p><p></p><p>The petitioners, who initially b'
            "rought the case before the Scottish</p><p>courts, had asked whether Britain can "
            "reverse its decision to trigger</p><p>the Brexit countdown, arguing that lawmake"
            "rs should be aware of all</p><p>options when they cast their Brexit votes.</p><p"
            "></p><p>Britain is due to leave the EU on March 29, 2019, two years after May</p"
            "><p>invoked Article 50 of the EU treaty, triggering the countdown.</p><p></p><p>"
            "May's government had sought to have the case dismissed, arguing that</p><p>the q"
            "uestion is purely hypothetical since it has no intention of</p><p>reversing Brex"
            "it.</p><p></p><p>But the Luxembourg-based judges rejected that argument.</p><p><"
            "/p><p>The ruling is broadly in line with the recommendations of Advocate</p><p>G"
            "eneral Manuel Campos Sanchez-Bordona, a top advisor to the court.</p><p></p><p>I"
            "t could, however, open the way for disgruntled member states to</p><p>trigger Ar"
            "ticle 50 in future, in the hope of negotiating better</p><p>membership terms.</p"
            "><p></p><p>The British parliament is due to vote on Tuesday on the withdrawal</p"
            "><p>agreement and a political declaration outlining joint ambitions for</p><p>th"
            "e future relationship between Britain and the EU.</p><p></p><p>May has faced an "
            "uphill struggle to sell the deal to parliament.</p><p>Hardline eurosceptics fear"
            " that it binds Britain too closely to the</p><p>EU, while those in favour of a s"
            "ofter Brexit say it goes too far.</p><p></p><p># Notebook</p><p></p><p>## Note t"
            "o editors</p><p>- Adds reaction from British minister, opposition</p><p></p><p>#"
            "# Internet links</p><p>- [ECJ press release](http://dpaq.de/IcoPF)</p><p>- [Alyn"
            " Smith, Joanna Cherry statement](http://dpaq.de/X9BxF)</p><p>- [Tom Brake statem"
            "ent via Twitter](http://dpaq.de/dWWFK)</p><p></p><p>* * * *</p><p></p>"
        )
        self.assertEqual(item["body_html"], expected_body)


class ATSBelgaFeedParserTestCase(BaseBelgaIPTC7901FeedParserTestCase):
    filename = "ats.txt"

    def test_content(self):
        item = self.item
        self.assertEqual(item["slugline"], None)
        self.assertEqual(item["keywords"], [])
        self.assertEqual(item["ingest_provider_sequence"], "025")
        self.assertEqual(item["anpa_category"], [{"qcode": "EC"}])
        self.assertListEqual(
            item["subject"],
            [
                {
                    "name": "NEWS/ECONOMY",
                    "parent": "NEWS",
                    "qcode": "NEWS/ECONOMY",
                    "scheme": "services-products",
                },
                {"name": "ATS", "qcode": "ATS", "scheme": "sources"},
                {"name": "default", "qcode": "default", "scheme": "distribution"},
            ],
        )
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["language"], "fr")
        self.assertEqual(item["extra"], {"city": "Paris"})
        self.assertEqual(item["original_source"], "bsf")
        self.assertEqual(
            item["headline"],
            "Gilets jaunes: une «catastrophe pour notre économie» (Le Maire) =",
        )
        self.assertEqual(item["priority"], 3)
        self.assertEqual(item["word_count"], 121)
        expected_body = (
            "<p>«gilets jaunes» sont une «catastrophe» pour l'économie, a estimé  </p>"
            "<p>dimanche le ministre de l'Economie. Bruno Le Maire a été jusqu'à  </p>"
            "<p>parler d'une «crise de la nation».  </p><p>  </p>"
            "<p>   «C'est une catastrophe pour le commerce, c'est une catastrophe  </p>"
            "<p>pour notre économie», a déclaré à la presse le ministre, lors d'une  </p>"
            "<p>visite aux commerçants à Paris au lendemain de nouvelles violences  </p>"
            "<p>lors de la quatrième journée de mobilisation. Il a énuméré «une  </p>"
            "<p>crise sociale», «une crise démocratique» et «une crise de la  </p><p>nation».  </p><p>  </p>"
            "<p>   De son côté, Ségolène Royal, ancienne finaliste de la  </p>"
            "<p>présidentielle de 2007, a fustigé dimanche des «décisions mal  </p>"
            "<p>préparées» par le gouvernement ayant conduit, selon elle, à la  </p>"
            "<p>crise des «gilets jaunes» en raison de leur impact sur le pouvoir  </p>"
            "<p>d'achat.  </p><p>  </p><p>(SDA\\/sj)  </p><p>  </p>"
            "<p>\x03091223 dec 18 </p><p> </p><p> </p><p>\x04 </p>"
        )
        self.assertEqual(item["body_html"], expected_body)
