from superdesk.tests import TestCase
from belga.signals.update import handle_update, ALERT, TEXT, handle_coming_up_field


class UpdateAlertTestCase(TestCase):
    def setUp(self):
        self.profiles = self.app.data.insert(
            "content_types",
            [
                {"label": "Foo"},
                {"label": ALERT},
                {"label": TEXT},
            ],
        )

    def test_update_alert(self):
        item = {}
        orig = {}
        handle_update(None, item, orig)
        self.assertIsNone(item.get("profile"))

        item["profile"] = self.profiles[0]
        handle_update(None, item, orig)
        self.assertEqual(self.profiles[0], item["profile"])

        item["profile"] = self.profiles[1]
        handle_update(None, item, orig)
        self.assertEqual(self.profiles[2], item["profile"])
        self.assertEqual(3, item["urgency"])
        self.assertIn(
            {
                "name": "default",
                "qcode": "default",
                "scheme": "distribution",
            },
            item["subject"],
        )

    def test_update_is_coming_up_field(self):
        item = {
            "extra": {
                "DueBy": "2021-04-12T20:45:33+0000",
            },
            "state": "in_progress",
        }
        orig = {
            "extra": {
                "DueBy": "2021-04-12T20:45:33+0000",
            },
            "state": "in_progress",
        }

        handle_coming_up_field(None, item, orig)
        self.assertEqual("2021-04-12T20:45:33+0000", orig["extra"]["DueBy"])
        self.assertIsNone(item.get("extra", {}).get("DueBy"))
