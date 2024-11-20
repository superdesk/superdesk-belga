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
from superdesk.io.registry import (
    register_feeding_service,
    register_feeding_service_parser,
)
from superdesk.metadata.item import GUID_FIELD


class IngestTwitterBelgaError(SuperdeskIngestError):
    _codes = {6300: "Invalid iframely api key"}

    @classmethod
    def TwitterInvalidIframelyKey(cls, exception=None, provider=None):
        return IngestTwitterBelgaError(6300, exception, provider)


class TwitterBelgaFeedingService(TwitterFeedingService):
    NAME = "twitter_belga"

    label = "Twitter Belga"

    ERRORS = [
        IngestTwitterError.TwitterLoginError().get_error_description(),
        IngestTwitterError.TwitterNoScreenNamesError().get_error_description(),
        IngestTwitterBelgaError.TwitterInvalidIframelyKey().get_error_description(),
    ]

    fields = [
        {
            "id": "consumer_key",
            "type": "text",
            "label": "Twitter Consumer Key",
            "placeholder": "Twitter consumer key",
            "required": True,
            "errors": {6100: "Twitter authentication failure"},
        },
        {
            "id": "consumer_secret",
            "type": "password",
            "label": "Twitter Consumer Secret",
            "placeholder": "Twitter consumer secret",
            "required": True,
        },
        {
            "id": "access_token_key",
            "type": "text",
            "label": "Twitter Access Token Key",
            "placeholder": "Twitter access token key",
            "required": True,
        },
        {
            "id": "access_token_secret",
            "type": "password",
            "label": "Twitter Access Token Secret",
            "placeholder": "Twitter access token secret",
            "required": True,
        },
        {
            "id": "screen_names",
            "type": "text",
            "label": "Twitter Screen Names",
            "placeholder": "Twitter screen names",
            "required": True,
            "errors": {6200: "No Screen names specified"},
        },
        {
            "id": "embed_tweet",
            "type": "boolean",
            "default": False,
            "label": "Embed the tweet in the body",
        },
        {
            "id": "iframely_key",
            "type": "password",
            "label": "iframely API Key",
            "placeholder": "iframely api key",
            "required": True,
            "errors": {6300: "Invalid iframely api key"},
        },
    ]

    def _test(self, provider):
        super()._update(provider, None, test=True)
        config = provider.get("config", {})
        key = config.get("iframely_key")
        self._create_embed("https://iframely.com", key)

    def _update(self, provider, update, test=False):
        items = super()._update(provider, update, test)[0]
        return self.parse_twitter_belga(items, provider)

    def parse_twitter_belga(self, items, provider):
        config = provider.get("config", {})
        key = config.get("iframely_key")
        embed = config.get("embed_tweet")
        ingest_service = superdesk.get_resource_service("ingest")
        # get all guid of old items
        old_guid = [
            item[GUID_FIELD]
            for item in ingest_service.find(
                {GUID_FIELD: {"$in": [item[GUID_FIELD] for item in items]}}
            )
        ]
        # remove all old item
        [items.remove(item) for item in items.copy() if item[GUID_FIELD] in old_guid]
        for item in items:
            if embed:
                urls = re.findall(
                    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-;]|[\[\]?@_~]|"
                    r"(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                    item.get("body_html", ""),
                )
                for url in set(urls):
                    embed_content = self._create_embed(url, key)
                    if embed_content:
                        item["body_html"] += "<!-- EMBED START Twitter -->"
                        item["body_html"] += embed_content
                        item["body_html"] += "<!-- EMBED END Twitter -->"
        return [items]

    def _create_embed(self, url, key):
        """
        Get embed html from iframely service for provided url
        """
        response = requests.get(
            "https://iframe.ly/api/oembed?url={}&api_key={}".format(url, key)
        )
        content = response.json()
        if response.status_code == 200:
            return content.get("html", "")
        elif response.status_code == 403:
            raise IngestTwitterBelgaError.TwitterInvalidIframelyKey()
        # when turn off setting: On URL errors, don't repeat it as HTTP status (use code 200 instead)
        # iframely will return 417 response on URL error
        return ""


register_feeding_service(TwitterBelgaFeedingService)
register_feeding_service_parser(TwitterBelgaFeedingService.NAME, None)
