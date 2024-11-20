# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import json
import logging
from copy import deepcopy
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import superdesk
from belga.io.feed_parsers.belga_spreadsheet import BelgaSpreadsheetParser
from superdesk.errors import IngestApiError, ParserError, SuperdeskIngestError
from superdesk.io.feeding_services import FeedingService
from superdesk.io.registry import (
    register_feeding_service,
    register_feeding_service_parser,
)
from superdesk.metadata.item import GUID_FIELD, GUID_NEWSML
from superdesk.metadata.utils import generate_guid

logger = logging.getLogger(__name__)


class IngestSpreadsheetError(SuperdeskIngestError):
    _codes = {
        15100: "Missing permission",
        15200: "Quota limit",
        15300: "Invalid credentials",
        15400: "Worksheet not found",
    }

    @classmethod
    def SpreadsheetPermissionError(cls, exception=None, provider=None):
        return IngestSpreadsheetError(15100, exception, provider)

    @classmethod
    def SpreadsheetQuotaLimitError(cls, exception=None, provider=None):
        return IngestSpreadsheetError(15200, exception, provider)

    @classmethod
    def SpreadsheetCredentialsError(cls, exception=None, provider=None):
        return IngestSpreadsheetError(15300, exception, provider)

    @classmethod
    def WorksheetNotFoundError(cls, exception=None, provider=None):
        return IngestSpreadsheetError(15400, exception, provider)


