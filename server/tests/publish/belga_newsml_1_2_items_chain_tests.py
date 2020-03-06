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
import datetime
from lxml import etree
from unittest import mock
from bson.objectid import ObjectId

from superdesk.tests import TestCase
from superdesk.publish import init_app
from belga.publish.belga_newsml_1_2 import BelgaNewsML12Formatter

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


class BelgaNewsML12FormatterTextTest(TestCase):
    article = {
        '_id': 'update-2',
        'guid': 'update-2',
        'type': 'text',
        'version': 1,
        'profile': 'belga_text',
        'pubstatus': 'usable',
        'format': 'HTML',
        'template': ObjectId('5c94ead2fe985e1c5776ddca'),
        '_updated': datetime.datetime(2019, 4, 3, 12, 45, 14),
        '_created': datetime.datetime(2019, 4, 3, 12, 41, 53),
        'firstcreated': datetime.datetime(2019, 4, 3, 12, 41, 53),
        'versioncreated': datetime.datetime(2019, 4, 3, 12, 45, 14),
        'original_creator': '5d385f31fe985ec67a0ca583',
        'state': 'in_progress',
        'source': 'Belga',
        'priority': 6,
        'urgency': 4,
        'language': 'nl',
        'headline': 'New Skoda Scala 2',
        'keywords': ['europe', 'Prague', 'CZ', 'Skoda'],
        'slugline': 'skoda scala',
        'byline': 'BELGA',
        "rewrite_of": "update-1",
        "rewrite_sequence": 2,
    }

    archive = (
        {
            '_id': 'original',
            'guid': 'original',
            'type': 'text',
            'version': 1,
            'profile': 'belga_text',
            'pubstatus': 'usable',
            'format': 'HTML',
            'template': ObjectId('5c94ead2fe985e1c5776ddca'),
            '_updated': datetime.datetime(2019, 4, 3, 12, 45, 14),
            '_created': datetime.datetime(2019, 4, 3, 12, 41, 53),
            'firstcreated': datetime.datetime(2019, 4, 3, 12, 41, 53),
            'versioncreated': datetime.datetime(2019, 4, 3, 12, 45, 14),
            'original_creator': '5d385f31fe985ec67a0ca583',
            'state': 'in_progress',
            'source': 'Belga',
            'priority': 6,
            'urgency': 4,
            'language': 'nl',
            'headline': 'New Skoda Scala',
            'keywords': ['europe', 'Prague', 'CZ', 'Skoda'],
            'slugline': 'skoda scala',
            'byline': 'BELGA',
            'rewritten_by': 'update-1'
        },
        {
            '_id': 'update-1',
            'guid': 'update-1',
            'type': 'text',
            'version': 1,
            'profile': 'belga_text',
            'pubstatus': 'usable',
            'format': 'HTML',
            'template': ObjectId('5c94ead2fe985e1c5776ddca'),
            '_updated': datetime.datetime(2019, 4, 3, 12, 45, 14),
            '_created': datetime.datetime(2019, 4, 3, 12, 41, 53),
            'firstcreated': datetime.datetime(2019, 4, 3, 12, 41, 53),
            'versioncreated': datetime.datetime(2019, 4, 3, 12, 45, 14),
            'original_creator': '5d385f31fe985ec67a0ca583',
            'state': 'in_progress',
            'source': 'Belga',
            'priority': 6,
            'urgency': 4,
            'language': 'nl',
            'headline': 'New Skoda Scala 1',
            'keywords': ['europe', 'Prague', 'CZ', 'Skoda'],
            'slugline': 'skoda scala',
            'byline': 'BELGA',
            'rewritten_by': 'update-2',
            "rewrite_of": "original",
            "rewrite_sequence": 1,
        },
        {
            '_id': 'update-2',
            'guid': 'update-2',
            'type': 'text',
            'version': 1,
            'profile': 'belga_text',
            'pubstatus': 'usable',
            'format': 'HTML',
            'template': ObjectId('5c94ead2fe985e1c5776ddca'),
            '_updated': datetime.datetime(2019, 4, 3, 12, 45, 14),
            '_created': datetime.datetime(2019, 4, 3, 12, 41, 53),
            'firstcreated': datetime.datetime(2019, 4, 3, 12, 41, 53),
            'versioncreated': datetime.datetime(2019, 4, 3, 12, 45, 14),
            'original_creator': '5d385f31fe985ec67a0ca583',
            'state': 'in_progress',
            'source': 'Belga',
            'priority': 6,
            'urgency': 4,
            'language': 'nl',
            'headline': 'New Skoda Scala 2',
            'keywords': ['europe', 'Prague', 'CZ', 'Skoda'],
            'slugline': 'skoda scala',
            'byline': 'BELGA',
            "rewrite_of": "update-1",
            "rewrite_sequence": 2,
        }
    )

    users = ({
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
        "role": ObjectId("5d542206c04280bc6d6157f9"),
    },)

    roles = ({
        "_id": ObjectId("5d542206c04280bc6d6157f9"),
        "author_role": "AUTHOR",
        "editor_role": "AUTHOR"
    },)

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
    def setUp(self):
        init_app(self.app)
        self.app.data.insert('users', self.users)
        self.app.data.insert('archive', self.archive)
        self.app.data.insert('roles', self.roles)
        self.app.data.insert('vocabularies', self.vocabularies)

        self.article['state'] = 'published'
        self.formatter = BelgaNewsML12Formatter()
        seq, doc = self.formatter.format(self.article, self.subscriber)[0]
        self.newsml = etree.XML(bytes(bytearray(doc, encoding=BelgaNewsML12Formatter.ENCODING)))

    def test_newsitemid(self):
        # NewsML -> NewsItem -> Identification
        self.assertEqual(
            self.newsml.xpath('NewsItem/Identification/NewsIdentifier/NewsItemId')[0].text,
            'original'
        )

    def test_1_level_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent
        newscomponent_1_level = self.newsml.xpath('NewsItem/NewsComponent')[0]
        self.assertDictEqual(
            dict(newscomponent_1_level.attrib),
            {
                'Duid': 'original',
                '{http://www.w3.org/XML/1998/namespace}lang': 'nl'
            }
        )

    def test_belga_text_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        ids = (
            'original',
            'update-1',
            'update-2',
        )
        for i, newscomponent_2_level in enumerate(self.newsml.xpath('NewsItem/NewsComponent/NewsComponent')):
            self.assertDictEqual(
                dict(newscomponent_2_level.attrib),
                {
                    'Duid': ids[i],
                    '{http://www.w3.org/XML/1998/namespace}lang': 'nl'
                }
            )
