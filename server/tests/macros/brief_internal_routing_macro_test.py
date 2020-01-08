
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
        item = {}
        macro.callback(item)
