import unittest

from belga.macros import unmark_from_user as macro


class UnmarkFromUserTestCase(unittest.TestCase):
    def test_metadata(self):
        assert hasattr(macro, "name")
        assert hasattr(macro, "label")
        assert hasattr(macro, "callback")

    def test_callback(self):
        item = {"marked_for_user": "foo", "guid": "test"}
        orig = item.copy()
        item = macro.callback(item)
        self.assertIsNone(item["marked_for_user"])
        self.assertEqual(item["previous_marked_user"], "foo")
