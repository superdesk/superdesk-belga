import time

from tests import TestCase


dataset = {
    "title": "'Duizenden banen weg bij Britse super Tesco'",
    "title_detail": {
        "type": "text/plain",
        "language": "NL",
        "base": "",
        "value": "'Duizenden banen weg bij Britse super Tesco'",
    },
    "links": [
        {
            "href": "https://playlist.anp.nl/portal/news/item/belga-eco/ANPX270119007",
            "rel": "alternate",
            "type": "text/html",
        }
    ],
    "link": "https://playlist.anp.nl/portal/news/item/belga-eco/ANPX270119007",
    "id": "http://nofollow.anp.nl/portal/news/item/belga-eco/ANPX270119007",
    "guidislink": False,
    "published": "2019-01-27T07:15:14+01:00",
    "published_parsed": time.struct_time((2019, 1, 27, 6, 15, 14, 6, 27, 0)),
    "updated": "2019-01-27T07:15:16+01:00",
    "updated_parsed": time.struct_time((2019, 1, 27, 6, 15, 16, 6, 27, 0)),
    "tags": [{"term": "ECO", "scheme": None, "label": "ECO"}],
    "authors": [{"name": "Marijn Wellink (wki)"}],
    "author_detail": {"name": "Marijn Wellink (wki)"},
    "author": "Marijn Wellink (wki)",
    "summary": "LONDEN (ANP) - Supermarktketen Tesco zet het mes in 15.000 banen in Groot-Britta"
    "nnië. Dat schrijft Mail on Sunday op basis van ingewijden. Het zou daarmee een v"
    "eel grotere ingreep zijn dan waar andere Britse media de afgelopen dagen op spec"
    "uleerden, van mogelijk honderden tot wat meer dan duizend banen.",
    "summary_detail": {
        "type": "text/plain",
        "language": "NL",
        "base": "",
        "value": "LONDEN (ANP) - Supermarktketen Tesco zet het mes in 15.000 banen in Groot-Britta"
        "nnië. Dat schrijft Mail on Sunday op basis van ingewijden. Het zou daarmee een v"
        "eel grotere ingreep zijn dan waar andere Britse media de afgelopen dagen op spec"
        "uleerden, van mogelijk honderden tot wat meer dan duizend banen.",
    },
    "content": [
        {
            "type": "application/xhtml+xml",
            "language": "NL",
            "base": "",
            "value": "<p>LONDEN (ANP) - Supermarktketen Tesco zet het mes in 15.000 banen in Groot-Bri"
            "ttannië. Dat schrijft Mail on Sunday op basis van ingewijden. Het zou daarmee ee"
            "n veel grotere ingreep zijn dan waar andere Britse media de afgelopen dagen op s"
            "peculeerden, van mogelijk honderden tot wat meer dan duizend banen.</p><p>De reo"
            "rganisatie is onderdeel van een plan om in 2020 zo'n 1,5 miljard pond, ruim 1,7 "
            "miljard euro, te besparen. Onder meer de vlees-, vis- en delicatessenafdelingen "
            "zullen niet meer standaard bezet worden met specialisten en ook de bemande perso"
            "neelskantines en -restaurants gaan dicht. Tesco is de grootste supermarktketen v"
            "an het Verenigd Koninkrijk met 732 filialen en heeft verder veel ondersteunende-"
            " en klantenservice-afdelingen.</p><p>Tesco is opgericht in 1919 en heeft wereldw"
            "ijd 3400 filialen. Het bedrijf heeft een personeelsbestand van circa 460.000 waa"
            "rvan zo'n 300.000 medewerkers actief zijn in Groot-Brittannië. Tesco is verder a"
            "anwezig in landen als India, Polen, Tsjechië en Hongarije. Een woordvoerder van "
            "Tesco wilde het bericht tegenover de krant niet bevestigen. ,,We zijn altijd op "
            "zoek naar manieren om ons bedrijf eenvoudiger en efficiënter te runnen. Wanneer "
            "we veranderingen aanbrengen in ons bedrijf, zijn collega's altijd de eersten die"
            " het weten'', aldus de zegsman.</p>",
        }
    ],
    "anp_priority": "3",
    "anp_keywords": "",
    "anp_copyright": "© 2019 ANP. Alle auteursrechten en databankrechten voorbehouden. All copyrights "
    "and database rights reserved.",
    "anp_provider": "ANP",
    "anp_version": "1",
    "anp_country": "NEDERLAND(NL)",
    "anp_charcount": "1294",
    "anp_wordcount": "197",
    "anp_lang": "nl",
    "anp_updated": "2019-01-27T07:15:14+01:00",
}


class RssBelgaIngestServiceTest(TestCase):
    """Base class for RSSFeedingService tests."""

    def setUpForChildren(self):
        super().setUpForChildren()
        try:
            from belga.io.feeding_services.rss_belga import RSSBelgaFeedingService
        except ImportError:
            # a missing class should result in a test failure, not in an error
            self.fail("Could not import class under test (RSSFeedingService).")
        else:
            self.instance = RSSBelgaFeedingService()


class RSSBelgaTestCase(RssBelgaIngestServiceTest):
    """Tests for the _create_item() method."""

    def test_creates_item_from_given_data(self):
        self.maxDiff = None
        data = dataset

        item = self.instance._create_item(data, source="source")
        self.assertEqual(item["provider_id"], "ANP")
        self.assertEqual(item["char_count"], "1294")
        self.assertEqual(item["location"], {"city": None, "country": "NEDERLAND(NL)"})
        self.assertEqual(item["codes"], None)
        self.assertEqual(
            item["copyright"],
            "© 2019 ANP. Alle auteursrechten en databankrechten voorbehouden. All copyrights "
            "and database rights reserved.",
        )
        self.assertEqual(item["financial"], None)
        self.assertEqual(item["keywords"], [""])
        self.assertEqual(item["language"], "nl")
        self.assertEqual(item["priority"], "3")
        self.assertEqual(item["updated_date"], "2019-01-27T07:15:14+01:00")
        self.assertEqual(item["version"], "1")
        self.assertEqual(item["word_count"], "197")
        self.assertEqual(
            item["authors"],
            [
                {
                    "uri": None,
                    "parent": None,
                    "name": "Marijn Wellink (wki)",
                    "role": None,
                    "jobtitle": None,
                }
            ],
        )
