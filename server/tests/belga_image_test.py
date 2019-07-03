import os
import hmac
import hashlib
import unittest
import requests
import superdesk

from flask import json
from httmock import all_requests, HTTMock
from unittest.mock import MagicMock

from belga.image import BelgaImageSearchProvider


def fixture(filename):
    return os.path.join(os.path.dirname(__file__), 'fixtures', filename)


@all_requests
def search_mock(url, request):
    with open(fixture('belga-image-search.json')) as _file:
        return _file.read()


class DetailResponse():

    status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        with open(fixture('belga-image-by-id.json')) as _file:
            return json.load(_file)


class BelgaImageTestCase(unittest.TestCase):

    def test_instance(self):
        provider = BelgaImageSearchProvider(dict())
        self.assertEqual('Belga Image', provider.label)
        self.assertIsInstance(provider, superdesk.SearchProvider)

    def test_find_items(self):
        query = {}
        provider = BelgaImageSearchProvider(dict())
        with HTTMock(search_mock):
            items = provider.find(query)
        self.assertEqual(83681621, items.count(with_limit_and_skip=False))

        item = items[0]
        self.assertEqual('picture', item['type'])
        self.assertEqual('usable', item['pubstatus'])
        self.assertEqual('urn:belga.be:image:143831778', item['_id'])
        self.assertEqual('urn:belga.be:image:143831778', item['guid'])
        self.assertEqual("signature d'une convention entre l'agglo Val de sambre et la SA", item['headline'])
        self.assertIn('©PHOTOPQR/VOIX', item['description_text'])
        self.assertEqual('2019-01-08T12:32:06+00:00', item['versioncreated'].isoformat())
        self.assertEqual('2019-01-08T12:32:06+00:00', item['firstcreated'].isoformat())
        self.assertEqual('MAXPPP', item['creditline'])
        self.assertEqual('MAXPPP', item['source'])
        self.assertEqual('MEFYJJ', item['byline'])

        renditions = item['renditions']
        self.assertIn('original', renditions)
        self.assertIn('thumbnail', renditions)
        self.assertIn('viewImage', renditions)
        self.assertIn('baseImage', renditions)

        self.assertIn('600x140', renditions['thumbnail']['href'])
        self.assertIn('800x800', renditions['viewImage']['href'])
        self.assertIn('1800x650', renditions['baseImage']['href'])
        self.assertIn('1800x650', renditions['original']['href'])

        # orig
        self.assertEqual(4300, renditions['original']['width'])
        self.assertEqual(2868, renditions['original']['height'])

    def test_find_params(self):
        query = {
            'size': 20,
            'from': 10,
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

        params = {
            'source': {
                'belga': True,
                'ansa': True,
                'afp': False,
            },
            'subject': {
                'news': True,
                'sports': True,
                'finance': False,
            },
            'period': 'today',
        }

        provider = BelgaImageSearchProvider(dict())
        provider.session.get = MagicMock()

        provider.find(query, params)

        url = requests.Request('GET', provider.base_url + 'searchImages', params={
            's': 10,
            'l': 20,
            'c': 'belga,ansa',
            'h': 'news,sports',
            'p': 'TODAY',
            't': 'test AND query',
        }).prepare().url
        provider.session.get.assert_called_with(url, headers={})

    def test_fetch(self):
        provider = BelgaImageSearchProvider(dict())
        provider.session.get = MagicMock(return_value=DetailResponse())

        item = provider.fetch('urn:belga.be:image:143831778')

        url = requests.Request('GET', provider.base_url + 'getImageById', params={
            'i': '143831778',
        }).prepare().url
        provider.session.get.assert_called_with(url, headers={})

        self.assertEqual('urn:belga.be:image:143831778', item['guid'])
        self.assertEqual('Belloumi', item['byline'])

    def test_auth_headers(self):
        provider = BelgaImageSearchProvider(dict())
        provider.provider['config'] = {'username': 'john', 'password': 'pwd'}
        headers = provider.auth_headers('/test', 'pwd')
        self.assertIn('X-Date', headers)
        self.assertEqual(
            headers['X-Authorization'],
            'john:{}'.format(
                hmac.new(
                    'pwd'.encode(),
                    '/test+{}'.format(headers['X-Date']).encode(),
                    hashlib.sha256,
                ).hexdigest(),
            )
        )
