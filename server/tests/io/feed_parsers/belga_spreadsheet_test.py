# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from datetime import datetime, timezone

from belga.io.feed_parsers.belga_spreadsheet import BelgaSpreadsheetParser
from tests import TestCase


data = [
    [
        "Start date",
        "Start time",
        "End date",
        "End time",
        "All day",
        "Timezone",
        "Slugline",
        "Event name",
        "Description",
        "Occurence status",
        "Calendars",
        "Location Name",
        "Location Address",
        "Location City/Town",
        "Location State/Province/Region",
        "Location Country",
        "Contact Honorific",
        "Contact First name",
        "Contact Last name",
        "Contact Organisation",
        "Contact Point of Contact",
        "Contact Email",
        "Contact Phone Number",
        "Contact Phone Usage",
        "Contact Phone Public",
        "Long description",
        "Internal note",
        "Ed note",
        "External links",
        "_STATUS",
        "_ERR_MESSAGE",
        "_GUID",
    ],
    [],
    [
        "2019-06-20",
        "7:00",
        "2019-06-20",
        "15:00",
        "FALSE",
        "Europe/Brussels",
        "Slugline1",
        "Event 1",
        "Description",
        "Planned, occurrence planned only",
        "Culture",
        "Name",
        "Address",
        "City",
        "State",
        "Country",
        "Honorific",
        "First name",
        "Last name",
        "Organisation",
        "Point of Contact",
        "email@mail.com",
        "Phone",
        "Business",
        "FALSE",
        "Long description",
        "Inote",
        "Enote",
        "https://www.superdesk.org",
        "",
        "",
        "",
    ],
    [
        "2019-06-20",
        "7:00",
        "2019-06-21",
        "8:00",
        "TRUE",
        "Europe/Brussels",
        "Slugline2",
        "Event 2",
        "Description",
        "",
        "Business",
        "",
    ]
    + [""] * 20,
    [
        "2019-06-20",
        "7:00",
        "2019-06-20",
        "7:00",
        "TRUE",
        "Europe/Bruss",
        "Slugline3",
        "Event 3",
    ]
    + [""] * 20,
    [
        "",
        "7:00",
        "2019-06-20",
        "7:00",
        "TRUE",
        "Europe/Brussels",
        "Slugline4",
        "Event 4",
    ]
    + [""] * 20,
]


class BelgaSpreadsheetsTestCase(TestCase):
    def setUp(self):
        provider = {"name": "test"}
        self.parser = BelgaSpreadsheetParser()
        self.items, self.error = self.parser.parse(data, provider)

    def test_can_parse(self):
        self.assertTrue(self.parser.can_parse(data[0]))

    def test_content(self):
        item = self.items[0]
        self.assertEqual(item["name"], "Event 1")
        self.assertEqual(item["slugline"], "Slugline1")
        self.assertEqual(item["definition_short"], "Description")
        self.assertEqual(item["definition_long"], "Long description")
        self.assertEqual(item["status"], "")
        self.assertEqual(item["internal_note"], "Inote")
        self.assertEqual(item["ednote"], "Enote")
        self.assertListEqual(item["links"], ["https://www.superdesk.org"])
        self.assertListEqual(
            item["calendars"],
            [{"is_active": True, "name": "Culture", "qcode": "culture"}],
        )
        self.assertListEqual(
            item["location"],
            [
                {
                    "name": "Name",
                    "address": {
                        "line": ["Address"],
                        "locality": "City",
                        "area": "State",
                        "country": "Country",
                    },
                }
            ],
        )
        self.assertDictEqual(
            item["dates"],
            {
                "start": datetime(2019, 6, 20, 5, tzinfo=timezone.utc),
                "end": datetime(2019, 6, 20, 13, tzinfo=timezone.utc),
                "tz": "Europe/Brussels",
            },
        )
        self.assertDictEqual(
            item["occur_status"],
            {
                "qcode": "eocstat:eos1",
                "name": "Planned, occurrence planned only",
                "label": "planned, occurrence planned only",
            },
        )
        self.assertDictEqual(
            item["contact"],
            {
                "honorific": "Honorific",
                "first_name": "First name",
                "last_name": "Last name",
                "organisation": "Organisation",
                "contact_email": ["email@mail.com"],
                "contact_address": ["Point of Contact"],
                "contact_phone": [
                    {"number": "Phone", "public": False, "usage": "Business"}
                ],
            },
        )

    def test_all_day(self):
        item = self.items[1]
        self.assertDictEqual(
            item["dates"],
            {
                "start": datetime(2019, 6, 19, 22, tzinfo=timezone.utc),
                "end": datetime(2019, 6, 21, 21, 59, 59, tzinfo=timezone.utc),
                "tz": "Europe/Brussels",
            },
        )

    def test_error(self):
        error = [c.value for c in self.error[6:]]  # ignore first 6 non-error cells
        self.assertListEqual(
            error,
            [
                "ERROR",
                "Invalid timezone",
                "ERROR",
                "String does not contain a date: %s",
            ],
        )
