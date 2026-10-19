import re
import unittest
from unittest.mock import patch, MagicMock

from superdesk.tests import TestCase

from belga.macros import auto_translate_to_en as macro
from belga.macros.helpers import belga_ai_translate


def _fake_translate(text, target_language="en"):
    """Prefix text with ``EN ``, keeping tags and wrapping plain text in ``<p>``."""
    if "<" in text and ">" in text:
        return re.sub(r">([^<]+)<", lambda m: ">EN " + m.group(1).strip() + "<", text)
    return "<p>EN " + text + "</p>"


SERVICES_PRODUCTS_CV = {
    "_id": "services-products",
    "display_name": "Packages",
    "type": "manageable",
    "unique_field": "qcode",
    "service": {"all": 1},
    "items": [
        {"name": "BIN", "qcode": "BIN", "is_active": True, "parent": None},
        {"name": "NEWS", "qcode": "NEWS", "is_active": True, "parent": None},
        {
            "name": "NEWS/GENERAL",
            "qcode": "NEWS/GENERAL",
            "is_active": True,
            "parent": "NEWS",
        },
        {
            "name": "NEWS/ECONOMY",
            "qcode": "NEWS/ECONOMY",
            "is_active": True,
            "parent": "NEWS",
        },
        {
            "name": "NEWS/POLITICS",
            "qcode": "NEWS/POLITICS",
            "is_active": True,
            "parent": "NEWS",
        },
        {
            "name": "NEWS/SPORTS",
            "qcode": "NEWS/SPORTS",
            "is_active": True,
            "parent": "NEWS",
        },
    ],
}

COUNTRY_CV = {
    "_id": "country",
    "display_name": "Countries keywords",
    "type": "manageable",
    "unique_field": "qcode",
    "service": {"all": 1},
    "items": [
        {
            "name": "Belgium",
            "qcode": "country_bel",
            "is_active": True,
            "translations": {"name": {"nl": "BELGIE", "fr": "BELGIQUE"}},
        }
    ],
}


def _services_product(qcode, parent):
    return {
        "name": qcode,
        "qcode": qcode,
        "parent": parent,
        "scheme": "services-products",
    }


class MapPackageQcodeTestCase(unittest.TestCase):
    def test_news_services(self):
        self.assertEqual(macro._map_package_qcode("BIN/ALG"), ("NEWS/GENERAL", "BIN"))
        self.assertEqual(macro._map_package_qcode("EXT/ECO"), ("NEWS/ECONOMY", "EXT"))
        self.assertEqual(macro._map_package_qcode("BTL/POL"), ("NEWS/POLITICS", "BTL"))
        self.assertEqual(macro._map_package_qcode("INT/GEN"), ("NEWS/GENERAL", "INT"))

    def test_sports_exception(self):
        self.assertEqual(macro._map_package_qcode("SPN/GEN"), ("NEWS/SPORTS", "SPN"))
        self.assertEqual(macro._map_package_qcode("SPF/ALG"), ("NEWS/SPORTS", "SPF"))

    def test_fallback(self):
        self.assertEqual(macro._map_package_qcode("BTL/EUR"), ("NEWS/GENERAL", "BTL"))
        self.assertEqual(
            macro._map_package_qcode("THEMA/ECO"), ("NEWS/GENERAL", "THEMA")
        )
        self.assertEqual(macro._map_package_qcode(""), ("NEWS/GENERAL", ""))


class AutoTranslateToEnMacroTestCase(unittest.TestCase):
    def test_macro_attributes(self):
        self.assertEqual(macro.name, "Auto translate to en")
        self.assertEqual(macro.label, "Auto translate to en")
        self.assertTrue(callable(macro.callback))
        self.assertEqual(macro.access_type, "frontend")
        self.assertEqual(macro.action_type, "direct")
        self.assertEqual(macro.replace_type, "editor_state")


class MapPackagesTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.app.data.insert("vocabularies", [SERVICES_PRODUCTS_CV, COUNTRY_CV])

    def test_bin_maps_to_news_general_and_belgium(self):
        item = {"subject": [_services_product("BIN/ALG", "BIN")]}
        macro.map_packages(item)

        services = [s for s in item["subject"] if s["scheme"] == "services-products"]
        countries = [s for s in item["subject"] if s["scheme"] == "country"]
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]["qcode"], "NEWS/GENERAL")
        self.assertEqual(len(countries), 1)
        self.assertEqual(countries[0]["qcode"], "country_bel")

    def test_ext_maps_to_economy_without_country(self):
        item = {"subject": [_services_product("EXT/ECO", "EXT")]}
        macro.map_packages(item)

        services = [s for s in item["subject"] if s["scheme"] == "services-products"]
        countries = [s for s in item["subject"] if s["scheme"] == "country"]
        self.assertEqual(services[0]["qcode"], "NEWS/ECONOMY")
        self.assertEqual(countries, [])

    def test_sports_exception(self):
        item = {"subject": [_services_product("SPN/GEN", "SPN")]}
        macro.map_packages(item)

        services = [s for s in item["subject"] if s["scheme"] == "services-products"]
        countries = [s for s in item["subject"] if s["scheme"] == "country"]
        self.assertEqual(services[0]["qcode"], "NEWS/SPORTS")
        self.assertEqual(countries, [])

    def test_int_sets_belgium(self):
        item = {"subject": [_services_product("INT/POL", "INT")]}
        macro.map_packages(item)

        services = [s for s in item["subject"] if s["scheme"] == "services-products"]
        countries = [s for s in item["subject"] if s["scheme"] == "country"]
        self.assertEqual(services[0]["qcode"], "NEWS/POLITICS")
        self.assertEqual(countries[0]["qcode"], "country_bel")

    def test_no_services_products_is_noop(self):
        item = {"subject": [{"qcode": "BRIEF", "scheme": "belga-keywords"}]}
        macro.map_packages(item)
        self.assertEqual(
            item["subject"], [{"qcode": "BRIEF", "scheme": "belga-keywords"}]
        )


class AutoTranslateToEnTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.app.data.insert("vocabularies", [SERVICES_PRODUCTS_CV, COUNTRY_CV])

    def test_translates_and_maps(self):
        item = {
            "guid": "guid-1",
            "language": "fr",
            "headline": "Bonjour",
            "body_html": "<p>Bonjour le monde</p>",
            "subject": [_services_product("EXT/ECO", "EXT")],
        }

        with patch.object(
            macro, "translate_text", side_effect=_fake_translate
        ) as translate:
            macro.auto_translate_to_en(item)

        self.assertEqual(translate.call_count, 1)
        combined = translate.call_args[0][0]
        self.assertIn('<h1 data-field="headline">Bonjour</h1>', combined)
        self.assertIn("<p>Bonjour le monde</p>", combined)

        self.assertEqual(item["language"], "en")
        self.assertEqual(item["headline"], "EN Bonjour")
        self.assertNotIn("<", item["headline"])
        self.assertIn("<p>", item["body_html"])
        self.assertIn("EN", item["body_html"])

        services = [s for s in item["subject"] if s["scheme"] == "services-products"]
        self.assertEqual(services[0]["qcode"], "NEWS/ECONOMY")

    def test_headline_only_is_stripped(self):
        item = {
            "guid": "guid-3",
            "language": "fr",
            "headline": "Bonjour le monde",
            "subject": [_services_product("EXT/ECO", "EXT")],
        }

        with patch.object(macro, "translate_text", side_effect=_fake_translate):
            macro.auto_translate_to_en(item)

        self.assertEqual(item["headline"], "EN Bonjour le monde")
        self.assertNotIn("<", item["headline"])

    def test_body_with_its_own_h1_is_preserved(self):
        item = {
            "guid": "guid-5",
            "language": "fr",
            "headline": "Bonjour",
            "body_html": "<h1>Titre du corps</h1><p>Bonjour le monde</p>",
            "subject": [_services_product("EXT/ECO", "EXT")],
        }

        with patch.object(macro, "translate_text", side_effect=_fake_translate):
            macro.auto_translate_to_en(item)

        self.assertEqual(item["headline"], "EN Bonjour")
        self.assertIn("EN Titre du corps", item["body_html"])
        self.assertIn("<h1>", item["body_html"])

    def test_falls_back_to_separate_calls_when_marker_lost(self):
        item = {
            "guid": "guid-4",
            "language": "fr",
            "headline": "Bonjour",
            "body_html": "<p>Bonjour le monde</p>",
            "subject": [_services_product("EXT/ECO", "EXT")],
        }

        calls = []

        def fake(text, target_language="en"):
            calls.append(text)
            if len(calls) == 1:
                return "<p>EN everything</p>"
            return _fake_translate(text, target_language)

        with patch.object(macro, "translate_text", side_effect=fake):
            macro.auto_translate_to_en(item)

        self.assertEqual(len(calls), 3)
        self.assertEqual(item["headline"], "EN Bonjour")
        self.assertNotIn("<", item["headline"])
        self.assertIn("<p>", item["body_html"])

    def test_translation_failure_still_maps_packages(self):
        item = {
            "guid": "guid-2",
            "language": "nl",
            "headline": "Hallo",
            "body_html": "<p>Hallo wereld</p>",
            "subject": [_services_product("BIN/ALG", "BIN")],
        }

        with patch.object(
            macro,
            "translate_text",
            side_effect=RuntimeError("endpoint unreachable"),
        ):
            macro.auto_translate_to_en(item)

        self.assertEqual(item["headline"], "Hallo")
        services = [s for s in item["subject"] if s["scheme"] == "services-products"]
        countries = [s for s in item["subject"] if s["scheme"] == "country"]
        self.assertEqual(services[0]["qcode"], "NEWS/GENERAL")
        self.assertEqual(countries[0]["qcode"], "country_bel")


class BelgaAiTranslateTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.app.config["BELGA_AI_URL"] = "http://belga-ai.test/api/"

    def _mock_response(self, payload):
        response = MagicMock()
        response.json.return_value = payload
        response.raise_for_status.return_value = None
        return response

    def test_posts_expected_request(self):
        with patch.object(
            belga_ai_translate.requests,
            "post",
            return_value=self._mock_response({"response": "Hello world"}),
        ) as post:
            result = belga_ai_translate.translate_text("<p>Bonjour le monde</p>")

        self.assertEqual(result, "Hello world")
        post.assert_called_once()
        args, kwargs = post.call_args
        self.assertEqual(args[0], "http://belga-ai.test/api/toolkit/translate")
        self.assertEqual(
            kwargs["json"],
            {"language": "en", "text": "<p>Bonjour le monde</p>"},
        )
        self.assertIn("User", kwargs["headers"])

    def test_handles_list_response(self):
        with patch.object(
            belga_ai_translate.requests,
            "post",
            return_value=self._mock_response({"response": ["Hello world"]}),
        ):
            result = belga_ai_translate.translate_text("Bonjour le monde")

        self.assertEqual(result, "Hello world")

    def test_empty_text_skips_request(self):
        with patch.object(belga_ai_translate.requests, "post") as post:
            self.assertEqual(belga_ai_translate.translate_text(""), "")
        post.assert_not_called()

    def test_missing_url_raises(self):
        self.app.config["BELGA_AI_URL"] = None
        with self.assertRaises(RuntimeError):
            belga_ai_translate.translate_text("Bonjour")
