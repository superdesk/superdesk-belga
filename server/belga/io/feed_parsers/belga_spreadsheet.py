# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from datetime import timedelta

from dateutil.parser import parse
from gspread import Cell
from pytz.exceptions import UnknownTimeZoneError

import superdesk
from superdesk.errors import ParserError
from superdesk.io.feed_parsers import FeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.metadata.item import CONTENT_STATE, GUID_NEWSML, ITEM_STATE
from superdesk.metadata.utils import generate_guid
from superdesk.utc import local_to_utc

logger = logging.getLogger(__name__)


class BelgaSpreadsheetParser(FeedParser):
    """Feed Parser for Spreadsheet"""

    NAME = "belgaspreadsheet"

    label = "Belga Google Documents Spreadsheet Parser"

    titles = [
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
    ]

    generate_fields = ["_STATUS", "_ERR_MESSAGE", "_GUID"]

    required_field = ["calendars", "name"]

    required_contact_field = ["Contact Email", "Contact Phone Number"]
    required_location_field = ["Location Name", "Location Address", "Location Country"]

    occur_status_qcode_mapping = {
        "Unplanned event": "eocstat:eos0",
        "Planned, occurrence planned only": "eocstat:eos1",
        "Planned, occurrence highly uncertain": "eocstat:eos2",
        "Planned, May occur": "eocstat:eos3",
        "Planned, occurrence highly likely": "eocstat:eos4",
        "Planned, occurs certainly": "eocstat:eos5",
    }

    def can_parse(self, titles):
        try:
            self.parse_titles(titles)
            return True
        except ParserError:
            return False

    def parse(self, data, provider=None):
        index = self.parse_titles(data[0])
        items = []
        cells_list = []  # use for patch update to reduce write requests usage
        # skip first two title rows
        for row in range(3, len(data) + 1):
            if not row:
                break
            item = {}
            error_message = None
            values = data[row - 1]
            is_updated = (
                values[index["_STATUS"]].strip().upper()
                if len(values) - 1 > index["_STATUS"]
                else None
            )

            try:
                # only insert item if _STATUS is empty
                if is_updated in ("UPDATED", "ERROR"):
                    guid = values[index["_GUID"]]
                    # check if it's exists and guid is valid
                    if not superdesk.get_resource_service("events").find_one(
                        guid=guid, req=None
                    ):
                        raise KeyError("GUID is not exists")
                else:
                    guid = generate_guid(type=GUID_NEWSML)

                # avoid momentsJS throw null timezone value error
                tzone = (
                    values[index["Timezone"]]
                    if values[index["Timezone"]] != "none"
                    else "UTC"
                )
                start_datetime = parse(
                    values[index["Start date"]] + " " + values[index["Start time"]]
                )
                end_datetime = parse(
                    values[index["End date"]] + " " + values[index["End time"]]
                )
                if values[index["All day"]] == "TRUE":
                    start_datetime = parse(values[index["Start date"]])
                    end_datetime = parse(values[index["End date"]]) + timedelta(
                        days=1, seconds=-1
                    )
                if end_datetime < start_datetime:
                    raise ValueError("End datetime is smaller than Start datetime")

                item = {
                    "type": "event",
                    "name": values[index["Event name"]],
                    "slugline": values[index["Slugline"]],
                    "dates": {
                        "start": local_to_utc(tzone, start_datetime),
                        "end": local_to_utc(tzone, end_datetime),
                        "tz": tzone,
                    },
                    "definition_short": values[index["Description"]],
                    "definition_long": values[index["Long description"]],
                    "internal_note": values[index["Internal note"]],
                    "ednote": values[index["Ed note"]],
                    "links": [values[index["External links"]]],
                    "guid": guid,
                    "status": is_updated,
                }
                item.setdefault(ITEM_STATE, CONTENT_STATE.DRAFT)

                occur_status = values[index["Occurence status"]]
                if occur_status and occur_status in self.occur_status_qcode_mapping:
                    item["occur_status"] = {
                        "qcode": self.occur_status_qcode_mapping.get(
                            values[index["Occurence status"]]
                        ),
                        "name": values[index["Occurence status"]],
                        "label": values[index["Occurence status"]].lower(),
                    }

                calendars = values[index["Calendars"]]
                if calendars:
                    item["calendars"] = [
                        {
                            "is_active": True,
                            "name": calendars,
                            "qcode": calendars.lower(),
                        }
                    ]

                if all(values[index[field]] for field in self.required_location_field):
                    item["location"] = [
                        {
                            "name": values[index["Location Name"]],
                            "address": {
                                "line": [values[index["Location Address"]]],
                                "locality": values[index["Location City/Town"]],
                                "area": values[index["Location State/Province/Region"]],
                                "country": values[index["Location Country"]],
                            },
                        }
                    ]

                if all(
                    values[index[field]] for field in self.required_contact_field
                ) and (
                    all(
                        values[index[field]]
                        for field in ["Contact First name", "Contact Last name"]
                    )
                    or values[index["Contact Organisation"]]
                ):
                    is_public = values[index["Contact Phone Public"]] == "TRUE"
                    if values[index["Contact Phone Usage"]] == "Confidential":
                        is_public = False
                    item["contact"] = {
                        "honorific": values[index["Contact Honorific"]],
                        "first_name": values[index["Contact First name"]],
                        "last_name": values[index["Contact Last name"]],
                        "organisation": values[index["Contact Organisation"]],
                        "contact_email": [values[index["Contact Email"]]],
                        "contact_address": [values[index["Contact Point of Contact"]]],
                        "contact_phone": [
                            {
                                "number": values[index["Contact Phone Number"]],
                                "public": is_public,
                                "usage": values[index["Contact Phone Usage"]],
                            }
                        ],
                    }
                # ignore invalid item
                missing_fields = [
                    field for field in self.required_field if not item.get(field)
                ]
                if missing_fields:
                    missing_fields = ", ".join(missing_fields)
                    logger.error(
                        'Provider %s: Event "%s". Missing %s fields',
                        provider.get("name"),
                        item.get("name"),
                        missing_fields,
                    )
                    error_message = "Missing " + missing_fields + " fields"
            except UnknownTimeZoneError:
                error_message = "Invalid timezone"
                logger.error(
                    'Provider %s: Event "%s": Invalid timezone %s',
                    provider.get("name"),
                    values[index["Event name"]],
                    tzone,
                )
            except (TypeError, ValueError, KeyError) as e:
                error_message = e.args[0]
                logger.error(
                    'Provider %s: Event "%s": %s',
                    provider.get("name"),
                    item.get("name"),
                    error_message,
                )

            if error_message:
                cells_list.extend(
                    [
                        Cell(row, index["_STATUS"] + 1, "ERROR"),
                        Cell(row, index["_ERR_MESSAGE"] + 1, error_message),
                    ]
                )
            elif not is_updated or is_updated == "UPDATED":
                cells_list.extend(
                    [
                        Cell(row, index["_STATUS"] + 1, "DONE"),
                        Cell(row, index["_ERR_MESSAGE"] + 1, ""),
                    ]
                )
                if not is_updated:
                    # only update _GUID when status is empty
                    cells_list.append(Cell(row, index["_GUID"] + 1, guid))
                items.append(item)
        return items, cells_list

    def parse_titles(self, titles):
        """Lookup title columns and return dictionary of titles index"""
        index = {}
        titles = [s.lower().strip() for s in titles]
        for field in self.titles:
            if field.lower().strip() not in titles:
                raise ParserError.parseFileError()
            index[field] = titles.index(field.lower().strip())
        # generate_fields may not present when testing config
        for field in self.generate_fields:
            if field.lower().strip() in titles:
                index[field] = titles.index(field.lower().strip())

        return index


register_feed_parser(BelgaSpreadsheetParser.NAME, BelgaSpreadsheetParser())
