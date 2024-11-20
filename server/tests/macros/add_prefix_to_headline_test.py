import unittest

from belga.macros.add_prefix_to_headline import add_prefix_to_headline


class AddBelgToHeadlineTestCase(unittest.TestCase):
    def test_add_belg_to_headline_macro(self):
        item = {"headline": "This is headline"}
        headline = "BELG " + item.get("headline", "")
        add_prefix_to_headline(item)
        self.assertEqual(item.get("headline"), headline)
