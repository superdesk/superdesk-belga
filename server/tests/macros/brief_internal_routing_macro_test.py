
import unittest
import superdesk.tests as tests

from datetime import timedelta
from superdesk.utc import utcnow
from superdesk.errors import StopDuplication
from superdesk.metadata.item import CONTENT_STATE
from apps.archive.common import SCHEDULE_SETTINGS
from belga.macros import brief_internal_routing as macro


class MacroMetadataTestCase(unittest.TestCase):

    def test_macro(self):
        assert hasattr(macro, 'name')
        assert hasattr(macro, 'label')
        assert hasattr(macro, 'callback')
        assert macro.action_type == 'direct'
        assert macro.access_type == 'backend'


class BriefInternalRoutingMacroTestCase(tests.TestCase):

    def setUp(self):
        self.profiles = self.app.data.insert('content_types', [
            {'label': 'Brief'},
        ])

    def test_callback(self):
        now = utcnow()
        item = {
            '_id': 'foo',
            'guid': 'foo',
            'type': 'text',
            'state': CONTENT_STATE.PUBLISHED,
            'task': {},
            'versioncreated': now,
        }

        with self.assertRaises(StopDuplication):
            macro.callback(item)

        # test metadata
        self.assertEqual(self.profiles[0], item['profile'])
        self.assertEqual(2, item['urgency'])
        self.assertIn({
            'name': 'BELGA/AG',
            'qcode': 'BELGA/AG',
            'scheme': 'credits',
        }, item['subject'])

        # test published
        published = self.app.data.find_one('published', req=None, original_id=item['_id'])
        self.assertIsNotNone(published)
        self.assertEqual(CONTENT_STATE.SCHEDULED, published['state'])

        # test schedule
        schedule = published[SCHEDULE_SETTINGS]['utc_publish_schedule']
        self.assertGreaterEqual(now + timedelta(minutes=31), schedule)
        self.assertLessEqual(now + timedelta(minutes=29), schedule)
