import os
import superdesk

import arrow
from flask import json
from httmock import all_requests, HTTMock
from unittest.mock import MagicMock, patch
from belga.search_providers import BelgaPressSearchProvider, TIMEOUT, get_datetime
from superdesk.tests import TestCase


def fixture(filename):
    return os.path.join(os.path.dirname(__file__), "..", "fixtures", filename)


class DetailResponse:
    status_code = 200

    def raise_for_status(self):
        pass


@all_requests
def archive_mock(url, request):
    with open(fixture("belga-press-search.json")) as _file:
        return _file.read()


def get_item():
    with open(fixture("belga-press-search.json")) as _file:
        items = json.load(_file)
        return items["data"][0]


class BelgaPressTestCase(TestCase):
    def setUp(self):
        self.provider = BelgaPressSearchProvider(dict())
        self.provider._access_token = "abc"
        self.query = {
            "size": 25,
            "from": 50,
            "query": {
                "filtered": {
                    "query": {
                        "query_string": {"query": "test query"},
                    },
                },
            },
            "sort": [{"versioncreated": "asc"}],
        }

    def test_instance(self):
        self.assertEqual("Belga Press", self.provider.label)
        self.assertIsInstance(self.provider, superdesk.SearchProvider)

    @patch("belga.search_providers.session.get")
    @patch("belga.search_providers.session.post")
    def test_find_params(self, session_post, session_get):
        params = {
            "types": "ONLINE",
            "dates": {"start": "25/11/2020", "end": "26/11/2020"},
            "languages": "EN",
        }
        session_post.return_value = {"access_token": "abc"}
        self.provider.find(self.query, params)
        url = self.provider.base_url + "/" + self.provider.search_endpoint
        api_params = {
            "offset": 50,
            "count": 25,
            "mediumtypegroup": "ONLINE",
            "language": "EN",
            "start": "2020-11-25",
            "end": "2020-11-26",
            "order": "PUBLISHDATE",
            "searchtext": "test query",
        }
        headers = {"Authorization": "Bearer abc", "X-Belga-Context": "API"}
        session_get.assert_called_with(
            url, headers=headers, params=api_params, timeout=TIMEOUT
        )
        # Test combine period and date
        arrow.now = MagicMock(return_value=arrow.get("2020-11-26"))
        params = {
            "dates": {"start": "26/10/2020", "end": "25/11/2020"},
            "period": "year",
        }

        self.provider.find(self.query, params)
        session_get.assert_called_with(
            url,
            headers=headers,
            params={
                "offset": 50,
                "count": 25,
                "start": "2020-10-26",
                "end": "2020-11-25",
                "order": "PUBLISHDATE",
                "searchtext": "test query",
            },
            timeout=TIMEOUT,
        )

    def test_format_list_item(self):
        item = self.provider.format_list_item(get_item())
        guid = "urn:belga.be:belgapress:4fe4c785-b4d4-43f9-b6e1-c28bbc53363c"
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["mimetype"], "application/superdesk.item.text")
        self.assertEqual(item["state"], "published")
        self.assertEqual(item["_id"], guid)
        self.assertEqual(item["guid"], guid)
        self.assertEqual(item["headline"], "Lorem Ipsum")
        self.assertEqual(
            item["abstract"],
            (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi in semper ex, vel faucibus neque.\n"
            ),
        )
        self.assertEqual(item["body_html"], "")
        self.assertEqual(item["firstcreated"], "2020-11-27T00:00:00+01:00")
        self.assertEqual(item["versioncreated"], "2020-11-27T00:00:00+01:00")
        self.assertEqual(item["source"], "La Libre Belgique")
        self.assertEqual(item["language"], "fr")
        self.assertEqual(item["word_count"], 820)
        self.assertEqual(
            item["extra"]["bpress"], "4fe4c785-b4d4-43f9-b6e1-c28bbc53363c"
        )

        self.assertFalse(item["_fetchable"])

    def test_find_item(self):
        with HTTMock(archive_mock):
            items = self.provider.find(self.query)
        self.assertEqual(len(items.docs), 2)
        self.assertEqual(items._count, 3000)

    @patch("belga.search_providers.session.get")
    def test_fetch(self, session_get):
        response = DetailResponse()
        response.json = MagicMock(return_value=get_item())
        session_get.return_value = response

        item = self.provider.fetch(
            "urn:belga.be:belgapress:4fe4c785-b4d4-43f9-b6e1-c28bbc53363c"
        )
        url = (
            self.provider.base_url + "/newsobject/4fe4c785-b4d4-43f9-b6e1-c28bbc53363c"
        )

        session_get.assert_called_with(
            url,
            headers={"Authorization": "Bearer abc", "X-Belga-Context": "API"},
            params={},
            timeout=TIMEOUT,
        )
        self.assertEqual(
            "urn:belga.be:belgapress:4fe4c785-b4d4-43f9-b6e1-c28bbc53363c", item["guid"]
        )

    def test_get_periods(self):
        arrow.now = MagicMock(return_value=arrow.get("2020-11-25"))

        def get_period(period):
            return self.provider._get_period(period)["start"]

        self.assertEqual(self.provider._get_period("day")["end"], "2020-11-25")
        self.assertEqual(get_period("day"), "2020-11-25")
        self.assertEqual(get_period("yesterday"), "2020-11-24")
        self.assertEqual(get_period("this-week"), "2020-11-23")
        self.assertEqual(get_period("week"), "2020-11-18")
        self.assertEqual(get_period("month"), "2020-10-25")
        self.assertEqual(get_period("year"), "2019-11-25")

        # test this-week for Monday
        arrow.now = MagicMock(return_value=arrow.get("2020-11-23"))
        self.assertEqual(get_period("this-week"), "2020-11-23")
