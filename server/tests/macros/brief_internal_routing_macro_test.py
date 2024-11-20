import unittest
from datetime import timedelta

import superdesk.tests as tests
from superdesk.utc import utcnow, utc_to_local, utc
from superdesk.errors import StopDuplication
from superdesk.metadata.item import CONTENT_STATE
from apps.archive.common import SCHEDULE_SETTINGS
from belga.macros import brief_internal_routing as macro
from belga.macros.brief_internal_routing import _get_product_subject, PRODUCTS


class MacroMetadataTestCase(unittest.TestCase):
    def test_macro(self):
        assert hasattr(macro, "name")
        assert hasattr(macro, "label")
        assert hasattr(macro, "callback")
        assert macro.action_type == "direct"
        assert (
            macro.access_type == "frontend"
        )  # to make it visible in internal destinations

    def test_product_rules(self):
        test_map = {
            "BIN/foo": "NEWS/GENERAL",
            "INT/foo": "NEWS/GENERAL",
            "SPN/foo": "NEWS/SPORTS",
            "SPF/foo": "NEWS/SPORTS",
            "foo/ALG": "NEWS/GENERAL",
            "foo/GEN": "NEWS/GENERAL",
            "SPN/ALG": "NEWS/SPORTS",
            "SPF/GEN": "NEWS/SPORTS",
            "foo/POL": "NEWS/POLITICS",
            "foo/ECO": "NEWS/ECONOMY",
            "other": "NEWS/GENERAL",
        }

        for old, new in test_map.items():
            subject = [
                {
                    "name": old,
                    "qcode": old,
                    "scheme": PRODUCTS,
                },
                {
                    "name": "foo",
                    "qcode": "country_foo",
                    "scheme": "country",
                },
            ]
            subject = _get_product_subject(subject)
            self.assertEqual(new, subject[0]["name"])
            if old in ("BIN/foo", "INT/foo"):
                self.assertIn(
                    {
                        "name": "Belgium",
                        "qcode": "country_bel",
                        "scheme": "country",
                    },
                    subject,
                )


