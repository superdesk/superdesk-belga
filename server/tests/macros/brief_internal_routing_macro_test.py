
import unittest
import superdesk.tests as tests

from datetime import timedelta
from superdesk.utc import utcnow
from superdesk.errors import StopDuplication
from superdesk.metadata.item import CONTENT_STATE
from apps.archive.common import SCHEDULE_SETTINGS
from belga.macros import brief_internal_routing as macro
from belga.macros.brief_internal_routing import _get_product_subject, PRODUCTS


class MacroMetadataTestCase(unittest.TestCase):

    def test_macro(self):
        assert hasattr(macro, 'name')
        assert hasattr(macro, 'label')
        assert hasattr(macro, 'callback')
        assert macro.action_type == 'direct'
        assert macro.access_type == 'frontend'  # to make it visible in internal destinations

    def test_product_rules(self):
        test_map = {
            'BIN/foo': 'NEWS/GENERAL',
            'INT/foo': 'NEWS/GENERAL',
            'SPN/foo': 'NEWS/SPORTS',
            'SPF/foo': 'NEWS/SPORTS',
            'foo/ALG': 'NEWS/GENERAL',
            'foo/GEN': 'NEWS/GENERAL',
            'foo/POL': 'NEWS/POLITICS',
            'foo/ECO': 'NEWS/ECONOMY',
            'other': 'NEWS/GENERAL',
        }

        for old, new in test_map.items():
            subject = [{
                'name': old,
                'qcode': old,
                'scheme': PRODUCTS,
            }, {
                'name': 'foo',
                'qcode': 'country_foo',
                'scheme': 'country',
            }]
            subject = _get_product_subject(subject)
            self.assertEqual(new, subject[0]['name'])
            if old in ('BIN/foo', 'INT/foo'):
                self.assertIn({
                    'name': 'Belgium',
                    'qcode': 'country_bel',
                    'scheme': 'country',
                }, subject)


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
