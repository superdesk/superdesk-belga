import hmac
import hashlib

from aioresponses import aioresponses

import superdesk

from belga.search_providers import BelgaImageSearchProvider

from .. import TestCase, mock


class BelgaImageTestCase(TestCase):
    def test_instance(self):
        provider = BelgaImageSearchProvider(dict())
        self.assertEqual("Belga Image", provider.label)
        self.assertIsInstance(provider, superdesk.SearchProvider)

    @aioresponses()
    async def test_find_items(self, http_mock):
        query = {}
        provider = BelgaImageSearchProvider(dict())

        mock.http(
            http_mock, payload=mock.fixture("belga-image-search.json", as_json=True)
        )

        cursor = await provider.find_async(query)
        self.assertEqual(83681621, await cursor.count(with_limit_and_skip=False))

        item = await cursor.next()
        self.assertEqual("picture", item["type"])
        self.assertEqual("usable", item["pubstatus"])
        self.assertEqual("urn:belga.be:image:143831778", item["_id"])
        self.assertEqual("urn:belga.be:image:143831778", item["guid"])
        self.assertEqual(
            "signature d'une convention entre l'agglo Val de sambre et la SA",
            item["headline"],
        )
        self.assertIn("©PHOTOPQR/VOIX", item["description_text"])
        self.assertEqual(
            "2019-01-08T12:32:06+00:00", item["versioncreated"].isoformat()
        )
        self.assertEqual("2019-01-08T12:32:06+00:00", item["firstcreated"].isoformat())
        self.assertEqual("MAXPPP", item["creditline"])
        self.assertEqual("MAXPPP", item["source"])
        self.assertEqual("MEFYJJ", item["byline"])
        self.assertFalse(item["_fetchable"])

        renditions = item["renditions"]
        self.assertIn("original", renditions)
        self.assertIn("thumbnail", renditions)
        self.assertIn("viewImage", renditions)
        self.assertIn("baseImage", renditions)

        self.assertIn("600x140", renditions["thumbnail"]["href"])
        self.assertIn("800x800", renditions["viewImage"]["href"])
        self.assertIn("1800x650", renditions["baseImage"]["href"])
        self.assertIn("1800x650", renditions["original"]["href"])

        # orig
        self.assertEqual(4300, renditions["original"]["width"])
        self.assertEqual(2868, renditions["original"]["height"])

    @aioresponses()
    async def test_find_params(self, http_mock):
        query = {
            "size": 20,
            "from": 10,
            "query": {
                "filtered": {
                    "query": {
                        "query_string": {"query": "test query"},
                    },
                },
            },
        }

        params = {
            "source": {
                "belga": True,
                "ansa": True,
                "afp": False,
            },
            "subject": {
                "news": True,
                "sports": True,
                "finance": False,
            },
            "period": "today",
            "dates": {"start": "01/09/2020", "end": "10/09/2020"},
        }

        provider = BelgaImageSearchProvider(dict())
        mock.http(http_mock, payload={"images": [], "nrImages": 0})
        await provider.find_async(query, params)

        http_mock.assert_called_with(
            provider.base_url
            + provider.construct_url(
                "searchImages",
                {
                    "s": 10,
                    "l": 20,
                    "o": "0",
                    "c": "ansa,belga",
                    "h": "news,sports",
                    "f": 1598918400000,
                    "e": 1599696000000,
                    "p": "TODAY",
                    "t": "test AND query",
                },
            ).lstrip("/"),
            headers={},
        )

    @aioresponses()
    async def test_fetch(self, http_mock):
        mock.http(
            http_mock, payload=mock.fixture("belga-image-by-id.json", as_json=True)
        )
        provider = BelgaImageSearchProvider(dict())
        item = await provider.fetch_async("urn:belga.be:image:143831778")
        http_mock.assert_called_with(
            provider.base_url
            + provider.construct_url("getImageById", {"i": "143831778"}).lstrip("/"),
            headers={},
        )

        self.assertEqual("urn:belga.be:image:143831778", item["guid"])
        self.assertEqual("Belloumi", item["byline"])

    def test_auth_headers(self):
        provider = BelgaImageSearchProvider(dict())
        provider.provider["config"] = {"username": "john", "password": "pwd"}
        headers = provider.auth_headers("/test", "pwd")
        self.assertIn("X-Date", headers)
        self.assertEqual(
            headers["X-Authorization"],
            "john:{}".format(
                hmac.new(
                    "pwd".encode(),
                    "/test+{}".format(headers["X-Date"]).encode(),
                    hashlib.sha256,
                ).hexdigest(),
            ),
        )

    def test_auth_search_criteria(self):
        provider = BelgaImageSearchProvider({})
        provider.provider["config"] = {"username": "test"}
        provider._id_token = "25222473406"
        provider._auth_token = "339824739329"
        nonce = "Thu, 13 Feb 2020 13:19:05 GMT"
        url = (
            "/searchImages?s=0&l=200&t="
            "(test) AND (BELGAPORTRAIT OR HEADSHOT)&r=2&c=AFP,BELGA&h=news&l=BELGAPORTRAIT,HEADSHOT"
        )
        headers = provider.auth_headers(url, nonce=nonce)
        self.assertEqual(
            "test:30f35157e8da2015c069af6a814ab30ee0121b2ce22d4f060140e32cce013af6",
            headers["X-Identification"],
        )
        self.assertEqual(
            "test:da70d29ee4703023f27b6af5cbad9fb267de50e02332ec4359d860c5d5b98253",
            headers["X-Authorization"],
        )
