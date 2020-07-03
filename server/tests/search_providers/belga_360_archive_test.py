import os
import superdesk

import arrow
from flask import json
from httmock import all_requests, HTTMock
from unittest.mock import MagicMock
from belga.search_providers import Belga360ArchiveSearchProvider, get_datetime
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

    def test_find_params(self):
        params = {
            'credits': 'afp',
            'dates': {'start': '02/02/2020', 'end': '14/02/2020'},
            'languages': 'en',
            'types': 'Short',
        }
        self.provider.session.get = MagicMock()
        self.provider.find(self.query, params)
        url = self.provider.base_url + 'archivenewsobjects'
        params = {
            'start': 50, 'pageSize': 50, 'language': 'en', 'assetType': 'Short', 'credits': 'AFP',
            'fromDate': '20200202', 'toDate': '20200214', 'searchText': 'test query',
        }
        self.provider.session.get.assert_called_with(url, params=params)

    def test_format_list_item(self):
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
        self.assertEqual(item['firstcreated'], get_datetime(1581646440))
        self.assertEqual(item['versioncreated'], get_datetime(1581654480))
        self.assertEqual(item['abstract'], (
            'Vivamus rutrum sapien a purus posuere eleifend. Integer non feugiat sapien. Proin'
            ' finibus diam in urna vehicula accumsan'
        ))
        self.assertEqual(item['body_html'], (
            '&nbsp;&nbsp;&nbsp;&nbsp;'
            'Morbi lacus ex, molestie id ullamcorper quis, scelerisque quis lectus.<br/>&nbsp;&nbsp;&nbsp;&nbsp;'
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

    def test_fetch(self):
        response = DetailResponse()
        response.json = MagicMock(return_value=get_belga360_item())
        self.provider.session.get = MagicMock(return_value=response)

        item = self.provider.fetch('urn:belga.be:360archive:39670442')

        url = self.provider.base_url + 'archivenewsobjects/39670442'
        self.provider.session.get.assert_called_with(url, params={})

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
