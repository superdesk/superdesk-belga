#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
import json

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from superdesk.errors import IngestApiError, ParserError, SuperdeskIngestError
from superdesk.io.feeding_services import FeedingService
from superdesk.io.registry import register_feeding_service
from belga.io.feed_parsers.belga_spreadsheets import BelgaSpreadsheetsParser

logger = logging.getLogger(__name__)


class IngestSpreadsheetError(SuperdeskIngestError):
    _codes = {
        15100: "Missing permission",
        15200: "Quota limit",
        15300: "Invalid credentials"
    }

    @classmethod
    def SpreadsheetPermissionError(cls, exception=None, provider=None):
        return IngestSpreadsheetError(15100, exception, provider)

    @classmethod
    def SpreadsheetQuotaLimit(cls, exception=None, provider=None):
        return IngestSpreadsheetError(15200, exception, provider)

    @classmethod
    def SpreadsheetCredentialsError(cls, exception=None, provider=None):
        return IngestSpreadsheetError(15300, exception, provider)


class SpreadsheetFeedingService(FeedingService):
    NAME = 'spreadsheet'

    ERRORS = [
        IngestApiError.apiNotFoundError().get_error_description(),
        ParserError.parseFileError().get_error_description(),
        IngestSpreadsheetError.SpreadsheetPermissionError().get_error_description(),
    ]

    label = 'Google Spreadsheet'

    fields = [
        {
            'id': 'service_account', 'type': 'text', 'label': 'Service account',
            'required': True, 'errors': {15300: 'Invalid service account key'},
        },
        {
            'id': 'url', 'type': 'text', 'label': 'Source',
            'placeholder': 'Google Spreadsheet URL', 'required': True,
            'errors': {
                1001: 'Can\'t parse spreadsheets.',
                1002: 'Can\'t parse spreadsheets.',
                4006: 'URL not found.',
                15100: 'Missing write permission while processing file',
                15200: 'Server reaches read quota limits.'
            }
        }
    ]

    def _test(self, provider):
        return self._update(provider, update=None, test=True)

    def _update(self, provider, update, test=False):
        """Load items from google spreadsheet and insert (update) to events database

        If STATUS field is empty, create new item
        If STATUS field is UPDATED, update item
        """
        config = provider.get('config', {})
        url = config.get('url', '')
        service_account = config.get('service_account', '')
        worksheet = self._get_worksheet(url, service_account)
        try:
            # Get all values to avoid reaching read limit
            data = worksheet.get_all_values()
            titles = [s.lower().strip() for s in data[0]]

            # avoid maximum limit cols error
            total_col = worksheet.col_count
            if total_col < len(titles) + 3:
                worksheet.add_cols(len(titles) + 3 - total_col)

            for field in ('_STATUS', '_ERR_MESSAGE', '_GUID'):
                if field.lower() not in titles:
                    titles.append(field)
                    worksheet.update_cell(1, len(titles), field)
            data[0] = titles  # pass to parser uses for looking up index

            parser = BelgaSpreadsheetsParser()
            items, cells_list = parser.parse(data, provider)
            if cells_list:
                worksheet.update_cells(cells_list)
            return [items]
        except gspread.exceptions.CellNotFound as e:
            raise ParserError.parseFileError(e)

    def _get_worksheet(self, url, service_account):
        """Get worksheet from google spreadsheet

        :return: worksheet
        :rtype: object

        :raises IngestSpreadsheetError
        """
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
        ]

        try:
            service_account = json.loads(service_account)
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account, scope)
            gc = gspread.authorize(credentials)
            spreadsheet = gc.open_by_url(url)
            permission = spreadsheet.list_permissions()[0]
            if permission['role'] != 'writer':
                raise IngestSpreadsheetError.SpreadsheetPermissionError()
            worksheet = spreadsheet.worksheet('Agenda for ingest')
            return worksheet
        except (json.decoder.JSONDecodeError, ValueError):
            raise IngestSpreadsheetError.SpreadsheetCredentialsError()
        except gspread.exceptions.NoValidUrlKeyFound:
            raise IngestApiError.apiNotFoundError()
        except gspread.exceptions.WorksheetNotFound:
            raise ParserError.parseFileError()
        except gspread.exceptions.APIError as e:
            response_code = e.response.json()['error']['code']
            if response_code == 403:
                raise IngestSpreadsheetError.SpreadsheetPermissionError()
            elif response_code == 429:
                raise IngestSpreadsheetError.SpreadsheetQuotaLimit()
            else:
                raise IngestApiError.apiNotFoundError()


register_feeding_service(SpreadsheetFeedingService)
