
from superdesk.tests import TestCase
from belga.macros import brief_internal_routing as macro


class BriefInternalRoutingMacroTestCase(TestCase):

    def test_metadata(self):
        assert hasattr(macro, 'name')
        assert hasattr(macro, 'label')
        assert hasattr(macro, 'callback')
        assert macro.action_type == 'direct'
        assert macro.access_type == 'backend'

    def test_callback(self):
        profiles = self.app.data.insert('content_types', [
            {'label': 'Brief'},
        ])

        item = {}
        macro.callback(item)

        self.assertEqual(profiles[0], item['profile'])
        self.assertEqual(2, item['urgency'])
        self.assertIn({
            'name': 'BELGA/AG',
            'qcode': 'BELGA/AG',
            'scheme': 'credits',
        }, item['subject'])
