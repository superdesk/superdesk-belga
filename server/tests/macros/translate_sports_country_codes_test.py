import unittest
from belga.macros import translate_sports_country_codes as macro


class TranslateSportsCountryCodesTestCase(unittest.TestCase):

    def test_macro(self):
        assert hasattr(macro, 'name')
        assert hasattr(macro, 'label')
        assert hasattr(macro, 'callback')
        assert macro.action_type == 'direct'
        assert macro.access_type == 'frontend'

    def test_translate(self):
        item = {
            'language': 'fr',
            'body_html':
                '<p>29. Thomas Tumler (SUI) 2:00.44 ( 59.67 + 1:00.77)</p>',
        }
        macro.callback(item)
        self.assertEqual(
            '<p>29. Thomas Tumler (Sui) 2:00.44 ( 59.67 + 1:00.77)</p>',
            item['body_html'],
        )
        item['language'] = 'nl'
        macro.callback(item)
        self.assertEqual(
            '<p>29. Thomas Tumler (Zwi) 2:00.44 ( 59.67 + 1:00.77)</p>',
            item['body_html'],
        )
