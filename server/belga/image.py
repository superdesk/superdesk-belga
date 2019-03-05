import arrow
import requests
import superdesk

from urllib.parse import urljoin
from superdesk.utc import local_to_utc
from superdesk.utils import ListCursor

BELGA_TZ = 'Europe/Brussels'
GUID_PREFIX = 'urn:belga.be:image:'


def get_text(value):
    try:
        return value.strip()
    except AttributeError:
        return ''


def get_datetime(value):
    dt = arrow.get(value).datetime
    return local_to_utc(BELGA_TZ, dt)


def format_list_item(data):
    guid = '%s%d' % (GUID_PREFIX, data['imageId'])
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


class BelgaListCursor(ListCursor):

    def __init__(self, docs, count):
        super().__init__(docs)
        self._count = count

    def count(self, **kwargs):
        return self._count


class BelgaImageSearchProvider(superdesk.SearchProvider):

    label = 'Belga Image'
    base_url = 'https://api.ssl.belga.be/belgaimage-api/'

    def __init__(self, provider, **kwargs):
        super().__init__(provider, **kwargs)
        self.session = requests.Session()

    def url(self, resource):
        return urljoin(self.base_url, resource)

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

        resp = self.session.get(self.url('searchImages'), params=api_params)
        if resp.status_code != 200:
            resp.raise_for_status()

        data = resp.json()
        docs = [format_list_item(item) for item in data['images']]
        return BelgaListCursor(docs, data['nrImages'])

    def fetch(self, guid):
        _id = guid.replace(GUID_PREFIX, '')
        params = {'i': _id}
        resp = self.session.get(self.url('getImageById'), params=params)
        if resp.status_code != 200:
            resp.raise_for_status()

        data = resp.json()
        return format_list_item(data)


def init_app(app):
    superdesk.register_search_provider('belga_image', provider_class=BelgaImageSearchProvider)