class SpreadsheetFeedingService(FeedingService):
    NAME = "spreadsheet"
    service = "events"
    ERRORS = [
        IngestApiError.apiNotFoundError().get_error_description(),
        ParserError.parseFileError().get_error_description(),
        IngestSpreadsheetError.SpreadsheetPermissionError().get_error_description(),
        IngestSpreadsheetError.SpreadsheetQuotaLimitError().get_error_description(),
        IngestSpreadsheetError.SpreadsheetCredentialsError().get_error_description(),
        IngestSpreadsheetError.WorksheetNotFoundError().get_error_description(),
    ]

    label = "Events from Google Documents Spreadsheet"

    fields = [
        {
            "id": "service_account",
            "type": "text",
            "label": "Service account",
            "required": True,
            "errors": {15300: "Invalid service account key"},
        },
        {
            "id": "url",
            "type": "text",
            "label": "Source",
            "placeholder": "Google Spreadsheet URL",
            "required": True,
            "errors": {
                1001: "Can't parse spreadsheet.",
                1002: "Can't parse spreadsheet.",
                4006: "URL not found.",
                15100: "Missing write permission while processing file",
                15200: "Server reaches read quota limits.",
            },
        },
        {
            "id": "worksheet_title",
            "type": "text",
            "label": "Sheet title",
            "placeholder": "Title / Name of sheet",
            "required": True,
            "errors": {15400: "Sheet not found"},
        },
    ]

    def _test(self, provider):
        worksheet = self._get_worksheet(provider)
        data = worksheet.get_all_values()
        BelgaSpreadsheetParser().parse_titles(data[0])

    def _update(self, provider, update):
        """Load items from google spreadsheet and insert (update) to events database

        If STATUS field is empty, create new item
        If STATUS field is UPDATED, update item
        """
        worksheet = self._get_worksheet(provider)

        # Get all values to avoid reaching read limit
        data = worksheet.get_all_values()
        titles = [s.lower().strip() for s in data[0]]

        # avoid maximum limit cols error
        total_col = worksheet.col_count
        if total_col < len(titles) + 3:
            worksheet.add_cols(len(titles) + 3 - total_col)

        for field in ("_STATUS", "_ERR_MESSAGE", "_GUID"):
            if field.lower() not in titles:
                titles.append(field)
                worksheet.update_cell(1, len(titles), field)
        data[0] = titles  # pass to parser uses for looking up index

        parser = BelgaSpreadsheetParser()
        items, cells_list = parser.parse(data, provider)
        items = self._process_event_items(items, provider)
        # add ingest item
        yield items
        # Update status for google sheet
        if cells_list:
            worksheet.update_cells(cells_list)

    def _get_worksheet(self, provider):
        """Get worksheet from google spreadsheet

        :return: worksheet
        :rtype: object
        """
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        config = provider.get("config", {})
        url = config.get("url", "")
        service_account = config.get("service_account", "")
        title = config.get("worksheet_title", "")

        try:
            service_account = json.loads(service_account)
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                service_account, scope
            )
            gc = gspread.authorize(credentials)
            spreadsheet = gc.open_by_url(url)
            permission = spreadsheet.list_permissions()[0]
            if permission["role"] != "writer":
                raise IngestSpreadsheetError.SpreadsheetPermissionError()
            worksheet = spreadsheet.worksheet(title)
            return worksheet
        except (json.decoder.JSONDecodeError, AttributeError, ValueError) as e:
            # both permission and credential raise Value error
            if e.args[0] == 15100:
                raise IngestSpreadsheetError.SpreadsheetPermissionError()
            raise IngestSpreadsheetError.SpreadsheetCredentialsError()
        except gspread.exceptions.NoValidUrlKeyFound:
            raise IngestApiError.apiNotFoundError()
        except gspread.exceptions.WorksheetNotFound:
            raise IngestSpreadsheetError.WorksheetNotFoundError()
        except gspread.exceptions.APIError as e:
            error = e.response.json()["error"]
            response_code = error["code"]
            logger.error("Provider %s: %s", provider.get("name"), error["message"])
            if response_code == 403:
                raise IngestSpreadsheetError.SpreadsheetPermissionError()
            elif response_code == 429:
                raise IngestSpreadsheetError.SpreadsheetQuotaLimitError()
            else:
                raise IngestApiError.apiNotFoundError()

    def _process_event_items(self, items, provider):
        events_service = superdesk.get_resource_service("events")
        list_items = []
        for item in items:
            status = item.pop("status")
            location = item.get("location")
            if item.get("contact"):
                contact = item.pop("contact")
                contact_service = superdesk.get_resource_service("contacts")
                _contact = contact_service.find_one(
                    req=None,
                    **{
                        "first_name": contact["first_name"],
                        "last_name": contact["last_name"],
                        "organisation": contact["organisation"],
                        "contact_email": contact["contact_email"][0],
                        "contact_phone.number": contact["contact_phone"][0]["number"],
                    },
                )
                if _contact and status == "UPDATED":
                    item.setdefault(
                        "event_contact_info", [_contact[superdesk.config.ID_FIELD]]
                    )
                    contact_service.patch(_contact[superdesk.config.ID_FIELD], contact)
                else:
                    item.setdefault(
                        "event_contact_info", list(contact_service.post([contact]))
                    )

            if location:
                location_service = superdesk.get_resource_service("locations")
                saved_location = list(
                    location_service.find(
                        {
                            "name": location[0]["name"],
                            "address.line": location[0]["address"]["line"],
                            "address.country": location[0]["address"]["country"],
                        }
                    )
                )
                if saved_location and status == "UPDATED":
                    location_service.patch(
                        saved_location[0][superdesk.config.ID_FIELD], location[0]
                    )
                elif not saved_location:
                    _location = deepcopy(location)
                    location_service.post(_location)
                    item["location"][0]["qcode"] = _location[0]["guid"]

            old_item = events_service.find_one(guid=item[GUID_FIELD], req=None)
            if not old_item:
                if not status:
                    item.setdefault("firstcreated", datetime.now())
                    item.setdefault("versioncreated", datetime.now())
                    list_items.append(item)
            else:
                old_item.update(item)
                list_items.append(old_item)
        return list_items


register_feeding_service(SpreadsheetFeedingService)
register_feeding_service_parser(SpreadsheetFeedingService.NAME, "belgaspreadsheet")
