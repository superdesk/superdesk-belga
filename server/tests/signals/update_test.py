
from superdesk.tests import TestCase
from belga.signals.update import handle_update, ALERT, TEXT


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
