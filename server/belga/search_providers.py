import hmac
import time
import uuid
import arrow
import hashlib
import requests
import superdesk
import logging

from pytz import utc
from datetime import datetime
from urllib.parse import urljoin
from typing import Any, Dict, Optional
from superdesk.utc import local_to_utc
from superdesk.utils import ListCursor
from superdesk.text_utils import get_text as _get_text

BELGA_TZ = 'Europe/Brussels'
TIMEOUT = (5, 30)

logger = logging.getLogger(__name__)
session = requests.Session()


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
        self._id_token = None
        self._auth_token = None
        if self.provider.get('config') and self.provider['config'].get('username'):
            self.auth()

    def auth_headers(self, url, secret=None, nonce=None):
        if not secret and not self._id_token:
            return {}
        if not nonce:
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
        resp = session.get(self.url(url), headers=headers, timeout=TIMEOUT)
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
                    api_params[api_param] = ','.join(sorted(items))  # avoid random sort breaking test

            dates = params.get('dates', {})
            if dates.get('start'):
                api_params['f'] = arrow.get(dates['start'], 'DD/MM/YYYY').timestamp * 1000
            if dates.get('end'):
                api_params['e'] = arrow.get(dates['end'], 'DD/MM/YYYY').timestamp * 1000

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
        headers = self.auth_headers(url.replace('%2C', ','))  # decode spaces
        resp = session.get(self.url(url), headers=headers, timeout=TIMEOUT)
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
            },
            '_fetchable': False,
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
            '_fetchable': False,
        }


