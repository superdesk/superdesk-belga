from superdesk.tests import TestCase
import os
from belga.io.feed_parsers.belga_iptc7901 import BelgaIPTC7901FeedParser


class BaseBelgaIPTC7901FeedParserTestCase(TestCase):
    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test'}
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
        self.assertEqual(item["anpa_category"], [{'qcode': 'I'}])
        self.assertListEqual(item["subject"], [{'qcode': 'POLITICS', 'name': 'POLITICS', 'scheme': 'news_products'},
                                               {'qcode': 'NEWS', 'name': 'NEWS', 'scheme': 'news_services'}])
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["byline"], "Helen Maguire, dpa")
        expected_body = \
            (
                '<p> </p><p>Britain could unilaterally decide not to leave the</p><p>European Uni'
                "on, the bloc's top court ruled on Monday, one day before</p><p>British lawmakers"
                ' are due to vote on the Brexit deal London has</p><p>struck with Brussels.</p><p'
                '></p><p>British politicians campaigning for a second referendum on Brexit</p><p>'
                'hailed the ruling as a boost for their cause, while some commentators</p><p>said'
                ' it could help Conservative Prime Minister Theresa May in her bid</p><p>to scare'
                ' rebel lawmakers away from voting against her deal.</p><p></p><p>The decision to'
                ' reverse Brexit would be a "sovereign" choice, the</p><p>European Court of Justi'
                'ce (ECJ) argued. Subjecting it to the approval</p><p>of other member states coul'
                'd end up forcing Britain to leave "against</p><p>its will," the court said in a '
                'statement.</p><p></p><p>British Foreign Secretary Jeremy Hunt dismissed the ruli'
                'ng, but</p><p>co-litigant Alyn Smith, a Scottish National Party (SNP) member of '
                'the</p><p>European Parliament, hailed it as a "huge win."</p><p></p><p>"I think '
                "it's irrelevant because just imagine how the 52 per cent of</p><p>the country wh"
                'o voted for Brexit would feel if any British government</p><p>were to delay leav'
                'ing the EU on March 29," Hunt told reporters in</p><p>Brussels.</p><p></p><p>"I '
                "think people would be shocked and very angry and it's certainly</p><p>not the in"
                'tention of the government," Hunt said.</p><p></p><p>Smith said taking the case t'
                'o the ECJ had "worked better than [the</p><p>SNP] could have hoped for."</p><p><'
                '/p><p>"A bright light has switched on above an exit sign," he said.</p><p></p><p'
                '>Joanna Cherry, an SNP member of the British parliament, said she was</p><p>plea'
                'sed that the ECJ had "provided this lifeline to the UK parliament</p><p>at this '
                'moment of crisis."</p><p></p><p>Liberal Democrat Brexit spokesman Tom Brake, who'
                ' helped bring the</p><p>case, said the ruling enabled the government to prevent '
                'a "chaotic</p><p>no-deal" Brexit and helped bring the possibility of a second</p'
                '><p>referendum "closer than ever."</p><p></p><p>The petitioners, who initially b'
                'rought the case before the Scottish</p><p>courts, had asked whether Britain can '
                'reverse its decision to trigger</p><p>the Brexit countdown, arguing that lawmake'
                'rs should be aware of all</p><p>options when they cast their Brexit votes.</p><p'
                '></p><p>Britain is due to leave the EU on March 29, 2019, two years after May</p'
                '><p>invoked Article 50 of the EU treaty, triggering the countdown.</p><p></p><p>'
                "May's government had sought to have the case dismissed, arguing that</p><p>the q"
                'uestion is purely hypothetical since it has no intention of</p><p>reversing Brex'
                'it.</p><p></p><p>But the Luxembourg-based judges rejected that argument.</p><p><'
                '/p><p>The ruling is broadly in line with the recommendations of Advocate</p><p>G'
                'eneral Manuel Campos Sanchez-Bordona, a top advisor to the court.</p><p></p><p>I'
                't could, however, open the way for disgruntled member states to</p><p>trigger Ar'
                'ticle 50 in future, in the hope of negotiating better</p><p>membership terms.</p'
                '><p></p><p>The British parliament is due to vote on Tuesday on the withdrawal</p'
                '><p>agreement and a political declaration outlining joint ambitions for</p><p>th'
                'e future relationship between Britain and the EU.</p><p></p><p>May has faced an '
                'uphill struggle to sell the deal to parliament.</p><p>Hardline eurosceptics fear'
                ' that it binds Britain too closely to the</p><p>EU, while those in favour of a s'
                'ofter Brexit say it goes too far.</p><p></p><p># Notebook</p><p></p><p>## Note t'
                'o editors</p><p>- Adds reaction from British minister, opposition</p><p></p><p>#'
                '# Internet links</p><p>- [ECJ press release](http://dpaq.de/IcoPF)</p><p>- [Alyn'
                ' Smith, Joanna Cherry statement](http://dpaq.de/X9BxF)</p><p>- [Tom Brake statem'
                'ent via Twitter](http://dpaq.de/dWWFK)</p><p></p><p>* * * *</p><p></p>'
            )
        self.assertEqual(item["body_html"], expected_body)


