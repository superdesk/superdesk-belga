from superdesk.tests import TestCase
import os
from belga.io.feed_parsers.belga_iptc7901 import BelgaIPTC7901FeedParser


class BaseBelgaIPTC7901FeedParserTestCase(TestCase):
    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'Test'}
        parser = BelgaIPTC7901FeedParser()
        self.assertTrue(BelgaIPTC7901FeedParser().can_parse(fixture))
        self.item = parser.parse(fixture, provider)


class DPABelgaFeedParserTestCase(BaseBelgaIPTC7901FeedParserTestCase):
    filename = 'dpa.txt'

    def test_content(self):
        item = self.item
        self.assertEqual(item["word_count"], 510)
        self.assertEqual(item["headline"], "Top EU court: Britain can unilaterally reverse Brexit decision\n")
        self.assertEqual(item["original_source"], "eca")
        self.assertEqual(item["ingest_provider_sequence"], "00075")
        self.assertEqual(item["priority"], 3)
        self.assertEqual(item["anpa_take_key"], "2ND LEAD 3RD NET")
        self.assertEqual(item["slugline"], "/politics/Britain/EU/Brexit/justice")
        self.assertEqual(item["anpa_category"], [{'qcode': 'i'}])
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["byline"], "Helen Maguire, dpa ")
        expected_body = \
            (
                '<p>Luxembourg (dpa) - Britain could unilaterally decide not to leave the</p><p>E'
                "uropean Union, the bloc's top court ruled on Monday, one day before</p><p>Britis"
                'h lawmakers are due to vote on the Brexit deal London has</p><p>struck with Brus'
                'sels.</p><p></p><p>British politicians campaigning for a second referendum on Br'
                'exit</p><p>hailed the ruling as a boost for their cause, while some commentators'
                '</p><p>said it could help Conservative Prime Minister Theresa May in her bid</p>'
                '<p>to scare rebel lawmakers away from voting against her deal.</p><p></p><p>The '
                'decision to reverse Brexit would be a "sovereign" choice, the</p><p>European Cou'
                'rt of Justice (ECJ) argued. Subjecting it to the approval</p><p>of other member '
                'states could end up forcing Britain to leave "against</p><p>its will," the court'
                ' said in a statement.</p><p></p><p>British Foreign Secretary Jeremy Hunt dismiss'
                'ed the ruling, but</p><p>co-litigant Alyn Smith, a Scottish National Party (SNP)'
                ' member of the</p><p>European Parliament, hailed it as a "huge win."</p><p></p><'
                'p>"I think it\'s irrelevant because just imagine how the 52 per cent of</p><p>the'
                ' country who voted for Brexit would feel if any British government</p><p>were to'
                ' delay leaving the EU on March 29," Hunt told reporters in</p><p>Brussels.</p><p'
                '></p><p>"I think people would be shocked and very angry and it\'s certainly</p><p'
                '>not the intention of the government," Hunt said.</p><p></p><p>Smith said taking'
                ' the case to the ECJ had "worked better than [the</p><p>SNP] could have hoped fo'
                'r."</p><p></p><p>"A bright light has switched on above an exit sign," he said.</'
                'p><p></p><p>Joanna Cherry, an SNP member of the British parliament, said she was'
                '</p><p>pleased that the ECJ had "provided this lifeline to the UK parliament</p>'
                '<p>at this moment of crisis."</p><p></p><p>Liberal Democrat Brexit spokesman Tom'
                ' Brake, who helped bring the</p><p>case, said the ruling enabled the government '
                'to prevent a "chaotic</p><p>no-deal" Brexit and helped bring the possibility of '
                'a second</p><p>referendum "closer than ever."</p><p></p><p>The petitioners, who '
                'initially brought the case before the Scottish</p><p>courts, had asked whether B'
                'ritain can reverse its decision to trigger</p><p>the Brexit countdown, arguing t'
                'hat lawmakers should be aware of all</p><p>options when they cast their Brexit v'
                'otes.</p><p></p><p>Britain is due to leave the EU on March 29, 2019, two years a'
                'fter May</p><p>invoked Article 50 of the EU treaty, triggering the countdown.</p'
                "><p></p><p>May's government had sought to have the case dismissed, arguing that<"
                '/p><p>the question is purely hypothetical since it has no intention of</p><p>rev'
                'ersing Brexit.</p><p></p><p>But the Luxembourg-based judges rejected that argume'
                'nt.</p><p></p><p>The ruling is broadly in line with the recommendations of Advoc'
                'ate</p><p>General Manuel Campos Sanchez-Bordona, a top advisor to the court.</p>'
                '<p></p><p>It could, however, open the way for disgruntled member states to</p><p'
                '>trigger Article 50 in future, in the hope of negotiating better</p><p>membershi'
                'p terms.</p><p></p><p>The British parliament is due to vote on Tuesday on the wi'
                'thdrawal</p><p>agreement and a political declaration outlining joint ambitions f'
                'or</p><p>the future relationship between Britain and the EU.</p><p></p><p>May ha'
                's faced an uphill struggle to sell the deal to parliament.</p><p>Hardline eurosc'
                'eptics fear that it binds Britain too closely to the</p><p>EU, while those in fa'
                'vour of a softer Brexit say it goes too far.</p><p></p><p># Notebook</p><p></p><'
                'p>## Note to editors</p><p>- Adds reaction from British minister, opposition</p>'
                '<p></p><p>## Internet links</p><p>- [ECJ press release](http://dpaq.de/IcoPF)</p'
                '><p>- [Alyn Smith, Joanna Cherry statement](http://dpaq.de/X9BxF)</p><p>- [Tom B'
                'rake statement via Twitter](http://dpaq.de/dWWFK)</p><p></p><p>* * * *</p><p></p>'
            )
        self.assertEqual(item["body_html"], expected_body)


