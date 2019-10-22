import hmac
import uuid
import arrow
import hashlib
import requests
import datetime
import superdesk

from urllib.parse import urljoin
from superdesk.utc import local_to_utc
from superdesk.utils import ListCursor
from superdesk.text_utils import get_text as _get_text

BELGA_TZ = 'Europe/Brussels'


def get_text(value, strip_html=True):
    try:
        text = value.strip()
        if strip_html:
            text = _get_text(text, lf_on_block=True)
        return text
    except AttributeError:
        return ''


def get_datetime(value):
    dt = arrow.get(value).datetime
    return local_to_utc(BELGA_TZ, dt)


class BelgaListCursor(ListCursor):

    def __init__(self, docs, count):
        super().__init__(docs)
        self._count = count

    def count(self, **kwargs):
        return self._count


class BelgaImageSearchProvider(superdesk.SearchProvider):

    GUID_PREFIX = 'urn:belga.be:image:'

    label = 'Belga Image'
    base_url = 'https://api.ssl.belga.be/belgaimage-api/'
    search_endpoint = 'searchImages'
    items_field = 'images'
    count_field = 'nrImages'

    def __init__(self, provider, **kwargs):
        super().__init__(provider, **kwargs)
        self.session = requests.Session()
        self._id_token = None
        self._auth_token = None
        if self.provider.get('config') and self.provider['config'].get('username'):
            self.auth()

    def auth_headers(self, url, secret=None):
        if not secret and not self._id_token:
            return {}
        nonce = uuid.uuid4().hex
        return {
            'X-Date': nonce,
            'X-Identification': '{}:{}'.format(
                self.provider['config']['username'],
                self._hash(url, nonce, secret or self._id_token)
            ),
            'X-Authorization': '{}:{}'.format(
                self.provider['config']['username'],
                self._hash(url, nonce, secret or self._auth_token),
            ),
        }

    def _hash(self, url, now, secret):
        return hmac.new(
            secret.encode(),
            '/{}+{}'.format(url.lstrip('/'), now).encode(),
            hashlib.sha256,
        ).hexdigest()

    def auth(self):
        url = '/authorizeUser?l={}'.format(self.provider['config']['username'])
        headers = self.auth_headers(url, self.provider['config'].get('password'))
        resp = self.session.get(self.url(url), headers=headers)
        resp.raise_for_status()
        if resp.status_code == 200 and resp.content:
            data = resp.json()
            self._id_token = data.get('idToken')
            self._auth_token = data.get('authToken')

    def url(self, resource):
        return urljoin(self.base_url, resource.lstrip('/'))

    def find(self, query, params=None):
        api_params = {
            's': query.get('from', 0),
            'l': query.get('size', 25),
        }

        if params:
            for api_param, param in {'c': 'source', 'h': 'subject'}.items():
                items = [key for key, val in params.get(param, {}).items() if val]
                if items:
                    api_params[api_param] = ','.join(items)
            if params.get('period'):
                api_params['p'] = params['period'].upper()

        try:
            query_string = query['query']['filtered']['query']['query_string']['query']
            query_string_parts = query_string.strip().replace('  ', ' ').split()
            if query_string_parts:
                api_params['t'] = ' AND '.join(query_string_parts)
        except KeyError:
            pass

        data = self.api_get(self.search_endpoint, api_params)
        docs = [self.format_list_item(item) for item in data[self.items_field]]
        return BelgaListCursor(docs, data[self.count_field])

    def api_get(self, endpoint, params):
        url = requests.Request('GET', 'http://example.com/' + endpoint, params=params).prepare().path_url
        headers = self.auth_headers(url)
        resp = self.session.get(self.url(url), headers=headers)
        resp.raise_for_status()
        return resp.json()

    def fetch(self, guid):
        _id = guid.replace(self.GUID_PREFIX, '')
        params = {'i': _id}
        data = self.api_get('/getImageById', params)
        return self.format_list_item(data)

    def format_list_item(self, data):
        guid = '%s%d' % (self.GUID_PREFIX, data['imageId'])
        created = get_datetime(data['createDate'])
        return {
            'type': 'picture',
            'pubstatus': 'usable',
            '_id': guid,
            'guid': guid,
            'headline': get_text(data['name']),
            'description_text': get_text(data['caption']),
            'versioncreated': created,
            'firstcreated': created,
            'byline': get_text(data.get('author')) or get_text(data['userId']),
            'creditline': get_text(data['credit']),
            'source': get_text(data['credit']),
            'renditions': {
                'original': {
                    'width': data['width'],
                    'height': data['height'],
                    'href': data['detailUrl'],
                },
                'thumbnail': {
                    'href': data['smallUrl'],
                },
                'viewImage': {
                    'href': data['previewUrl'],
                },
                'baseImage': {
                    'href': data['detailUrl'],
                },
            }
        }


