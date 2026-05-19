import yarl
from aioresponses import aioresponses

from belga.search_providers import BelgaImageV2SearchProvider

from .. import TestCase, mock


class BelgaVideoTestCase(TestCase):
    app_config: dict = {
        **TestCase.app_config,
        "BELGA_VIDEO_ENABLED": True,
        "BELGA_IMAGE_LIMIT": "TODAY",
    }

    def test_instance_v2(self):
        provider = BelgaImageV2SearchProvider(dict(config={"username": "test_apikey"}))
        self.assertEqual("Belga Image v2", provider.label)
        self.assertIsInstance(provider, BelgaImageV2SearchProvider)

    @aioresponses()
    async def test_find_v2_videos(self, http_mock):
        mock.http(
            http_mock, payload=mock.fixture("belga-video-search.json", as_json=True)
        )

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

        items = await provider.find_async(query, params)

        url = str(
            yarl.URL(provider.base_url + "searchImages").with_query(
                {
                    "s": 0,
                    "l": 10,
                    "o": "1",
                    "t": "test AND video",
                    "p": "TODAY",
                }
            )
        )

        http_mock.assert_called_with(
            url,
            headers={"X-Authorization": "test_apikey"},
        )

        self.assertEqual(100, await items.count(with_limit_and_skip=False))
        item = await items.next()
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

    @aioresponses()
    async def test_fetch_v2_video(self, http_mock):
        """Test fetching a single video by ID"""
        provider = BelgaImageV2SearchProvider(dict(config={"username": "test_apikey"}))
        mock.http(
            http_mock, payload=mock.fixture("belga-video-by-id.json", as_json=True)
        )

        item = await provider.fetch_async("urn:belga.be:picturepackmedia:123456789")

        url = str(
            yarl.URL(provider.base_url + "getImageById").with_query(
                {"i": "urn:belga.be:picturepackmedia:123456789", "p": "TODAY"}
            )
        )
        http_mock.assert_called_with(
            url,
            headers={"X-Authorization": "test_apikey"},
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
