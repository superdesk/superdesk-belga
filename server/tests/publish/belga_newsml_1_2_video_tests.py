# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from io import BytesIO
from lxml import etree
from unittest import mock
from bson.objectid import ObjectId

from superdesk.publish import init_app
from belga.publish.belga_newsml_1_2 import BelgaNewsML12Formatter
from .. import TestCase


belga_apiget_response = {
    'galleryId': 6666666,
    'active': True,
    'type': 'C',
    'name': 'JUDO   JPN   WORLD',
    'description': "Noel Van T End of Netherlands (L) celebrates after winning the gold medal.",
    'createDate': '2019-08-30T14:33:10Z',
    'deadlineDate': None,
    'author': 'auto',
    'credit': 'AFP',
    'category': None,
    'tagAuthor': None,
    'iconImageId': 777777777,
    'iconThumbnailUrl': 'https://2.t.cdn.belga.be/belgaimage:154669691:800x800:w?v=6666666&m=aaaaaaaa',
    'nrImages': 364,
    'themes': ['all', 'news', 'sports']
}


class BelgaNewsML12FormatterVideoTest(TestCase):
    article = {
        "_id": "urn:newsml:localhost:5000:2019-08-14T16:51:06.604540:734d4292-db4f-4358-8b2f-c2273a4925d5",
        "media": "video_1",
        "type": "video",
        "pubstatus": "usable",
        "format": "HTML",
        "firstcreated": "2019-08-14T14:51:06+0000",
        "versioncreated": "2019-08-14T14:51:06+0000",
        "original_creator": "5d385f31fe985ec67a0ca583",
        "guid": "tag:localhost:5000:2019:3fe341ab-45d8-4f72-9308-adde548daef8",
        "unique_id": 13,
        "unique_name": "#13",
        "family_id": "urn:newsml:localhost:5000:2019-08-14T16:51:06."
                     "604540:734d4292-db4f-4358-8b2f-c2273a4925d5",
        "event_id": "tag:localhost:5000:2019:d8846c42-d18a-447d-96e2-c3173c3adfdd",
        "state": "in_progress",
        "source": "Superdesk",
        "priority": 6,
        "urgency": 3,
        "genre": [
            {
                "qcode": "Article",
                "name": "Article (news)"
            }
        ],
        "place": [],
        "sign_off": "ADM",
        "language": "nl",
        "operation": "update",
        "version_creator": "5d385f31fe985ec67a0ca583",
        "renditions": {
            "original": {
                "href": "http://localhost:5000/api/upload-raw/video_1.mp4",
                "media": "video_1",
                "mimetype": "video/mp4"
            }
        },
        "mimetype": "video/mp4",
        "filemeta_json": "{\"duration\": \"0:00:09.482000\", \"width\": \"640\", \"height\": \"360\", \"creatio"
                         "n_date\": \"2019-06-16T17:32:12+00:00\", \"last_modification\": \"2019-06-16T17:32:12"
                         "+00:00\", \"comment\": \"User volume: 100.0%\", \"mime_type\": \"video/mp4\", \"endia"
                         "n\": \"Big endian\", \"length\": 1022462}",
        "description_text": "water",
        "expiry": "2046-12-29T14:51:06+0000",
        "headline": "water",
        "version": 2,
        "_current_version": 2,
    }

    archive = (
        {
            "_id": "urn:newsml:localhost:5000:2019-08-14T16:51:06.604540:734d4292-db4f-4358-8b2f-c2273a4925d5",
            "media": "video_1",
            "type": "video",
            "pubstatus": "usable",
            "format": "HTML",
            "firstcreated": "2019-08-14T14:51:06+0000",
            "versioncreated": "2019-08-14T14:51:06+0000",
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "tag:localhost:5000:2019:3fe341ab-45d8-4f72-9308-adde548daef8",
            "unique_id": 13,
            "unique_name": "#13",
            "family_id": "urn:newsml:localhost:5000:2019-08-14T16:51:06."
                         "604540:734d4292-db4f-4358-8b2f-c2273a4925d5",
            "event_id": "tag:localhost:5000:2019:d8846c42-d18a-447d-96e2-c3173c3adfdd",
            "state": "in_progress",
            "source": "Superdesk",
            "priority": 6,
            "urgency": 3,
            "genre": [
                {
                    "qcode": "Article",
                    "name": "Article (news)"
                }
            ],
            "place": [],
            "sign_off": "ADM",
            "language": "nl",
            "operation": "update",
            "version_creator": "5d385f31fe985ec67a0ca583",
            "renditions": {
                "original": {
                    "href": "http://localhost:5000/api/upload-raw/video_1.mp4",
                    "media": "video_1",
                    "mimetype": "video/mp4"
                }
            },
            "mimetype": "video/mp4",
            "filemeta_json": "{\"duration\": \"0:00:09.482000\", \"width\": \"640\", \"height\": \"360\", \"creatio"
                             "n_date\": \"2019-06-16T17:32:12+00:00\", \"last_modification\": \"2019-06-16T17:32:12"
                             "+00:00\", \"comment\": \"User volume: 100.0%\", \"mime_type\": \"video/mp4\", \"endia"
                             "n\": \"Big endian\", \"length\": 1022462}",
            "description_text": "water",
            "expiry": "2046-12-29T14:51:06+0000",
            "headline": "water",
            "version": 2,
            "_current_version": 2,
        },
    )

    users = (
        {
            "_id": ObjectId("5d385f31fe985ec67a0ca583"),
            "username": "admin",
            "password": "blabla",
            "email": "admin@example.com",
            "user_type": "administrator",
            "is_active": True,
            "needs_activation": False,
            "is_author": True,
            "is_enabled": True,
            "display_name": "John Smith",
            "sign_off": "ADM",
            "first_name": "John",
            "last_name": "Smith",
            "role": ObjectId("5d542206c04280bc6d6157f9"),
        },
    )

    roles = (
        {
            "_id": ObjectId("5d542206c04280bc6d6157f9"),
            "author_role": "AUTHOR",
            "editor_role": "AUTHOR"
        },
    )

    vocabularies = (
        {
            "_id": "belga-coverage-new",
            "field_type": "custom",
            "items": [],
            "type": "manageable",
            "schema": {
                "name": {},
                "qcode": {},
                "parent": {}
            },
            "service": {
                "all": 1
            },
            "custom_field_type": "belga.coverage",
            "display_name": "belga coverage new",
            "unique_field": "qcode",
        },
    )

    subscriber = {
        '_id': 'some_id',
        'name': 'Dev Subscriber',
    }

    @mock.patch('superdesk.publish.subscribers.SubscribersService.generate_sequence_number', lambda s, sub: 1)
    @mock.patch('belga.search_providers.BelgaCoverageSearchProvider.api_get',
                lambda self, endpoint, params: belga_apiget_response)
    def setUp(self):
        init_app(self.app)
        self.app.data.insert('users', self.users)
        self.app.data.insert('archive', self.archive)
        self.app.data.insert('roles', self.roles)
        self.app.data.insert('vocabularies', self.vocabularies)
        # insert pictures
        media_items = (
            {
                '_id': 'video_1',
                'content': BytesIO(b'czech rap xD'),
                'content_type': 'video/mp4',
                'metadata': {
                    'length': 12
                }
            },
        )
        for media_item in media_items:
            # base rendition
            self.app.media.put(**media_item)

        self.article['state'] = 'published'
        self.formatter = BelgaNewsML12Formatter()
        seq, doc = self.formatter.format(self.article, self.subscriber)[0]
        self.newsml = etree.XML(bytes(bytearray(doc, encoding=BelgaNewsML12Formatter.ENCODING)))

    def test_catalog(self):
        # NewsML -> Catalog
        catalog = self.newsml.xpath('Catalog')[0]
        self.assertEqual(
            catalog.get('Href'),
            'http://www.belga.be/dtd/BelgaCatalog.xml'
        )

    def test_newsenvelope(self):
        # NewsML -> NewsEnvelope
        self.assertEqual(
            self.newsml.xpath('NewsEnvelope/DateAndTime')[0].text,
            self.formatter._string_now
        )
        self.assertIsNone(
            self.newsml.xpath('NewsEnvelope/NewsService')[0].text,
        )
        self.assertIsNone(
            self.newsml.xpath('NewsEnvelope/NewsProduct')[0].text,
        )

    def test_identification(self):
        # NewsML -> NewsItem -> Identification
        with self.app.app_context():
            self.assertEqual(
                self.newsml.xpath('NewsItem/Identification/NewsIdentifier/ProviderId')[0].text,
                self.app.config['NEWSML_PROVIDER_ID']
            )
        self.assertEqual(
            self.newsml.xpath('NewsItem/Identification/NewsIdentifier/DateId')[0].text,
            '20190814T145106'
        )
        self.assertEqual(
            self.newsml.xpath('NewsItem/Identification/NewsIdentifier/NewsItemId')[0].text,
            self.formatter._duid
        )
        revisionid = self.newsml.xpath('NewsItem/Identification/NewsIdentifier/RevisionId')[0]
        self.assertEqual(revisionid.text, '2')
        self.assertDictEqual(dict(revisionid.attrib), {'Update': 'N', 'PreviousRevision': '0'})
        self.assertEqual(
            self.newsml.xpath('NewsItem/Identification/NewsIdentifier/PublicIdentifier')[0].text,
            'urn:newsml:localhost:5000:2019-08-14T16:51:06.604540:734d4292-db4f-4358-8b2f-c2273a4925d5:2N'
        )

    def test_newsmanagement(self):
        # NewsML -> NewsItem -> NewsManagement
        newsitemtype = self.newsml.xpath('NewsItem/NewsManagement/NewsItemType')[0]
        self.assertDictEqual(
            dict(newsitemtype.attrib),
            {'FormalName': 'News'}
        )
        self.assertIsNone(newsitemtype.text)
        self.assertEqual(
            self.newsml.xpath('NewsItem/NewsManagement/FirstCreated')[0].text,
            '20190814T145106'
        )
        self.assertEqual(
            self.newsml.xpath('NewsItem/NewsManagement/ThisRevisionCreated')[0].text,
            '20190814T145106'
        )
        status = self.newsml.xpath('NewsItem/NewsManagement/Status')[0]
        self.assertDictEqual(
            dict(status.attrib),
            {'FormalName': 'USABLE'}
        )
        self.assertIsNone(status.text)

    def test_1_level_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent
        newscomponent_1_level = self.newsml.xpath('NewsItem/NewsComponent')[0]
        self.assertDictEqual(
            dict(newscomponent_1_level.attrib),
            {
                'Duid': 'tag:localhost:5000:2019:3fe341ab-45d8-4f72-9308-adde548daef8',
                '{http://www.w3.org/XML/1998/namespace}lang': 'nl'
            }
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            self.newsml.xpath('NewsItem/NewsComponent/NewsLines/HeadLine')[0].text,
            'water'
        )
        # NewsML -> NewsItem -> NewsComponent -> AdministrativeMetadata
        self.assertIsNone(
            self.newsml.xpath('NewsItem/NewsComponent/AdministrativeMetadata')[0].text
        )
        # NewsML -> NewsItem -> NewsComponent -> DescriptiveMetadata -> Genre
        self.assertDictEqual(
            dict(self.newsml.xpath('NewsItem/NewsComponent/DescriptiveMetadata/Genre')[0].attrib),
            {'FormalName': ''}
        )

    def test_video(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="tag:localhost:5000:2019:3fe341ab-45d8-4f72-9308-adde548daef8"]'
        )[0]
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> Role
        self.assertEqual(
            newscomponent_2_level.xpath('Role[@FormalName="Video"]')[0].text,
            None
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CreditLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'water'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(title) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'water'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '5'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Body) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'water'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )[0]
        self.assertEqual(
            sizeinbytes.text,
            '5'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Clip"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:video_1'
        )
        _format = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Clip"]/ancestor::NewsComponent/ContentItem/Format'
        )[0]
        self.assertEqual(
            _format.attrib['FormalName'],
            'Mp4'
        )
        mimetype = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Clip"]/ancestor::NewsComponent/ContentItem/MimeType'
        )[0]
        self.assertEqual(
            mimetype.attrib['FormalName'],
            'video/mp4'
        )
