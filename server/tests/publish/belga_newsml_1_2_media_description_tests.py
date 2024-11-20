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
import pytz
import datetime
from lxml import etree
from unittest import mock
from bson.objectid import ObjectId

from superdesk.publish import init_app
from belga.publish.belga_newsml_1_2 import BelgaNewsML12Formatter
from .. import TestCase


class BelgaNewsML12FormatterTextTest(TestCase):
    article = {
        "_id": "urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5",
        "guid": "urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5",
        "family_id": "urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5",
        "event_id": "tag:localhost:5000:2019:f564b064-d0f9-45b2-b4a8-20a10dcfc761",
        "type": "text",
        "version": 1,
        "profile": "belga_text",
        "pubstatus": "usable",
        "format": "HTML",
        "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
        "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
        "_current_version": 2,
        "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
        "versioncreated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
        "firstpublished": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
        "original_creator": "5d385f31fe985ec67a0ca583",
        "state": "in_progress",
        "source": "Belga",
        "priority": 6,
        "urgency": 4,
        "genre": [{"qcode": "Article", "name": "Article (news)"}],
        "place": [],
        "sign_off": "ADM",
        "language": "nl",
        "operation": "update",
        "version_creator": "5d385f31fe985ec67a0ca583",
        "_etag": "61c350853dc1513064f9e566f6d3c161cd387a0f",
        "associations": {
            "belga_related_images--1": {"_id": "pic-1", "type": "picture"},
            "belga_related_images--2": {"_id": "pic-2", "type": "picture"},
            "belga_related_images--3": {"_id": "pic-3", "type": "picture"},
            "belga_related_images--4": {"_id": "pic-4", "type": "picture"},
            "belga_related_articles--1": {"_id": "video-1", "type": "video"},
            "belga_related_articles--2": {"_id": "video-2", "type": "video"},
            "belga_related_articles--3": {"_id": "video-3", "type": "video"},
            "belga_related_articles--4": {"_id": "video-4", "type": "video"},
        },
        "authors": [
            {
                "_id": ["5d385f31fe985ec67a0ca583", "AUTHOR"],
                "role": "AUTHOR",
                "name": "AUTHOR",
                "parent": "5d385f31fe985ec67a0ca583",
                "sub_label": "John Smith",
                "scheme": None,
            },
            {
                "role": "EDITOR",
                "name": "OLEG",
            },
        ],
        "body_html": "",
        "headline": "New Skoda Scala",
        "slugline": "skoda scala",
        "word_count": 28,
        "byline": "BELGA",
    }

    archive = (
        {
            "_id": "pic-1",
            "media": "pic_1",
            "type": "picture",
            "pubstatus": "usable",
            "format": "HTML",
            "firstcreated": "2019-08-14T14:51:06+0000",
            "versioncreated": "2019-08-14T14:51:06+0000",
            "firstpublished": "2019-08-14T14:51:06+0000",
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "pic-1",
            "state": "in_progress",
            "source": "Superdesk",
            "priority": 6,
            "urgency": 3,
            "sign_off": "ADM",
            "language": "nl",
            "operation": "update",
            "version_creator": "5d385f31fe985ec67a0ca583",
            "renditions": {
                "original": {
                    "href": "http://localhost:5000/api/upload-raw/pic_1.jpg",
                    "media": "pic_1",
                    "mimetype": "image/jpeg",
                    "width": 3000,
                    "height": 2000,
                },
            },
            "mimetype": "image/jpeg",
            "description_text": "water",
            "headline": "water",
            "version": 2,
            "_current_version": 2,
        },
        {
            "_id": "pic-2",
            "media": "pic_1",
            "type": "picture",
            "pubstatus": "usable",
            "format": "HTML",
            "firstcreated": "2019-08-14T14:51:06+0000",
            "versioncreated": "2019-08-14T14:51:06+0000",
            "firstpublished": "2019-08-14T14:51:06+0000",
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "pic-2",
            "state": "in_progress",
            "source": "Superdesk",
            "priority": 6,
            "urgency": 3,
            "sign_off": "ADM",
            "language": "nl",
            "operation": "update",
            "version_creator": "5d385f31fe985ec67a0ca583",
            "renditions": {
                "original": {
                    "href": "http://localhost:5000/api/upload-raw/pic_1.jpg",
                    "media": "pic_1",
                    "mimetype": "image/jpeg",
                    "width": 3000,
                    "height": 2000,
                },
            },
            "mimetype": "image/jpeg",
            "description_text": "water",
            "headline": "water",
            "version": 2,
            "_current_version": 2,
            "extra": {"people": "John Smith"},
        },
        {
            "_id": "pic-3",
            "media": "pic_1",
            "type": "picture",
            "pubstatus": "usable",
            "format": "HTML",
            "firstcreated": "2019-08-14T14:51:06+0000",
            "versioncreated": "2019-08-14T14:51:06+0000",
            "firstpublished": "2019-08-14T14:51:06+0000",
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "pic-3",
            "state": "in_progress",
            "source": "Superdesk",
            "priority": 6,
            "urgency": 3,
            "sign_off": "ADM",
            "language": "nl",
            "operation": "update",
            "version_creator": "5d385f31fe985ec67a0ca583",
            "renditions": {
                "original": {
                    "href": "http://localhost:5000/api/upload-raw/pic_1.jpg",
                    "media": "pic_1",
                    "mimetype": "image/jpeg",
                    "width": 3000,
                    "height": 2000,
                },
            },
            "mimetype": "image/jpeg",
            "description_text": "water",
            "headline": "water",
            "version": 2,
            "_current_version": 2,
            "extra": {
                "event_description": "killing",
            },
        },
        {
            "_id": "pic-4",
            "media": "pic_1",
            "type": "picture",
            "pubstatus": "usable",
            "format": "HTML",
            "firstcreated": "2019-08-14T14:51:06+0000",
            "versioncreated": "2019-08-14T14:51:06+0000",
            "firstpublished": "2019-08-14T14:51:06+0000",
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "pic-4",
            "state": "in_progress",
            "source": "Superdesk",
            "priority": 6,
            "urgency": 3,
            "sign_off": "ADM",
            "language": "nl",
            "operation": "update",
            "version_creator": "5d385f31fe985ec67a0ca583",
            "renditions": {
                "original": {
                    "href": "http://localhost:5000/api/upload-raw/pic_1.jpg",
                    "media": "pic_1",
                    "mimetype": "image/jpeg",
                    "width": 3000,
                    "height": 2000,
                },
            },
            "mimetype": "image/jpeg",
            "description_text": "water",
            "headline": "water",
            "version": 2,
            "_current_version": 2,
            "extra": {
                "people": "John Smith",
                "event_description": "killing",
            },
        },
        {
            "_id": "video-1",
            "media": "video_1",
            "type": "video",
            "pubstatus": "usable",
            "format": "HTML",
            "firstcreated": "2019-08-14T14:51:06+0000",
            "versioncreated": "2019-08-14T14:51:06+0000",
            "firstpublished": "2019-08-14T14:51:06+0000",
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "video-1",
            "state": "in_progress",
            "source": "Superdesk",
            "priority": 6,
            "urgency": 3,
            "sign_off": "ADM",
            "language": "nl",
            "operation": "update",
            "version_creator": "5d385f31fe985ec67a0ca583",
            "renditions": {
                "original": {
                    "href": "http://localhost:5000/api/upload-raw/video_1.mp4",
                    "media": "video_1",
                    "mimetype": "video/mp4",
                }
            },
            "mimetype": "video/mp4",
            "filemeta_json": '{"duration": "0:00:09.482000", "width": "640", "height": "360", "creatio'
            'n_date": "2019-06-16T17:32:12+00:00", "last_modification": "2019-06-16T17:32:12'
            '+00:00", "comment": "User volume: 100.0%", "mime_type": "video/mp4", "endia'
            'n": "Big endian", "length": 1022462}',
            "description_text": "water",
            "headline": "water",
            "version": 2,
            "_current_version": 2,
        },
        {
            "_id": "video-2",
            "media": "video_1",
            "type": "video",
            "pubstatus": "usable",
            "format": "HTML",
            "firstcreated": "2019-08-14T14:51:06+0000",
            "versioncreated": "2019-08-14T14:51:06+0000",
            "firstpublished": "2019-08-14T14:51:06+0000",
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "video-2",
            "state": "in_progress",
            "source": "Superdesk",
            "priority": 6,
            "urgency": 3,
            "sign_off": "ADM",
            "language": "nl",
            "operation": "update",
            "version_creator": "5d385f31fe985ec67a0ca583",
            "renditions": {
                "original": {
                    "href": "http://localhost:5000/api/upload-raw/video_1.mp4",
                    "media": "video_1",
                    "mimetype": "video/mp4",
                }
            },
            "mimetype": "video/mp4",
            "filemeta_json": '{"duration": "0:00:09.482000", "width": "640", "height": "360", "creatio'
            'n_date": "2019-06-16T17:32:12+00:00", "last_modification": "2019-06-16T17:32:12'
            '+00:00", "comment": "User volume: 100.0%", "mime_type": "video/mp4", "endia'
            'n": "Big endian", "length": 1022462}',
            "description_text": "water",
            "headline": "water",
            "version": 2,
            "_current_version": 2,
            "extra": {"people": "John Smith"},
        },
        {
            "_id": "video-3",
            "media": "video_1",
            "type": "video",
            "pubstatus": "usable",
            "format": "HTML",
            "firstcreated": "2019-08-14T14:51:06+0000",
            "versioncreated": "2019-08-14T14:51:06+0000",
            "firstpublished": "2019-08-14T14:51:06+0000",
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "video-3",
            "state": "in_progress",
            "source": "Superdesk",
            "priority": 6,
            "urgency": 3,
            "sign_off": "ADM",
            "language": "nl",
            "operation": "update",
            "version_creator": "5d385f31fe985ec67a0ca583",
            "renditions": {
                "original": {
                    "href": "http://localhost:5000/api/upload-raw/video_1.mp4",
                    "media": "video_1",
                    "mimetype": "video/mp4",
                }
            },
            "mimetype": "video/mp4",
            "filemeta_json": '{"duration": "0:00:09.482000", "width": "640", "height": "360", "creatio'
            'n_date": "2019-06-16T17:32:12+00:00", "last_modification": "2019-06-16T17:32:12'
            '+00:00", "comment": "User volume: 100.0%", "mime_type": "video/mp4", "endia'
            'n": "Big endian", "length": 1022462}',
            "description_text": "water",
            "headline": "water",
            "version": 2,
            "_current_version": 2,
            "extra": {
                "event_description": "killing",
            },
        },
        {
            "_id": "video-4",
            "media": "video_1",
            "type": "video",
            "pubstatus": "usable",
            "format": "HTML",
            "firstcreated": "2019-08-14T14:51:06+0000",
            "versioncreated": "2019-08-14T14:51:06+0000",
            "firstpublished": "2019-08-14T14:51:06+0000",
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "video-4",
            "state": "in_progress",
            "source": "Superdesk",
            "priority": 6,
            "urgency": 3,
            "sign_off": "ADM",
            "language": "nl",
            "operation": "update",
            "version_creator": "5d385f31fe985ec67a0ca583",
            "renditions": {
                "original": {
                    "href": "http://localhost:5000/api/upload-raw/video_1.mp4",
                    "media": "video_1",
                    "mimetype": "video/mp4",
                }
            },
            "mimetype": "video/mp4",
            "filemeta_json": '{"duration": "0:00:09.482000", "width": "640", "height": "360", "creatio'
            'n_date": "2019-06-16T17:32:12+00:00", "last_modification": "2019-06-16T17:32:12'
            '+00:00", "comment": "User volume: 100.0%", "mime_type": "video/mp4", "endia'
            'n": "Big endian", "length": 1022462}',
            "description_text": "water",
            "headline": "water",
            "version": 2,
            "_current_version": 2,
            "extra": {
                "people": "John Smith",
                "event_description": "killing",
            },
        },
    )

    users = (
        {
            "_id": ObjectId("5d385f31fe985ec67a0ca583"),
            "username": "adm",
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
        },
    )

    subscriber = {
        "_id": "some_id",
        "name": "Dev Subscriber",
    }

    @mock.patch(
        "superdesk.publish.subscribers.SubscribersService.generate_sequence_number",
        lambda s, sub: 1,
    )
    def setUp(self):
        init_app(self.app)
        self.app.data.insert("users", self.users)
        self.app.data.insert("archive", self.archive)

        # insert pictures
        media_items = (
            {
                "_id": "pic_1",
                "content": BytesIO(b"pic_one_content"),
                "content_type": "image/jpeg",
                "metadata": {"length": 10},
            },
            {
                "_id": "video_1",
                "content": BytesIO(b"czech rap xD"),
                "content_type": "video/mp4",
                "metadata": {"length": 12},
            },
        )
        for media_item in media_items:
            # base rendition
            self.app.media.put(**media_item)

        self.article["state"] = "published"
        self.formatter = BelgaNewsML12Formatter()
        seq, doc = self.formatter.format(self.article, self.subscriber)[0]
        self.newsml = etree.XML(
            bytes(bytearray(doc, encoding=BelgaNewsML12Formatter.ENCODING))
        )

    def test_video_description(self):
        # no `people` && no `event_description`
        newscomponent_2_level = self.newsml.xpath(
            "NewsItem/NewsComponent/NewsComponent" '[@Duid="video-1"]'
        )[0]
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(datacontent.text, "water")
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent'
            "/ContentItem/Characteristics/SizeInBytes"
        )[0]
        self.assertEqual(sizeinbytes.text, "5")
        # `people` && no `event_description`
        newscomponent_2_level = self.newsml.xpath(
            "NewsItem/NewsComponent/NewsComponent" '[@Duid="video-2"]'
        )[0]
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(datacontent.text, "Video showing John Smith")
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent'
            "/ContentItem/Characteristics/SizeInBytes"
        )[0]
        self.assertEqual(sizeinbytes.text, "24")
        # not `people` && `event_description`
        newscomponent_2_level = self.newsml.xpath(
            "NewsItem/NewsComponent/NewsComponent" '[@Duid="video-3"]'
        )[0]
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(datacontent.text, "Video showing killing")
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent'
            "/ContentItem/Characteristics/SizeInBytes"
        )[0]
        self.assertEqual(sizeinbytes.text, "21")
        # `people` && `event_description`
        newscomponent_2_level = self.newsml.xpath(
            "NewsItem/NewsComponent/NewsComponent" '[@Duid="video-4"]'
        )[0]
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(datacontent.text, "John Smith on the video regarding killing")
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent'
            "/ContentItem/Characteristics/SizeInBytes"
        )[0]
        self.assertEqual(sizeinbytes.text, "41")

    def test_picture_description(self):
        # no `people` && no `event_description`
        newscomponent_2_level = self.newsml.xpath(
            "NewsItem/NewsComponent/NewsComponent" '[@Duid="pic-1"]'
        )[0]
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(datacontent.text, "water")
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent'
            "/ContentItem/Characteristics/SizeInBytes"
        )[0]
        self.assertEqual(sizeinbytes.text, "5")
        # `people` && no `event_description`
        newscomponent_2_level = self.newsml.xpath(
            "NewsItem/NewsComponent/NewsComponent" '[@Duid="pic-2"]'
        )[0]
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(datacontent.text, "Picture showing John Smith")
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent'
            "/ContentItem/Characteristics/SizeInBytes"
        )[0]
        self.assertEqual(sizeinbytes.text, "26")
        # not `people` && `event_description`
        newscomponent_2_level = self.newsml.xpath(
            "NewsItem/NewsComponent/NewsComponent" '[@Duid="pic-3"]'
        )[0]
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(datacontent.text, "Picture showing killing")
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent'
            "/ContentItem/Characteristics/SizeInBytes"
        )[0]
        self.assertEqual(sizeinbytes.text, "23")
        # `people` && `event_description`
        newscomponent_2_level = self.newsml.xpath(
            "NewsItem/NewsComponent/NewsComponent" '[@Duid="pic-4"]'
        )[0]
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text, "John Smith on the picture regarding killing"
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent'
            "/ContentItem/Characteristics/SizeInBytes"
        )[0]
        self.assertEqual(sizeinbytes.text, "43")
