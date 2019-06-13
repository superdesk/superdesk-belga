#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from datetime import timedelta
from pathlib import Path

import gspread
from gspread import Cell
from dateutil.parser import parse
from oauth2client.service_account import ServiceAccountCredentials
from pytz import timezone
from pytz.exceptions import UnknownTimeZoneError
from tzlocal import get_localzone

from superdesk.errors import IngestApiError, ParserError, SuperdeskIngestError
from superdesk.io.feeding_services import FeedingService
from superdesk.io.registry import register_feeding_service
from superdesk.metadata.item import CONTENT_STATE, GUID_NEWSML, ITEM_STATE
from superdesk.metadata.utils import generate_guid

logger = logging.getLogger(__name__)


class IngestSpreadsheetError(SuperdeskIngestError):
    _codes = {
        15100: "Missing permission",
        15200: "Quota limit",
    }

    @classmethod
    def SpreadsheetPermissionError(cls, exception=None, provider=None):
        return IngestSpreadsheetError(15100, exception, provider)

    @classmethod
    def SpreadsheetQuotaLimit(cls, exception=None, provider=None):
        return IngestSpreadsheetError(15200, exception, provider)


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

    titles = [
        'Start date', 'Start time', 'End date', 'End time', 'All day', 'Timezone', 'Slugline', 'Event name',
        'Description', 'Occurence status', 'Calendars', 'Location Name', 'Location Address', 'Location City/Town',
        'Location State/Province/Region', 'Location Country', 'Contact Honorific', 'Contact First name',
        'Contact Last name', 'Contact Organisation', 'Contact Point of Contact', 'Contact Email',
        'Contact Phone Number', 'Contact Phone Usage', 'Contact Phone Public', 'Long description', 'Internal note',
        'Ed note', 'External links',
    ]

    required_field = [
        'slugline', 'calendars', 'name',
    ]

    required_contact_field = ['Contact Email', 'Contact Phone Number']
    required_location_field = ['Location Name', 'Location Address', 'Location Country']

    occur_status_qcode_mapping = {
        'Unplanned event': 'eocstat:eos0',
        'Planned, occurrence planned only': 'eocstat:eos1',
        'Planned, occurrence highly uncertain': 'eocstat:eos2',
        'Planned, May occur': 'eocstat:eos3',
        'Planned, occurrence highly likely': 'eocstat:eos4',
        'Planned, occurs certainly': 'eocstat:eos5',
    }

    def _test(self, provider):
        return self._update(provider, update=None, test=True)

    def _update(self, provider, update, test=False):
        """ Load items from google spreadsheet

        If STATUS or GUID field is null, create new item
        If STATUS field is UPDATED, update item with new value
        Find and update Contact based on all field in required_contact_field, create new record if not found
        Find and update Location based on all field in required_location_field, create new record if not found
        """
        config = provider.get('config', {})
        url = config.get('url', '')
        worksheet = self._get_worksheet(url)
        try:
            # Get all values to avoid reaching read limit
            data = worksheet.get_all_values()
            # lookup title columns in case it's not followed order
            index = {}
            titles = [s.lower().strip() for s in data[0]]
            for field in self.titles:
                if field.lower().strip() not in titles:
                    raise ParserError.parseFileError()
                index[field] = titles.index(field.lower().strip())

            # avoid exceed row/col limits error
            if len(titles) <= len(self.titles) + 2:
                worksheet.add_cols(2)

            for i, field in enumerate(('STATUS', 'GUID'), len(self.titles)):
                if field.lower().strip() in titles:
                    index[field] = titles.index(field.lower().strip())
                else:
                    worksheet.update_cell(1, i, field)
                    index[field] = i

            items = []
            cells_list = []
            # skip first two title rows
            for row in range(3, len(data) + 1):
                if not row:
                    break
                values = data[row - 1]
                is_updated = None if len(values) < index['STATUS'] else values[index['STATUS']].strip().upper()
                if len(values) - 1 > index['GUID'] and values[index['GUID']]:
                    guid = values[index['GUID']]
                else:
                    guid = generate_guid(type=GUID_NEWSML)
                try:
                    # avoid momentsJS throw none timezone value error
                    tzone = values[index['Timezone']] if values[index['Timezone']] != 'none' else str(get_localzone())
                    tz = timezone(tzone)
                    start_datetime = tz.localize(parse(values[index['Start date']] + ' ' + values[index['Start time']]))
                    end_date = values[index['End date']]
                    if values[index['All day']] == 'TRUE':
                        # set end datetime to the end of start date
                        end_datetime = tz.localize(parse(values[index['Start date']])) + timedelta(days=1, seconds=-1)
                    else:
                        end_datetime = tz.localize(parse(end_date + ' ' + values[index['End time']]))
                    item = {
                        'type': 'event',
                        'name': values[index['Event name']],
                        'slugline': values[index['Slugline']],
                        'dates': {
                            'start': start_datetime,
                            'end': end_datetime,
                            'tz': tzone,
                        },
                        'occur_status': {
                            'qcode': self.occur_status_qcode_mapping[values[index['Occurence status']]],
                            'name': values[index['Occurence status']],
                            'label': values[index['Occurence status']].lower(),
                        },
                        'definition_short': values[index['Description']],
                        'definition_long': values[index['Long description']],
                        'internal_note': values[index['Internal note']],
                        'ednote': values[index['Ed note']],
                        'links': values[index['External links']],
                        'guid': guid,
                        'status': is_updated,
                        'version': 1,
                    }
                    calendars = values[index['Calendars']]
                    if calendars:
                        item['calendars'] = [{
                            'is_active': True,
                            'name': calendars,
                            'qcode': calendars.lower(),
                        }]

                    if all(values[index[field]] for field in self.required_location_field):
                        item['location'] = [{
                            'name': values[index['Location Name']],
                            'address': {
                                'line': [values[index['Location Address']]],
                                'locality': values[index['Location City/Town']],
                                'area': values[index['Location State/Province/Region']],
                                'country': values[index['Location Country']],
                            }
                        }]
                    if all(values[index[field]] for field in self.required_contact_field) \
                        and (
                            all(values[index[field]] for field in ['Contact First name', 'Contact Last name'])
                            or values[index['Contact Organisation']]):
                        is_public = values[index['Contact Phone Public']] == 'TRUE'
                        if values[index['Contact Phone Usage']] == 'Confidential':
                            is_public = False
                        item['contact'] = {
                            'honorific': values[index['Contact Honorific']],
                            'first_name': values[index['Contact First name']],
                            'last_name': values[index['Contact Last name']],
                            'organisation': values[index['Contact Organisation']],
                            'contact_email': [values[index['Contact Email']]],
                            'contact_phone': [{
                                'number': values[index['Contact Phone Number']],
                                'public': is_public,
                                'usage': values[index['Contact Phone Usage']],
                            }]
                        }
                    item.setdefault(ITEM_STATE, CONTENT_STATE.DRAFT)
                    # ignore invalid item
                    missing_fields = [field for field in self.required_field if not item.get(field)]
                    if not missing_fields:
                        if not is_updated or is_updated == 'UPDATED':
                            cells_list.append(Cell(row, index['STATUS'] + 1, 'DONE'))
                        cells_list.append(Cell(row, index['GUID'] + 1, guid))
                        items.append(item)
                    else:
                        logger.error(
                            'Provider %s: Ignore event "%s". Missing %s fields',
                            provider.get('name'), item.get('name'), ', '.join(missing_fields),
                        )
                except TypeError as e:
                    logger.error(e)
                except UnknownTimeZoneError:
                    logger.error(
                        'Provider %s: Event "%s": Invalid timezone %s',
                        provider.get('name'), values[index['Event name']], tzone
                    )
            worksheet.update_cells(cells_list)
            return [items]
        except gspread.exceptions.CellNotFound:
            raise ParserError.parseFileError()

    def _get_worksheet(self, url):
        """Get worksheet from google spreadsheet

        :return: worksheet
        :rtype: object

        :raises IngestSpreadsheetError
        """
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
        ]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(Path('serviceAccount.json'), scope)
        gc = gspread.authorize(credentials)
        try:
            spreadsheet = gc.open_by_url(url)
            permission = spreadsheet.list_permissions()[0]
            if permission['role'] != 'writer':
                raise IngestSpreadsheetError.SpreadsheetPermissionError()
            worksheet = spreadsheet.worksheet('Agenda for ingest')
            return worksheet
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
