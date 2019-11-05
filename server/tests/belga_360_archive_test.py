import os
import hmac
import hashlib
import unittest
import requests
import superdesk

from flask import json
from httmock import all_requests, HTTMock
from unittest.mock import MagicMock

from belga.search_providers import Belga360ArchiveSearchProvider


def fixture(filename):
    return os.path.join(os.path.dirname(__file__), 'fixtures', filename)


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


class Belga360ArchiveTestCase(unittest.TestCase):
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
        self.provider.session.get = MagicMock()
        self.provider.find(self.query)
        url = self.provider.base_url + 'archivenewsobjects'
        params = {'start': 50, 'pageSize': 50, 'searchText': 'test query'}
        self.provider.session.get.assert_called_with(url, params=params)

    def test_format_list_item(self):
        item = self.provider.format_list_item(get_belga360_item())
        guid = 'urn:belga.be:360archive:39670442'
        self.assertEqual(item['type'], 'text')
        self.assertEqual(item['mimetype'], 'application/vnd.belga.360archive')
        self.assertEqual(item['_id'], guid)
        self.assertEqual(item['guid'], guid)
        self.assertEqual(item['extra']['bcoverage'], guid)
        self.assertEqual(item['headline'], 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.')
        self.assertEqual(item['name'], '')
        self.assertEqual(item['description_text'], '')
        self.assertEqual(item['creditline'], 'BELGA')
        self.assertEqual(item['source'], 'BELGA')
        self.assertEqual(item['language'], 'fr')
        self.assertEqual(item['abstract'], (
            'Vivamus rutrum sapien a purus posuere eleifend. Integer non feugiat sapien. Proin'
            ' finibus diam in urna vehicula accumsan'
        ))
        self.assertEqual(item['body_html'], (
            'Morbi lacus ex, molestie id ullamcorper quis, scelerisque quis lectus.\n'
            ' Phasellus laoreet turpis nunc, vitae porttitor sapien ultricies non.\n'
            ' Nullam fringilla justo vitae ex commodo vulputate.\n In bibendum diam vitae condimentum scelerisque.\n'
            ' Integer dapibus turpis augue, a varius diam ornare in.\n Donec aliquam cursus posuere.'
        ))

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
