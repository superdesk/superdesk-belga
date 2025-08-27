import os
import unittest
import requests
from flask import Flask, json
from httmock import all_requests
from unittest.mock import patch
from belga.search_providers import BelgaImageV2SearchProvider, TIMEOUT


def fixture(filename):
    return os.path.join(os.path.dirname(__file__), "..", "fixtures", filename)


@all_requests
def search_mock(url, request):
    if "o=1" in url.geturl():
        with open(fixture("belga-video-search.json")) as _file:
            return {"status_code": 200, "content": json.load(_file)}
    return {"status_code": 400, "content": "Invalid request"}


class VideoDetailResponse:
    status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        with open(fixture("belga-video-by-id.json")) as _file:
            return json.load(_file)


class BelgaVideoTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["BELGA_VIDEO_ENABLED"] = True
        self.app.config["BELGA_IMAGE_LIMIT"] = "TODAY"
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_instance_v2(self):
        provider = BelgaImageV2SearchProvider(dict(config={"username": "test_apikey"}))
        self.assertEqual("Belga Image v2", provider.label)
        self.assertIsInstance(provider, BelgaImageV2SearchProvider)

    @patch("belga.search_providers.session.get")
    def test_find_v2_videos(self, session_get):
        with open(fixture("belga-video-search.json")) as f:
            data = json.load(f)

        mock_response = unittest.mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = data
        session_get.return_value = mock_response

        query = {
            "size": 10,
            "from": 0,
            "query": {
                "filtered": {
                    "query": {
                        "query_string": {"query": "test video"},
                    },
                },
            },
        }
        params = {"objecttypes": "1"}  # Filter for videos
        provider = BelgaImageV2SearchProvider(dict(config={"username": "test_apikey"}))

        items = provider.find(query, params)

        url = (
            requests.Request(
                "GET",
                provider.base_url + "searchImages",
                params={
                    "s": 0,
                    "l": 10,
                    "o": "1",
                    "p": "TODAY",
                },
            )
            .prepare()
            .url
        )
        session_get.assert_called_with(
            url,
            headers={"X-Authorization": "test_apikey"},
            timeout=TIMEOUT,
        )

        self.assertEqual(100, items.count(with_limit_and_skip=False))
        item = items[0]
        self.assertEqual("video", item["type"])
        self.assertEqual("usable", item["pubstatus"])
        self.assertEqual("urn:belga.be:picturepackmedia:123456789", item["_id"])
        self.assertEqual("Video: Event Coverage", item["headline"])
        self.assertEqual("video/mp4", item["mimetype"])
        self.assertFalse(item["_fetchable"])

        renditions = item["renditions"]
        self.assertIn("original", renditions)
        self.assertEqual(
            "https://belga-websvc.picturepack.com/belgaimage-api/video/123456789.mp4",
            renditions["original"]["href"],
        )
        self.assertEqual("video/mp4", renditions["original"]["mimetype"])

    @patch("belga.search_providers.session.get")
    def test_fetch_v2_video(self, session_get):
        """Test fetching a single video by ID"""
        provider = BelgaImageV2SearchProvider(dict(config={"username": "test_apikey"}))
        session_get.return_value = VideoDetailResponse()

        item = provider.fetch("urn:belga.be:picturepackmedia:123456789")

        url = (
            requests.Request(
                "GET",
                provider.base_url + "getImageById",
                params={
                    "i": "urn:belga.be:picturepackmedia:123456789",
                    "p": "TODAY",
                },
            )
            .prepare()
            .url
        )
        session_get.assert_called_with(
            url,
            headers={"X-Authorization": "test_apikey"},
            timeout=TIMEOUT,
        )

        self.assertEqual("urn:belga.be:picturepackmedia:123456789", item["guid"])
        self.assertEqual("video", item["type"])
        self.assertEqual("John Doe", item["byline"])
        self.assertEqual("video/mp4", item["mimetype"])
        self.assertEqual(
            "https://belga-websvc.picturepack.com/belgaimage-api/video/123456789.mp4",
            item["renditions"]["original"]["href"],
        )
        self.assertEqual("video/mp4", item["renditions"]["original"]["mimetype"])
