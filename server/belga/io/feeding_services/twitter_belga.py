# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
import re
from datetime import datetime

import requests

import superdesk
from superdesk.errors import IngestTwitterError, SuperdeskIngestError
from superdesk.io.feeding_services import TwitterFeedingService
from superdesk.io.registry import register_feeding_service
from superdesk.metadata.item import GUID_FIELD


class IngestTwitterBelgaError(SuperdeskIngestError):
    _codes = {
        6300: "Invalid iframely api key"
    }

    @classmethod
    def TwitterInvalidIframelyKey(cls, exception=None, provider=None):
        return IngestTwitterBelgaError(6300, exception, provider)


class TwitterBelgaFeedingService(TwitterFeedingService):
    NAME = 'twitter_belga'

    label = 'Twitter Belga'

    ERRORS = [
        IngestTwitterError.TwitterLoginError().get_error_description(),
        IngestTwitterError.TwitterNoScreenNamesError().get_error_description(),
        IngestTwitterBelgaError.TwitterInvalidIframelyKey().get_error_description(),
    ]

    fields = [
        {
            'id': 'consumer_key', 'type': 'text', 'label': 'Twitter Consumer Key',
            'placeholder': 'Twitter consumer_key', 'required': True,
            'errors': {6100: 'Twitter authentication failure'}
        },
        {
            'id': 'consumer_secret', 'type': 'password', 'label': 'Twitter Consumer Secret',
            'placeholder': 'Twitter consumer_secret', 'required': True
        },
        {
            'id': 'access_token_key', 'type': 'text', 'label': 'Twitter Access Token Key',
            'placeholder': 'Twitter access_token_key', 'required': True
        },
        {
            'id': 'access_token_secret', 'type': 'password', 'label': 'Twitter Access Token Secret',
            'placeholder': 'Twitter access_token_secret', 'required': True
        },
        {
            'id': 'screen_names', 'type': 'text', 'label': 'Twitter Screen Names',
            'placeholder': 'Twitter screen_names', 'required': True,
            'errors': {6200: 'No Screen names specified'}
        },
        {
            'id': 'embed_tweet', 'type': 'boolean', 'default': False, 'label': 'Embed the tweet in the body'
        },
        {
            'id': 'iframely_key', 'type': 'password', 'label': 'iframely API Key',
            'placeholder': 'iframely api key', 'required': True,
            'errors': {6300: 'Invalid iframely api key'}
        },
    ]

    def _test(self, provider):
        super()._update(provider, None, test=True)
        config = provider.get('config', {})
        key = config.get('iframely_key')
        self._create_embed('https://iframely.com', key)

    def _update(self, provider, update, test=False):
        items = super()._update(provider, update, test)[0]
        config = provider.get('config', {})
        key = config.get('iframely_key')
        embed = config.get('embed_tweet')
        ingest_service = superdesk.get_resource_service('ingest')
        for item in items:
            # avoid update_ingest mark item as expired
            item['versioncreated'] = datetime.now()
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-;]|[\[\]?@_~]|'
                              r'(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                              item.get('body_html', ''))
            if embed:
                for url in set(urls):
                    item['body_html'] += '<!-- EMBED START Twitter -->'
                    item['body_html'] += self._create_embed(url, key)
                    item['body_html'] += '<!-- EMBED END Twitter -->'
            else:
                old_item = ingest_service.find_one(guid=item[GUID_FIELD], req=None)
                comment = '<!-- EMBED START Twitter -->'
                # only replace body_html of the tweet when embed is turn off
                # skip embed content as it is
                if old_item and comment in old_item.get('body_html', ''):
                    embed_content = comment.join(old_item['body_html'].split(comment)[1:])
                    item['body_html'] += comment + embed_content
        return [items]

    def _create_embed(self, url, key):
        """
        Get embed html from iframely service for provided url
        """
        response = requests.get('https://iframe.ly/api/oembed?url={}&api_key={}'.format(url, key))
        content = response.json()
        if response.status_code == 200:
            return content.get('html', '')
        elif response.status_code == 403:
            raise IngestTwitterBelgaError.TwitterInvalidIframelyKey()
        # when turn off setting: On URL errors, don't repeat it as HTTP status (use code 200 instead)
        # iframely will return 417 response on URL error
        return ''


register_feeding_service(TwitterBelgaFeedingService)
