from .. import TestCase
from datetime import datetime, timezone

from belga.planning_exports.common import (
    get_item_location,
    get_display_times,
    get_planning_display_times,
)


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


class GetPlanningDisplayTimesTests(TestCase):
    def test_prefers_event_dates_when_present(self):
        planning = {
            "planning_date": datetime(2024, 4, 23, 10, 0, tzinfo=timezone.utc),
            "coverages": [
                {
                    "planning": {
                        "scheduled": datetime(2024, 4, 23, 11, 0, tzinfo=timezone.utc)
                    }
                }
            ],
            "dates": {"tz": "Europe/Brussels"},
        }
        event_item = {
            "dates": {
                "start": datetime(2024, 4, 23, 8, 0, tzinfo=timezone.utc),
                "end": datetime(2024, 4, 23, 9, 0, tzinfo=timezone.utc),
                "tz": "Europe/Brussels",
            }
        }

        expected = get_display_times(event_item["dates"])

        result_time, result_display = get_planning_display_times(planning, event_item)

        self.assertEqual(result_time, expected["time"])
        self.assertEqual(result_display, expected["display_time"])

    def test_falls_back_to_coverage_scheduled_when_event_dates_incomplete(self):
        planning = {
            "planning_date": datetime(2024, 4, 23, 10, 0, tzinfo=timezone.utc),
            "coverages": [
                {
                    "planning": {
                        "scheduled": datetime(2024, 4, 23, 12, 0, tzinfo=timezone.utc)
                    }
                }
            ],
            "dates": {"tz": "Europe/Brussels"},
        }
        event_item = {
            "dates": {
                "start": datetime(2024, 4, 23, 8, 0, tzinfo=timezone.utc),
                "tz": "Europe/Brussels",
            }
        }

        fallback_dates = {
            "start": planning["coverages"][0]["planning"]["scheduled"],
            "end": planning["coverages"][0]["planning"]["scheduled"],
            "tz": "Europe/Brussels",
        }
        expected = get_display_times(fallback_dates)

        result_time, result_display = get_planning_display_times(planning, event_item)

        self.assertEqual(result_time, expected["time"])
        self.assertEqual(result_display, expected["display_time"])

    def test_falls_back_to_planning_date_when_no_coverage_scheduled(self):
        planning = {
            "planning_date": datetime(2024, 4, 23, 13, 30, tzinfo=timezone.utc),
            "coverages": [],
            "dates": {"tz": "Europe/Brussels"},
        }
        event_item = {
            "dates": {
                "start": datetime(2024, 4, 23, 8, 0, tzinfo=timezone.utc),
                "tz": "Europe/Brussels",
            }
        }

        fallback_dates = {
            "start": planning["planning_date"],
            "end": planning["planning_date"],
            "tz": "Europe/Brussels",
        }
        expected = get_display_times(fallback_dates)

        result_time, result_display = get_planning_display_times(planning, event_item)

        self.assertEqual(result_time, expected["time"])
        self.assertEqual(result_display, expected["display_time"])