class Belga360ArchiveSearchProvider(superdesk.SearchProvider):

    GUID_PREFIX = 'urn:belga.be:360archive:'

    label = 'Belga 360 Archive'
    base_url = 'http://mules.staging.belga.be:48080/belga360-ws/'
    search_endpoint = 'archivenewsobjects'
    items_field = 'newsObjects'
    count_field = 'nrNewsObjects'
    TYPE_SUPPORT = ('Text', 'Brieft', 'Alert', 'Short')
    PERIODS = {
        'day': {'days': -1},
        'week': {'weeks': -1},
        'month': {'months': -1},
        'year': {'years': -1},
    }

    def __init__(self, provider):
        super().__init__(provider)
        self.content_types = {
            c['_id'] for c in superdesk.get_resource_service('content_types').find({})
        }

    def url(self, resource):
        return urljoin(self.base_url, resource.lstrip('/'))

    def find(self, query, params=None):
        api_params = {
            'start': query.get('from', 0),
            'pageSize': query.get('size', 25),
        }

        if params:
            if params.get('languages'):
                api_params['language'] = params['languages'].lower()

            api_params['assetType'] = ' OR '.join([
                _type for _type in self.TYPE_SUPPORT
                if not params.get('types') or params['types'].lower() == _type.lower()
            ])

            if params.get('credits'):
                api_params['credits'] = params['credits'].strip().upper()

            dates = params.get('dates', {})
            if dates.get('start'):
                api_params['fromDate'] = self._get_belga_date(dates['start'])
            if dates.get('end'):
                api_params['toDate'] = self._get_belga_date(dates['end'])

            period = params.get('period')
            if period and self.PERIODS.get(period):
                # override value of search by date
                api_params.update(self._get_period(period))

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
        resp = session.get(self.url(endpoint), params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def _get_belga_date(self, date):
        try:
            return arrow.get(date, 'DD/MM/YYYY').format('YYYYMMDD')
        except arrow.parser.ParserError:
            return ''

    def _get_period(self, period):
        today = arrow.now(superdesk.app.config['DEFAULT_TIMEZONE'])
        return {
            'fromDate': today.shift(**self.PERIODS.get(period)).format('YYYYMMDD'),
            'toDate': today.format('YYYYMMDD'),
        }

    def _get_newscomponent(self, item, component):
        components = [i for i in item.get('newsComponents', []) if i.get('assetType', '').lower() == component.lower()]
        try:
            return components[0]['proxies'][0]['varcharData']
        except (KeyError, IndexError):
            return ''

    def _get_body_html(self, item):
        # SDBELGA-393
        body = '&nbsp;&nbsp;&nbsp;&nbsp;' + get_text(self._get_newscomponent(item, 'body'))
        return body.replace('\n', '<br/>&nbsp;&nbsp;&nbsp;&nbsp;')

    def _get_abstract(self, item):
        return self._get_newscomponent(item, 'lead')

    def _get_datetime(self, date=None):
        if not date:
            date = time.time()
        else:
            date = date / 1000
        return datetime.fromtimestamp(date, utc)

    def _get_profile(self, profile):
        label = profile.lower()
        if label == 'short':
            label = 'text'
        if label not in self.content_types:
            return
        return label

    def format_list_item(self, data):
        guid = '%s%d' % (self.GUID_PREFIX, data['newsObjectId'])
        return {
            'type': 'text',
            'mimetype': 'application/superdesk.item.text',
            'pubstatus': 'usable',
            '_id': guid,
            'state': 'published',
            'guid': guid,
            'profile': self._get_profile(data.get('assetType', '')),
            'headline': get_text(data['headLine']),
            'slugline': get_text(data['topic']),
            'name': get_text(data['name']),
            'description_text': get_text(data.get('description')),
            'versioncreated': self._get_datetime(data.get('validateDate')),
            'firstcreated': self._get_datetime(data.get('createDate')),
            'creditline': get_text(data['credit']),
            'source': get_text(data['source']),
            'language': get_text(data['language']),
            'abstract': get_text(self._get_abstract(data)),
            'body_html': self._get_body_html(data),
            'extra': {
                'bcoverage': guid,
            },
            '_fetchable': False,
        }


class BelgaPressSearchProvider(superdesk.SearchProvider):

    GUID_PREFIX = 'urn:belga.be:belgapress:'

    label = 'Belga Press'
    base_url = 'https://bp-api.ssl.belga.be/belgapress/api'
    search_endpoint = 'newsobjects'
    items_field = 'data'
    openid_provider_url = 'https://sso.ssl.belga.be/auth/realms/belga/protocol/openid-connect/token'
    PERIODS = {
        'day': {'days': 0},
        'yesterday': {'days': -1},
        'this-week': {'weekday': 0, 'days': -7},
        'week': {'weeks': -1},
        'month': {'months': -1},
        'year': {'years': -1},
    }

    def __init__(self, provider: Dict[str, Dict], **kwargs):
        super().__init__(provider, **kwargs)
        self._access_token = None
        config = provider.get('config', {})
        if config.get('username') and config.get('password'):
            self.auth()

    def auth(self):
        resp = session.post(f'{self.openid_provider_url}?scope=openid%20profile', data={
            'client_id': self.provider.get('config', {}).get('username'),
            'client_secret': self.provider.get('config', {}).get('password'),
            'grant_type': 'client_credentials'
        }, timeout=TIMEOUT)
        resp.raise_for_status()
        if resp.status_code == 200 and resp.content:
            data = resp.json()
            self._access_token = data.get('access_token')

    def find(self, query: Dict[str, Any], params: Optional[Dict] = None):
        api_params = {
            'offset': query.get('from', 0),
            'count': query.get('size', 25),
        }

        if params:
            for api_param, param in {'mediumtypegroup': 'types', 'language': 'languages'}.items():
                if params.get(param):
                    api_params[api_param] = params.get(param)

            period = params.get('period')
            if period and self.PERIODS.get(period):
                api_params.update(self._get_period(period))

            date = params.get('dates', {})
            if date.get('start'):
                start_date = arrow.get(date['start'], 'DD/MM/YYYY')
                api_start_date = api_params.get('start')
                # if period is set, only override start param when date start is greater than period start date
                if not api_start_date or (api_start_date and start_date > arrow.get(api_start_date)):
                    api_params['start'] = start_date.format('YYYY-MM-DD')

            if date.get('end'):
                api_params['end'] = arrow.get(date['end'], 'DD/MM/YYYY').format('YYYY-MM-DD')

        api_params['order'] = '-PUBLISHDATE'
        # Only check if current sorting is ascending or descending because Belga Press API order parameter
        # is not compatiable with Superdesk sorting criteria
        sort = next(iter(query.get('sort', [{}])[0].values()))
        if sort == 'asc':
            api_params['order'] = 'PUBLISHDATE'

        try:
            api_params['searchtext'] = query['query']['filtered']['query']['query_string']['query']
        except KeyError:
            pass

        data = self.api_get(self.search_endpoint, api_params)
        docs = [self.format_list_item(item) for item in data[self.items_field]]
        return BelgaListCursor(docs, data.get('_meta', {}).get('total', len(docs)))

    def api_get(self, endpoint: str, params: Dict) -> Dict:
        resp = session.get(f'{self.base_url}/{endpoint}', headers={
            'Authorization': f'Bearer {self._access_token}',
            'X-Belga-Context': 'API'
        }, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def fetch(self, guid: str):
        _id = guid.replace(self.GUID_PREFIX, '')
        data = self.api_get(f'newsobject/{_id}', {})
        return self.format_list_item(data)

    def _get_period(self, period: str) -> Dict[str, str]:
        today = arrow.now(BELGA_TZ)
        shift = self.PERIODS.get(period, {})
        if period == 'this-week' and today.weekday() == 0:
            # Don't shift backward 7 days if today is monday, because weekday shift will return today
            # instead of monday of next week
            shift.pop('days')
        return {
            'start': today.shift(**shift).format('YYYY-MM-DD'),
            'end': today.format('YYYY-MM-DD'),
        }

    def format_list_item(self, data: Dict[str, Any]) -> Dict:
        guid = f"{self.GUID_PREFIX}{data['uuid']}"
        return {
            'type': 'text',
            'mimetype': 'application/superdesk.item.text',
            'pubstatus': 'usable',
            '_id': guid,
            'state': 'published',
            'guid': guid,
            'headline': get_text(data['title']),
            'abstract': get_text(data['lead']),
            'body_html': get_text(data['body']),
            'versioncreated': data.get('publishDate'),
            'firstcreated': data.get('publishDate'),  # createDate always is null
            'source': get_text(data['source']),
            'language': get_text(data['language']),
            'word_count': data['wordCount'],
            'extra': {
                'bpress': data['uuid'],
            },
            '_fetchable': False,
        }


def init_app(app):
    superdesk.register_search_provider('belga_image', provider_class=BelgaImageSearchProvider)
    superdesk.register_search_provider('belga_coverage', provider_class=BelgaCoverageSearchProvider)
    superdesk.register_search_provider('belga_360archive', provider_class=Belga360ArchiveSearchProvider)
    superdesk.register_search_provider('belga_press', provider_class=BelgaPressSearchProvider)
