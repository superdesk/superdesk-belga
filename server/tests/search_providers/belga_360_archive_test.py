import os
import arrow
import superdesk

from pytz import utc
from flask import json
from datetime import datetime
from httmock import all_requests, HTTMock
from unittest.mock import patch, MagicMock
from belga.search_providers import Belga360ArchiveSearchProvider, TIMEOUT
from superdesk.tests import TestCase


def fixture(filename):
    return os.path.join(os.path.dirname(__file__), '..', 'fixtures', filename)


class DetailResponse():
    status_code = 200

    def raise_for_status(self):
        pass


@all_requests
def archive_mock(url, request):
    with open(fixture('belga-360archive-search.json')) as _file:
        return _file.read()


def get_belga360_item():
    with open(fixture('belga-360archive-search.json')) as _file:
        items = json.load(_file)
        return items['newsObjects'][0]


class Belga360ArchiveTestCase(TestCase):
    def setUp(self):
        self.provider = Belga360ArchiveSearchProvider(dict())
        self.query = {
            'size': 50,
            'from': 50,
            'query': {
                'filtered': {
                    'query': {
                        'query_string': {
                            'query': 'test query'
                        },
                    },
                },
            },
        }

    def test_instance(self):
        self.assertEqual('Belga 360 Archive', self.provider.label)
        self.assertIsInstance(self.provider, superdesk.SearchProvider)

    @patch('belga.search_providers.session.get')
    def test_find_params(self, session_get):
        params = {
            'credits': 'afp',
            'dates': {'start': '02/02/2020', 'end': '14/02/2020'},
            'languages': 'en',
            'types': 'Short',
        }
        self.provider.find(self.query, params)
        url = self.provider.base_url + 'archivenewsobjects'
        params = {
            'start': 50, 'pageSize': 50, 'language': 'en', 'assetType': 'Short', 'credits': 'AFP',
            'fromDate': '20200202', 'toDate': '20200214', 'searchText': 'test query',
        }
        session_get.assert_called_with(url, params=params, timeout=TIMEOUT)

    def test_format_list_item(self):
        self.app.data.insert(
            'content_types',
            [{'_id': 'text', 'label': 'text'}]
        )
        # reload content profiles
        self.provider = Belga360ArchiveSearchProvider(dict())
        item = self.provider.format_list_item(get_belga360_item())
        guid = 'urn:belga.be:360archive:39670442'
        self.assertEqual(item['type'], 'text')
        self.assertEqual(item['mimetype'], 'application/superdesk.item.text')
        self.assertEqual(item['_id'], guid)
        self.assertEqual(item['state'], 'published')
        self.assertEqual(item['profile'], 'text')
        self.assertEqual(item['guid'], guid)
        self.assertEqual(item['extra']['bcoverage'], guid)
        self.assertEqual(item['headline'], 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.')
        self.assertEqual(item['name'], '')
        self.assertEqual(item['slugline'], 'Belga 360 slugline')
        self.assertEqual(item['description_text'], '')
        self.assertEqual(item['creditline'], 'BELGA')
        self.assertEqual(item['source'], 'BELGA')
        self.assertEqual(item['language'], 'fr')
        self.assertEqual(item['firstcreated'], datetime.fromtimestamp(1581646440, utc))
        self.assertEqual(item['versioncreated'], datetime.fromtimestamp(1581654480, utc))
        self.assertEqual(item['keywords'], ['VS', 'HOCKEY', 'BRIEF', 'OS2022', 'GEZONDHEID', '#CORONAVIRUS', 'SPORTS'])
        self.assertEqual(item['sign_off'], 'BRV/Author')
        self.assertEqual(item['body_html'], (
            'Vivamus rutrum sapien a purus posuere eleifend. Integer non feugiat sapien. Proin'
            ' finibus diam in urna vehicula accumsan<br/><br/>'
            '&nbsp;&nbsp;&nbsp;&nbsp;'
            'Morbi lacus ex, molestie id ullamcorper quis co&v scelerisque quis lectus.<br/>&nbsp;&nbsp;&nbsp;&nbsp;'
            ' Phasellus laoreet turpis nunc, vitae porttitor sapien ultricies non.<br/>&nbsp;&nbsp;&nbsp;&nbsp;'
            ' Nullam fringilla justo vitae ex commodo vulputate.<br/>&nbsp;&nbsp;&nbsp;&nbsp;'
            ' In bibendum diam vitae condimentum scelerisque.<br/>&nbsp;&nbsp;&nbsp;&nbsp;'
            ' Integer dapibus turpis augue, a varius diam ornare in.<br/>&nbsp;&nbsp;&nbsp;&nbsp;'
            ' Donec aliquam cursus posuere.'
        ))
        self.assertFalse(item['_fetchable'])

    def test_find_item(self):
        with HTTMock(archive_mock):
            items = self.provider.find(self.query)
        self.assertEqual(len(items.docs), 2)
        self.assertEqual(items._count, 25000)

    @patch('belga.search_providers.session.get')
    def test_fetch(self, session_get):
        response = DetailResponse()
        response.json = MagicMock(return_value=get_belga360_item())
        session_get.return_value = response

        item = self.provider.fetch('urn:belga.be:360archive:39670442')

        url = self.provider.base_url + 'archivenewsobjects/39670442'
        session_get.assert_called_with(url, params={}, timeout=TIMEOUT)

        self.assertEqual('urn:belga.be:360archive:39670442', item['guid'])

    def test_get_periods(self):
        arrow.now = MagicMock(return_value=arrow.get('2020-02-14'))
        day_period = self.provider._get_period('day')
        self.assertEqual(day_period['fromDate'], '20200213')
        self.assertEqual(day_period['toDate'], '20200214')

        def get_period(period):
            return self.provider._get_period(period)['fromDate']

        self.assertEqual(get_period('week'), '20200207')
        self.assertEqual(get_period('month'), '20200114')
        self.assertEqual(get_period('year'), '20190214')
