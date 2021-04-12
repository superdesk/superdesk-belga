
from superdesk.tests import TestCase
from belga.signals.update import handle_update, ALERT, TEXT, handle_coming_up_field


class UpdateAlertTestCase(TestCase):

    def setUp(self):
        self.profiles = self.app.data.insert('content_types', [
            {'label': 'Foo'},
            {'label': ALERT},
            {'label': TEXT},
        ])

    def test_update_alert(self):
        item = {}
        orig = {}
        handle_update(None, item, orig)
        self.assertIsNone(item.get('profile'))

        item['profile'] = self.profiles[0]
        handle_update(None, item, orig)
        self.assertEqual(self.profiles[0], item['profile'])

        item['profile'] = self.profiles[1]
        handle_update(None, item, orig)
        self.assertEqual(self.profiles[2], item['profile'])
        self.assertEqual(3, item['urgency'])
        self.assertIn({
            'name': 'default',
            'qcode': 'default',
            'scheme': 'distribution',
        }, item['subject'])

    def test_update_is_coming_up_field(self):
        in_progress_item = {
            "extra": {
                "DueBy": "2021-04-12T20:45:33+0000",
            },
            "state": "in_progress",
        }
        published_item = {
            "extra": {
                "DueBy": "2021-04-12T20:45:33+0000",
            },
            "state": "published",
        }
        in_progress_orig = {
            "extra": {
                "DueBy": "2021-04-12T20:45:33+0000",
            },
            "state": "in_progress",
        }
        published_orig = {
            "extra": {
                "DueBy": "2021-04-12T20:45:33+0000",
            },
            "state": "published",
        }

        handle_coming_up_field(None, in_progress_item, in_progress_orig)
        self.assertEqual("2021-04-12T20:45:33+0000", in_progress_orig["extra"]["DueBy"])
        self.assertIsNone(in_progress_item.get("extra", {}).get("DueBy"))
        handle_coming_up_field(None, published_item, published_orig)
        self.assertEqual("2021-04-12T20:45:33+0000", published_orig["extra"]["DueBy"])
        self.assertIsNotNone(published_item.get("extra", {}).get("DueBy"))