class BelgaCoverageSearchProvider(BelgaImageSearchProvider):

    GUID_PREFIX = 'urn:belga.be:coverage:'

    label = 'Belga Coverage'
    search_endpoint = 'searchGalleries'
    items_field = 'galleries'
    count_field = 'nrGalleries'

    def format_list_item(self, data):
        guid = '%s%d' % (self.GUID_PREFIX, data['galleryId'])
        created = get_datetime(data['createDate'])
        thumbnail = data['iconThumbnailUrl']
        return {
            'type': 'graphic',
            'mimetype': 'application/vnd.belga.coverage',
            'pubstatus': 'usable',
            '_id': guid,
            'guid': guid,
            'headline': get_text(data['name']),
            'description_text': get_text(data.get('description')),
            'versioncreated': created,
            'firstcreated': created,
            'byline': get_text(data.get('author')) or get_text(data.get('userId')),
            'creditline': get_text(data['credit']),
            'source': get_text(data['credit']),
            'renditions': {
                'original': {
                    'href': thumbnail,
                },
                'thumbnail': {
                    'href': thumbnail,
                },
                'viewImage': {
                    'href': thumbnail,
                },
                'baseImage': {
                    'href': thumbnail,
                },
            },
            'extra': {
                'bcoverage': guid,
            },
        }


class Belga360ArchiveSearchProvider(superdesk.SearchProvider):

    GUID_PREFIX = 'urn:belga.be:360archive:'

    label = 'Belga 360 Archive'
    base_url = 'http://mules.staging.belga.be:48080/belga360-ws/'
    search_endpoint = 'archivenewsobjects'
    items_field = 'newsObjects'
    count_field = 'nrNewsObjects'

    def __init__(self, provider):
        super().__init__(provider)
        self.session = requests.Session()

    def url(self, resource):
        return urljoin(self.base_url, resource.lstrip('/'))

    def find(self, query, params=None):
        api_params = {
            'start': query.get('from', 0),
            'pageSize': query.get('size', 25),
        }

        try:
            api_params['searchText'] = query['query']['filtered']['query']['query_string']['query']
        except KeyError:
            api_params['searchText'] = ''

        data = self.api_get(self.search_endpoint, api_params)
        docs = [self.format_list_item(item) for item in data[self.items_field]]
        return BelgaListCursor(docs, data[self.count_field])

    def fetch(self, guid):
        _id = guid.replace(self.GUID_PREFIX, '')
        data = self.api_get(self.search_endpoint + '/' + _id, {})
        return self.format_list_item(data)

    def api_get(self, endpoint, params):
        resp = self.session.get(self.url(endpoint), params=params)
        resp.raise_for_status()
        return resp.json()

    def _get_newscomponent(self, item, component):
        components = [i for i in item.get('newsComponents', []) if i.get('assetType', '').lower() == component.lower()]
        try:
            return components[0]['proxies'][0]['varcharData']
        except (KeyError, IndexError):
            return ''

    def _get_body_html(self, item):
        return self._get_newscomponent(item, 'body')

    def _get_abstract(self, item):
        return self._get_newscomponent(item, 'lead')

    def format_list_item(self, data):
        guid = '%s%d' % (self.GUID_PREFIX, data['newsObjectId'])
        assets = ('picture',)
        asset_type = get_text(data['assetType']).lower()
        created = get_datetime(datetime.datetime.now())
        return {
            'type': asset_type if asset_type in assets else 'text',
            'mimetype': 'application/vnd.belga.360archive',
            'pubstatus': 'usable',
            '_id': guid,
            'guid': guid,
            'headline': get_text(data['headLine']),
            'name': get_text(data['name']),
            'description_text': get_text(data.get('description')),
            'versioncreated': created,
            'firstcreated': created,
            'creditline': get_text(data['credit']),
            'source': get_text(data['source']),
            'language': get_text(data['language']),
            'abstract': get_text(self._get_abstract(data)),
            'body_html': get_text(self._get_body_html(data)),
            'extra': {
                'bcoverage': guid,
            },
        }


def init_app(app):
    superdesk.register_search_provider('belga_image', provider_class=BelgaImageSearchProvider)
    superdesk.register_search_provider('belga_coverage', provider_class=BelgaCoverageSearchProvider)
    superdesk.register_search_provider('belga_360archive', provider_class=Belga360ArchiveSearchProvider)
