import arrow
import superdesk

from aioresponses import aioresponses

from pytz import utc
from datetime import datetime
from unittest.mock import MagicMock
from belga.search_providers import Belga360ArchiveSearchProvider
from superdesk.core import json

from .. import TestCase, mock


def get_belga360_search() -> str:
    return mock.fixture("belga-360archive-search.json")


def get_belga360_item():
    items = mock.fixture("belga-360archive-search.json", as_json=True)
    return items["newsObjects"]


class Belga360ArchiveTestCase(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.provider = Belga360ArchiveSearchProvider(dict())
        self.app.data.insert("content_types", [{"_id": "text", "label": "text"}])
        await self.provider._load_content_types()
        self.query = {
            "size": 50,
            "from": 50,
            "query": {
                "filtered": {
                    "query": {
                        "query_string": {"query": "test query"},
                    },
                },
            },
        }

    def test_instance(self):
        self.assertEqual("Belga 360 Archive", self.provider.label)
        self.assertIsInstance(self.provider, superdesk.SearchProvider)

    @aioresponses()
    async def test_find_params(self, http_mock):
        params = {
            "credits": "afp",
            "dates": {"start": "02/02/2020", "end": "14/02/2020"},
            "languages": "en",
            "types": {"Short": True},
        }
        mock.http(http_mock)
        await self.provider.find_async(self.query, params)
        http_mock.assert_called_once_with(
            self.provider.base_url + "archivenewsobjects",
            params={
                "start": 50,
                "pageSize": 50,
                "language": "en",
                "assetType": "Short",
                "credits": "AFP",
                "fromDate": "20200202",
                "toDate": "20200214",
                "searchText": "test query",
            },
        )

    async def test_format_list_item(self):
        item = await self.provider.format_list_item(get_belga360_item()[0])
        guid = "urn:belga.be:360archive:39670442"
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["mimetype"], "application/superdesk.item.text")
        self.assertEqual(item["_id"], guid)
        self.assertEqual(item["state"], "published")
        self.assertEqual(item["profile"], "text")
        self.assertEqual(item["guid"], guid)
        self.assertEqual(item["extra"]["city"], "Bruxelles")
        self.assertEqual(
            item["headline"],
            "(Lorem ipsum) dolor sit amet, consectetur adipiscing elit.",
        )
        self.assertEqual(item["name"], "")
        self.assertEqual(item["slugline"], "Belga 360 slugline")
        self.assertEqual(item["description_text"], "")
        self.assertEqual(item["creditline"], "BELGA")
        self.assertEqual(item["source"], "BELGA")
        self.assertEqual(item["language"], "fr")
        self.assertEqual(item["firstcreated"], datetime.fromtimestamp(1581646440, utc))
        self.assertEqual(
            item["versioncreated"], datetime.fromtimestamp(1581654480, utc)
        )
        self.assertEqual(
            item["keywords"], ["BRIEF", "#CORONAVIRUS", "SPORTS", "INTERNET"]
        )
        self.assertEqual(item["sign_off"], "BRV/Author")
        self.assertEqual(
            item["authors"], [{"name": "BRV", "sub_label": "BRV", "role": "AUTHOR"}]
        )
        self.assertEqual(
            item["body_html"],
            (
                "Vivamus rutrum sapien a purus posuere eleifend. Integer non feugiat sapien. Proin"
                " finibus diam in urna vehicula accumsan<br/><br/>"
                "&nbsp;&nbsp;&nbsp;&nbsp;"
                "Morbi lacus ex, molestie id ullamcorper quis"
                " co&v scelerisque quis lectus."
                "<br/>&nbsp;&nbsp;&nbsp;&nbsp;"
                " Phasellus laoreet turpis nunc,"
                " vitae porttitor sapien ultricies non."
                "<br/>&nbsp;&nbsp;&nbsp;&nbsp;"
                " Nullam fringilla justo vitae ex commodo vulputate."
                "<br/>&nbsp;&nbsp;&nbsp;&nbsp;"
                " In bibendum diam vitae condimentum scelerisque."
                "<br/>&nbsp;&nbsp;&nbsp;&nbsp;"
                " Integer dapibus turpis augue, a varius diam ornare in."
                "<br/>&nbsp;&nbsp;&nbsp;&nbsp;"
                " Donec aliquam cursus posuere."
            ),
        )
        self.assertEqual(
            item["subject"],
            [
                {
                    "name": "#CORONAVIRUS",
                    "qcode": "#CORONAVIRUS",
                    "scheme": "original-metadata",
                },
                {
                    "name": "BRIEF",
                    "qcode": "BRIEF",
                    "translations": {"name": {"nl": "BRIEF", "fr": "BRIEF"}},
                    "scheme": "belga-keywords",
                },
                {
                    "name": "INT/POL",
                    "qcode": "INT/POL",
                    "parent": "INT",
                    "scheme": "services-products",
                },
                {
                    "name": "INTERNET",
                    "qcode": "INTERNET",
                    "scheme": "belga-keywords",
                    "translations": {"name": {"fr": "INTERNET", "nl": "INTERNET"}},
                },
                {
                    "name": "SPORTS",
                    "qcode": "SPORTS",
                    "translations": {"name": {"nl": "SPORTS", "fr": "SPORTS"}},
                    "scheme": "belga-keywords",
                },
                {
                    "name": "Belgium",
                    "qcode": "bel",
                    "translations": {"name": {"nl": "België", "fr": "Belgique"}},
                    "scheme": "countries",
                },
                {
                    "name": "Belgium",
                    "qcode": "country_bel",
                    "translations": {"name": {"nl": "BELGIE", "fr": "BELGIQUE"}},
                    "scheme": "country",
                },
            ],
        )
        self.assertFalse(item["_fetchable"]),
        self.assertEqual(item["ednote"], "Test Ednote of Belga archive api")

    async def test_get_related_article(self):
        items = await self.provider.get_related_article(get_belga360_item())
        self.assertIn("belga_related_articles--0", items)
        self.assertEqual(len(items), 2)

        item = items["belga_related_articles--0"]
        guid = "urn:belga.be:360archive:44690231"
        self.assertEqual(item["_id"], guid)
        self.assertEqual(item["state"], "published")
        self.assertEqual(item["guid"], guid)
        self.assertEqual(item["headline"], "Related item headline")
        self.assertEqual(item["slugline"], "Related item slugline")
        self.assertEqual(item["description_text"], "")
        self.assertEqual(item["creditline"], "BELGA")
        self.assertEqual(item["source"], "BELGA")
        self.assertEqual(item["language"], "fr")
        self.assertEqual(
            item["firstcreated"], datetime(2022, 10, 5, 13, 41, 50, tzinfo=utc)
        )
        self.assertEqual(
            item["versioncreated"], datetime(2022, 10, 5, 13, 41, 50, tzinfo=utc)
        )
        self.assertEqual(
            item["firstpublished"], datetime(2022, 10, 5, 13, 41, 50, tzinfo=utc)
        )
        self.assertEqual(item["sign_off"], "TOB/Author, EDS/Editor")
        self.assertEqual(
            item["authors"],
            [
                {"name": "TOB", "sub_label": "TOB", "role": "AUTHOR"},
                {"name": "EDS", "sub_label": "EDS", "role": "EDITOR"},
            ],
        )

        related_picture_item = items["belga_related_images--1"]
        guid = "urn:belga.be:360archive:46768825"
        self.assertEqual(related_picture_item["_id"], guid)
        self.assertEqual(related_picture_item["state"], "published")
        self.assertEqual(
            related_picture_item["mimetype"], "application/superdesk.item.picture"
        )
        self.assertEqual(related_picture_item["type"], "picture")
        self.assertEqual(related_picture_item["headline"], "FILES - FBL - WC - 2022")

    @aioresponses()
    async def test_find_item(self, http_mock):
        mocked_response = mock.fixture("belga-360archive-search.json", as_json=True)
        mock.http(http_mock, payload=mocked_response)
        items = await self.provider.find_async(self.query)
        self.assertEqual(len(items.docs), 4)
        self.assertEqual(items._count, 25000)

    @aioresponses()
    async def test_fetch(self, http_mock):
        mock.http(http_mock, payload=get_belga360_item()[0])
        item = await self.provider.fetch_async("urn:belga.be:360archive:39670442")
        url = self.provider.base_url + "archivenewsobjects/39670442"
        http_mock.assert_called_with(url, params={})

        self.assertEqual("urn:belga.be:360archive:39670442", item["guid"])

    async def test_get_periods(self):
        arrow.now = MagicMock(return_value=arrow.get("2020-02-14"))
        day_period = self.provider._get_period("day")
        self.assertEqual(day_period["fromDate"], "20200213")
        self.assertEqual(day_period["toDate"], "20200214")

        def get_period(period):
            return self.provider._get_period(period)["fromDate"]

        self.assertEqual(get_period("week"), "20200207")
        self.assertEqual(get_period("month"), "20200114")
        self.assertEqual(get_period("year"), "20190214")

    async def test_get_image_renditions(self):
        item = await self.provider.format_list_item(get_belga360_item()[3])
        guid = "urn:belga.be:360archive:46768825"
        self.assertEqual(item["_id"], guid)
        self.assertEqual(item["mimetype"], "application/superdesk.item.picture")
        self.assertEqual(item["state"], "published")
        self.assertEqual(item["guid"], guid)
        self.assertEqual(item["headline"], "FILES - FBL - WC - 2022")
        self.assertEqual(
            item["description_text"],
            (
                "(FILES) In this file photo taken on September 25, 2022 Croatia's coach"
                " Zlatko Dalic poses prior the UEFA Nations League, league A, Group 1"
                " football match betwen Austria and Croatia in Vienna.  JOE KLAMAR / AFP"
            ),
        )
        self.assertEqual(
            item["authors"], [{"name": "MAK", "sub_label": "MAK", "role": "AUTHOR"}]
        )
        self.assertEqual(
            item["renditions"],
            {
                "original": {
                    "href": "https://3.ssl.belga.be/360-archief:picture:46768825:full?v=636939e3&m=pdnmpbgp"
                },
                "thumbnail": {
                    "href": "https://0.ssl.belga.be/360-archief:picture:46768825:thumbnail?v=636939e3&m=gpdoidca"
                },
                "viewImage": {
                    "href": "https://0.ssl.belga.be/360-archief:picture:46768825:preview?v=636939e3&m=njfkedgg"
                },
                "baseImage": {
                    "href": "https://3.ssl.belga.be/360-archief:picture:46768825:full?v=636939e3&m=pdnmpbgp"
                },
            },
        )

    @aioresponses()
    async def test_get_highlighted_text(self, http_mock):
        mock.http(http_mock, payload=json.loads(get_belga360_search()))
        query = {
            "size": 50,
            "from": 50,
            "query": {
                "filtered": {
                    "query": {
                        "query_string": {"query": "Lorem ipsum"},
                    },
                },
            },
        }
        items = await self.provider.find_async(query)
        self.assertEqual(len(items.docs), 4)
        highlighted_item = await items.next()
        self.assertEqual(
            highlighted_item["es_highlight"],
            {
                "headline": [
                    (
                        '(<span class="es-highlight">Lorem</span> <span class="es-highlight">ipsum</span>) dolor '
                        "sit amet, consectetur adipiscing elit."
                    )
                ]
            },
        )

        query["query"]["filtered"]["query"]["query_string"]["query"] = "ipsum Lorem"
        items = await self.provider.find_async(query)
        highlighted_item = await items.next()
        self.assertEqual(
            highlighted_item["es_highlight"],
            {
                "headline": [
                    (
                        '(<span class="es-highlight">Lorem</span> <span class="es-highlight">ipsum</span>) dolor '
                        "sit amet, consectetur adipiscing elit."
                    )
                ]
            },
        )

        query["query"]["filtered"]["query"]["query_string"]["query"] = "(Lorem ipsum)"
        items = await self.provider.find_async(query)
        highlighted_item = await items.next()

        self.assertEqual(
            highlighted_item["es_highlight"],
            {
                "headline": [
                    (
                        '<span class="es-highlight">(Lorem</span> <span class="es-highlight">ipsum)</span> dolor '
                        "sit amet, consectetur adipiscing elit."
                    )
                ]
            },
        )