class ATSBelgaFeedParserTestCase(BaseBelgaIPTC7901FeedParserTestCase):
    filename = 'ats.txt'

    def test_content(self):
        item = self.item
        self.assertEqual(item["ingest_provider_sequence"], "037")
        self.assertEqual(item["slugline"], "Notes de frais GE")
        self.assertEqual(item["anpa_category"], [{'qcode': 'su'}])
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["original_source"], "bsf")
        expected_headline = \
            (
                "Notes de frais GE: \r\nL'affaire des notes de frais a marquÃ© l'exÃ©cutif de la Vi"
                'lle\n'
            )
        self.assertEqual(item["headline"], expected_headline)
        self.assertEqual(item["priority"], 4)
        self.assertEqual(item["word_count"], 174)
        expected_body = \
            (
                '<p>GenÃ¨ve (ats) Le scandale causÃ© par les notes de frais  considÃ©rables de ce'
                'rtains conseillers administratifs de la Ville de  GenÃ¨ve a provoquÃ© un sÃ©isme'
                " au sein de l'exÃ©cutif municipal. Â«Le  rapport de confiance a Ã©tÃ© Ã©branlÃ©Â"
                '», a admis le maire de la Ville  de GenÃ¨ve Sami Kanaan, dans une interview lund'
                'i Ã\xa0 la Tribune de  GenÃ¨ve.   Â«Il y aura un avant et un aprÃ¨s rapport de la C'
                "our des comptesÂ»,  souligne l'Ã©lu socialiste. Ce dernier dit avoir Â«Ã©tÃ© cho"
                'quÃ© de  dÃ©couvrir certaines pratiques trÃ¨s discutablesÂ». Le magistrat  appel'
                'le maintenant Ã\xa0 tourner la page, afin de Â«repartir sur des  bases sainesÂ».   '
                "Une quinzaine de textes liÃ©s Ã\xa0 l'affaire ont Ã©tÃ© dÃ©posÃ©s au  Conseil munic"
                'ipal. Le dÃ©libÃ©ratif devra les traiter le plus  rapidement, estime M. Kanaan, '
                "dans le but Â«de ne pas handicaper  d'autres dossiers importantsÂ». Selon le mai"
                're de GenÃ¨ve, ce travail  devrait Ãªtre fait Â«dans les quatre Ã\xa0 six prochaine'
                's semainesÂ».   Des mesures ont dÃ©jÃ\xa0 Ã©tÃ© prises. Un dispositif des frais a Ã'
                '©tÃ©  crÃ©Ã©. Une charte des valeurs sera instaurÃ©e, qui complÃ©tera une  versi'
                "on actualisÃ©e de la rÃ©glementation sur les frais. Â«L'enjeu, ce  ne sont pas s"
                'eulement les rÃ¨gles, mais aussi les attitudes et les  comportements face Ã\xa0 ell'
                'esÂ», note le maire.   (SDA\\/mf ba)   </p>'

            )
        self.assertEqual(item["body_html"], expected_body)
