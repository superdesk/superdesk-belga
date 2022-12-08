import os
import arrow
import superdesk

from pytz import utc
from flask import json
from datetime import datetime
from httmock import all_requests, HTTMock
from unittest.mock import patch, MagicMock
from belga.search_providers import Belga360ArchiveSearchProvider, TIMEOUT
from superdesk.tests import TestCase


def fixture(filename):
    return os.path.join(os.path.dirname(__file__), "..", "fixtures", filename)


class DetailResponse:
    status_code = 200

    def raise_for_status(self):
        pass


@all_requests
def archive_mock(url, request):
    with open(fixture("belga-360archive-search.json")) as _file:
        return _file.read()


def get_belga360_item():
    with open(fixture("belga-360archive-search.json")) as _file:
        items = json.load(_file)
        return items["newsObjects"]


class Belga360ArchiveTestCase(TestCase):
    def setUp(self):
        self.provider = Belga360ArchiveSearchProvider(dict())
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

    @patch("belga.search_providers.session.get")
    def test_find_params(self, session_get):
        params = {
            "credits": "afp",
            "dates": {"start": "02/02/2020", "end": "14/02/2020"},
            "languages": "en",
            "types": {"Short": True},
        }
        self.provider.find(self.query, params)
        url = self.provider.base_url + "archivenewsobjects"
        params = {
            "start": 50,
            "pageSize": 50,
            "language": "en",
            "assetType": "Short",
            "credits": "AFP",
            "fromDate": "20200202",
            "toDate": "20200214",
            "searchText": "test query",
        }
        session_get.assert_called_with(url, params=params, timeout=TIMEOUT)

    def test_format_list_item(self):
        self.app.data.insert("content_types", [{"_id": "text", "label": "text"}])

        self.app.data.insert(
            "vocabularies",
            [
                {
                    "_id": "belga-keywords",
                    "display_name": "Belga Keywords",
                    "type": "manageable",
                    "selection_type": "multi selection",
                    "unique_field": "qcode",
                    "schema": {"name": {}, "qcode": {}, "translations": {}},
                    "service": {"all": 1},
                    "items": [
                        {
                            "name": "BRIEF",
                            "qcode": "BRIEF",
                            "is_active": True,
                            "translations": {"name": {"nl": "BRIEF", "fr": "BRIEF"}},
                        },
                        {
                            "name": "SPORTS",
                            "qcode": "SPORTS",
                            "is_active": True,
                            "translations": {"name": {"nl": "SPORTS", "fr": "SPORTS"}},
                        },
                    ],
                },
                {
                    "_id": "countries",
                    "display_name": "Country",
                    "type": "manageable",
                    "selection_type": "single selection",
                    "unique_field": "qcode",
                    "schema": {"name": {}, "qcode": {}, "translations": {}},
                    "service": {"all": 1},
                    "items": [
                        {
                            "name": "Belgium",
                            "qcode": "bel",
                            "is_active": True,
                            "translations": {
                                "name": {"nl": "België", "fr": "Belgique"}
                            },
                        }
                    ],
                },
                {
                    "_id": "country",
                    "display_name": "Countries keywords",
                    "type": "manageable",
                    "selection_type": "multi selection",
                    "unique_field": "qcode",
                    "schema": {"name": {}, "qcode": {}, "translations": {}},
                    "service": {"all": 1},
                    "items": [
                        {
                            "name": "Belgium",
                            "qcode": "country_bel",
                            "is_active": True,
                            "translations": {
                                "name": {"nl": "België", "fr": "Belgique"}
                            },
                        }
                    ],
                },
                {
                    "_id": "services-products",
                    "display_name": "Packages",
                    "type": "manageable",
                    "selection_type": "multi selection",
                    "unique_field": "qcode",
                    "service": {"all": 1},
                    "items": [
                        {
                            "name": "INT/POL",
                            "qcode": "INT/POL",
                            "is_active": True,
                            "parent": "INT",
                        }
                    ],
                },
            ],
        )

        # reload content profiles
        self.provider = Belga360ArchiveSearchProvider(dict())
        item = self.provider.format_list_item(get_belga360_item()[0])
        guid = "urn:belga.be:360archive:39670442"
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["mimetype"], "application/superdesk.item.text")
        self.assertEqual(item["_id"], guid)
        self.assertEqual(item["state"], "published")
        self.assertEqual(item["profile"], "text")
        self.assertEqual(item["guid"], guid)
        self.assertEqual(item["extra"]["city"], "Bruxelles")
        self.assertEqual(
            item["headline"], "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
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
                    "scheme": "original-metadata",
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
                    "translations": {"name": {"nl": "België", "fr": "Belgique"}},
                    "scheme": "country",
                },
            ],
        )
        self.assertFalse(item["_fetchable"]),
        self.assertEqual(item["ednote"], "Test Ednote of Belga archive api")

    def test_get_related_article(self):
        self.provider = Belga360ArchiveSearchProvider(dict())

        with open(fixture("belga-360archive-search.json")) as _file:
            items = self.provider.get_related_article(json.load(_file)["newsObjects"])
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
                item["firstcreated"], datetime.fromtimestamp(1638953020, utc)
            )
            self.assertEqual(
                item["versioncreated"], datetime(2022, 10, 5, 10, 11, 50, tzinfo=utc)
            )
            self.assertEqual(
                item["firstpublished"], datetime(2022, 10, 5, 10, 11, 50, tzinfo=utc)
            )
            self.assertEqual(item["sign_off"], "TOB/Author, EDS/Editor")
            self.assertEqual(
                item["authors"],
                [
                    {"name": "TOB", "sub_label": "TOB", "role": "AUTHOR"},
                    {"name": "EDS", "sub_label": "EDS", "role": "EDITOR"},
                ],
            )

            related_picture_item = items["belga_related_articles--1"]
            guid = "urn:belga.be:360archive:46768825"
            self.assertEqual(related_picture_item["_id"], guid)
            self.assertEqual(related_picture_item["state"], "published")
            self.assertEqual(
                related_picture_item["mimetype"], "application/superdesk.item.picture"
            )
            self.assertEqual(related_picture_item["type"], "picture")
            self.assertEqual(
                related_picture_item["headline"], "FILES - FBL - WC - 2022"
            )

    def test_find_item(self):
        with HTTMock(archive_mock):
            items = self.provider.find(self.query)
        self.assertEqual(len(items.docs), 4)
        self.assertEqual(items._count, 25000)

    @patch("belga.search_providers.session.get")
    def test_fetch(self, session_get):
        response = DetailResponse()
        response.json = MagicMock(return_value=get_belga360_item()[0])
        session_get.return_value = response

        item = self.provider.fetch("urn:belga.be:360archive:39670442")

        url = self.provider.base_url + "archivenewsobjects/39670442"
        session_get.assert_called_with(url, params={}, timeout=TIMEOUT)

        self.assertEqual("urn:belga.be:360archive:39670442", item["guid"])

    def test_get_periods(self):
        arrow.now = MagicMock(return_value=arrow.get("2020-02-14"))
        day_period = self.provider._get_period("day")
        self.assertEqual(day_period["fromDate"], "20200213")
        self.assertEqual(day_period["toDate"], "20200214")

        def get_period(period):
            return self.provider._get_period(period)["fromDate"]

        self.assertEqual(get_period("week"), "20200207")
        self.assertEqual(get_period("month"), "20200114")
        self.assertEqual(get_period("year"), "20190214")

    def test_get_image_renditions(self):
        item = self.provider.format_list_item(get_belga360_item()[3])
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