class BriefInternalRoutingMacroTestCase(tests.TestCase):
    def setUp(self):
        self.profiles = self.app.data.insert(
            "content_types",
            [
                {"label": "BRIEF"},
                {"label": "TEXT"},
            ],
        )
        self.now = utcnow()

    def test_callback(self):
        # Test when BELGA source is already present in the item
        item = {
            "_id": "foo",
            "guid": "foo",
            "type": "text",
            "state": CONTENT_STATE.PUBLISHED,
            "task": {},
            "profile": self.profiles[1],
            "versioncreated": self.now - timedelta(minutes=5),
            "headline": "foo BELGANIGHT bar (test)",
            "body_html": "".join(
                [
                    "<p>foo</p>",
                    "<p>Disclaimer:</p>",
                    "<p>bar</p>",
                ]
            ),
            "subject": [
                {"name": "superdesk", "qcode": "SUPERDESK", "scheme": "sources"},
                {"name": "BELGA", "qcode": "BELGA", "scheme": "sources"},
            ],
        }

        with self.assertRaises(StopDuplication):
            macro.callback(item)

        # test metadata
        self.assertEqual(self.profiles[0], item["profile"])
        self.assertEqual(2, item["urgency"])
        self.assertIn(
            {
                "name": "BELGA",
                "qcode": "BELGA",
                "scheme": "credits",
            },
            item["subject"],
        )
        # Ensure BELGA is present in 'sources'
        self.assertIn(
            {
                "name": "BELGA",
                "qcode": "BELGA",
                "scheme": "sources",
            },
            item["subject"],
        )
        # Ensure SUPERDESK is present in 'sources'
        self.assertIn(
            {
                "name": "superdesk",
                "qcode": "SUPERDESK",
                "scheme": "sources",
            },
            item["subject"],
        )

        # Ensure BELGA is present in 'sources' only once
        sources = [subj for subj in item["subject"] if subj["scheme"] == "sources"]
        self.assertEqual(len([src for src in sources if src["qcode"] == "BELGA"]), 1)

        # Test when BELGA source is not present in the item (item2)
        item2 = {
            "_id": "bar",
            "guid": "bar",
            "type": "text",
            "state": CONTENT_STATE.PUBLISHED,
            "task": {},
            "profile": self.profiles[1],
            "versioncreated": self.now - timedelta(minutes=5),
            "headline": "bar BELGANIGHT bar (test)",
            "body_html": "".join(
                [
                    "<p>bar</p>",
                    "<p>Disclaimer:</p>",
                    "<p>bar</p>",
                ]
            ),
            "subject": [
                {"name": "ANP", "qcode": "ANP", "scheme": "sources"},
            ],
        }

        with self.assertRaises(StopDuplication):
            macro.callback(item2)

        self.assertIn(
            {
                "name": "BELGA",
                "qcode": "BELGA",
                "scheme": "credits",
            },
            item2["subject"],
        )

        # Ensure BELGA is correctly added to 'sources' in item2
        self.assertIn(
            {
                "name": "BELGA",
                "qcode": "BELGA",
                "scheme": "sources",
            },
            item2["subject"],
        )

        # Ensure ANP is still present in 'sources' in item2
        self.assertIn(
            {
                "name": "ANP",
                "qcode": "ANP",
                "scheme": "sources",
            },
            item2["subject"],
        )

        # Ensure BELGA is present in 'sources' only once in item2
        sources2 = [subj for subj in item2["subject"] if subj["scheme"] == "sources"]
        self.assertEqual(len([src for src in sources2 if src["qcode"] == "BELGA"]), 1)

        # test published
        published = self.app.data.find_one(
            "published", req=None, original_id=item["_id"]
        )
        self.assertIsNotNone(published)
        self.assertEqual(CONTENT_STATE.SCHEDULED, published["state"])

        # test schedule
        schedule = published[SCHEDULE_SETTINGS]["utc_publish_schedule"]
        self.assertGreaterEqual(self.now + timedelta(minutes=31), schedule)
        self.assertLessEqual(self.now + timedelta(minutes=29), schedule)
        self.assertEqual("Europe/Brussels", published[SCHEDULE_SETTINGS]["time_zone"])
        self.assertEqual(
            utc_to_local("Europe/Brussels", self.now + timedelta(minutes=30)).replace(
                tzinfo=utc
            ),
            published["publish_schedule"],
        )

        # test content
        self.assertEqual("foo bar", published["headline"])
        self.assertEqual("<p>foo</p>", published["body_html"])

    def test_publish_scheduled(self):
        item = {
            "_id": "foo",
            "guid": "foo",
            "type": "text",
            "state": CONTENT_STATE.SCHEDULED,
            "task": {},
            "profile": self.profiles[1],
            "versioncreated": self.now - timedelta(minutes=5),
            "headline": "foo bar",
            "body_html": "foo",
            SCHEDULE_SETTINGS: {
                "time_zone": "Europe/Brussels",
                "utc_publish_schedule": self.now + timedelta(minutes=20),
            },
        }

        with self.assertRaises(StopDuplication):
            macro.callback(item)

        published = self.app.data.find_one(
            "published", req=None, original_id=item["_id"]
        )
        schedule = published[SCHEDULE_SETTINGS]["utc_publish_schedule"]
        self.assertLessEqual(self.now + timedelta(minutes=45), schedule)

    def test_filtering(self):
        item = {}
        with self.assertRaises(StopDuplication):
            macro.callback(item)
        self.assertEqual({}, item)

        item["profile"] = self.profiles[0]
        with self.assertRaises(StopDuplication):
            macro.callback(item)
        self.assertEqual(1, len(item.keys()))

        item["profile"] = self.profiles[1]
        item["body_html"] = "<p>foo</p>" * 500
        with self.assertRaises(StopDuplication):
            macro.callback(item)
        self.assertEqual(2, len(item.keys()))
