from .. import TestCase

from belga.planning_exports.common import get_item_location


class GetItemLocationTests(TestCase):
    def test_no_index_error_when_address_lines_missing(self):
        """Address line missing/empty should not raise and still return parts."""
        event = {
            "language": "en",
            "location": [
                {
                    "name": "Brussels",
                    "address": {
                        "city": "Brussels",
                        "country": "Belgium",
                        # Explicitly provide empty list to mimic missing address lines
                        "line": [],
                    },
                }
            ],
        }

        result = get_item_location(event, locale="en")

        self.assertIsInstance(result, str)
        self.assertEqual(result, "Brussels, Brussels, Belgium")

    def test_location_with_empty_line_and_area(self):
        """Handles empty address.line with area/postal code present."""
        event = {
            "language": "en",
            "location": [
                {
                    "name": "Brussel",
                    "qcode": "736614",
                    "address": {
                        "area": "Brussel",
                        "boundingbox": [],
                        "country": "Belgium",
                        "line": [],
                        "locality": "Brussel",
                        "postal_code": "1000",
                        "type": "unclassified",
                    },
                }
            ],
        }

        result = get_item_location(event, locale="en")

        self.assertIsInstance(result, str)
        self.assertEqual(result, "Brussel, 1000 Brussel, Belgium")