class ATSBelgaFeedParserTestCase(DPABelgaFeedParserTestCase):
    filename = 'ats.txt'

    def test_content(self):
        item = self.item
        self.assertEqual(item["ingest_provider_sequence"], "037")
        # self.assertEqual(item["slugline"], "Notes de frais GE")
        self.assertEqual(item["anpa_category"], [{'qcode': 'EC'}])
        self.assertListEqual(item["subject"], [{'qcode': 'ECONOMY', 'name': 'ECONOMY', 'scheme': 'news_products'},
                                               {'qcode': 'NEWS', 'name': 'NEWS', 'scheme': 'news_services'}])
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["original_source"], "bsf")
        expected_headline = \
            (
                "Notes de frais GE: \r\nL'affaire des notes de frais a marquÃ© l'exÃ©cutif de la Vi"
                'lle'
            )
        self.assertEqual(item["headline"], expected_headline)
        self.assertEqual(item["priority"], 4)
        self.assertEqual(item["word_count"], 174)
        expected_body = \
            (
                '<p> GenÃ¨ve (ats) Le scandale causÃ© par les notes de frais  considÃ©rables de c'
                'ertains conseillers administratifs de la Ville de  GenÃ¨ve a provoquÃ© un sÃ©ism'
                "e au sein de l'exÃ©cutif municipal. Â«Le  rapport de confiance a Ã©tÃ© Ã©branlÃ©"
                'Â», a admis le maire de la Ville  de GenÃ¨ve Sami Kanaan, dans une interview lun'
                'di Ã\xa0 la Tribune de  GenÃ¨ve.   Â«Il y aura un avant et un aprÃ¨s rapport de la '
                "Cour des comptesÂ»,  souligne l'Ã©lu socialiste. Ce dernier dit avoir Â«Ã©tÃ© ch"
                'oquÃ© de  dÃ©couvrir certaines pratiques trÃ¨s discutablesÂ». Le magistrat  appe'
                'lle maintenant Ã\xa0 tourner la page, afin de Â«repartir sur des  bases sainesÂ».  '
                " Une quinzaine de textes liÃ©s Ã\xa0 l'affaire ont Ã©tÃ© dÃ©posÃ©s au  Conseil muni"
                'cipal. Le dÃ©libÃ©ratif devra les traiter le plus  rapidement, estime M. Kanaan,'
                " dans le but Â«de ne pas handicaper  d'autres dossiers importantsÂ». Selon le ma"
                'ire de GenÃ¨ve, ce travail  devrait Ãªtre fait Â«dans les quatre Ã\xa0 six prochain'
                'es semainesÂ».   Des mesures ont dÃ©jÃ\xa0 Ã©tÃ© prises. Un dispositif des frais a '
                'Ã©tÃ©  crÃ©Ã©. Une charte des valeurs sera instaurÃ©e, qui complÃ©tera une  vers'
                "ion actualisÃ©e de la rÃ©glementation sur les frais. Â«L'enjeu, ce  ne sont pas "
                'seulement les rÃ¨gles, mais aussi les attitudes et les  comportements face Ã\xa0 el'
                'lesÂ», note le maire.   (SDA\\/mf ba)   </p>'
            )
        self.assertEqual(item["body_html"], expected_body)
