# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import html
import datetime
from lxml import etree
from unittest import mock
from bson.objectid import ObjectId

from superdesk.tests import TestCase
from belga.publish.belga_newsml_1_2 import BelgaNewsML12Formatter


@mock.patch(
    'superdesk.publish.subscribers.SubscribersService.generate_sequence_number',
    lambda self, subscriber: 1
)
class BelgaNewsML12FormatterTest(TestCase):
    article = {
        '_id': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
        'guid': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
        'family_id': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
        'event_id': 'tag:localhost:5000:2019:f564b064-d0f9-45b2-b4a8-20a10dcfc761',
        'type': 'text',
        'version': 1,
        'flags': {
            'marked_for_not_publication': False,
            'marked_for_legal': False,
            'marked_archived_only': False,
            'marked_for_sms': False
        },
        'profile': 'belga_text',
        'pubstatus': 'usable',
        'format': 'HTML',
        'template': ObjectId('5c94ead2fe985e1c5776ddca'),
        'task': {
            'desk': ObjectId('5c94ed09fe985e1b69d7cb64'),
            'stage': ObjectId('5c94ed09fe985e1b69d7cb62'),
            'user': ObjectId('5c94ebcdfe985e1c9fc26d52')
        },
        '_updated': datetime.datetime(2019, 4, 3, 12, 45, 14),
        '_created': datetime.datetime(2019, 4, 3, 12, 41, 53),
        '_current_version': 2,
        'firstcreated': datetime.datetime(2019, 4, 3, 12, 41, 53),
        'versioncreated': datetime.datetime(2019, 4, 3, 12, 45, 14),
        'original_creator': '5c94ebcdfe985e1c9fc26d52',
        'unique_id': 43,
        'unique_name': '#43',
        'state': 'in_progress',
        'source': 'Belga',
        'priority': 6,
        'urgency': 4,
        'genre': [{'qcode': 'Article', 'name': 'Article (news)'}],
        'place': [],
        'sign_off': 'ADM',
        'language': 'en',
        'operation': 'update',
        'version_creator': '5c94ebcdfe985e1c9fc26d52',
        'expiry': None,
        'schedule_settings': {'utc_embargo': None, 'time_zone': None},
        '_etag': '61c350853dc1513064f9e566f6d3c161cd387a0f',
        'lock_action': 'edit',
        'lock_session': ObjectId('5ca1cb4afe985e54931ee112'),
        'lock_time': datetime.datetime(2019, 4, 3, 12, 41, 53),
        'lock_user': ObjectId('5c94ebcdfe985e1c9fc26d52'),
        'annotations': [],
        'associations': {},
        'authors': [
            {
                '_id': ['5c94ebcdfe985e1c9fc26d52', 'AUTHOR'],
                'role': 'AUTHOR',
                'name': 'AUTHOR',
                'parent': '5c94ebcdfe985e1c9fc26d52',
                'sub_label': 'admin',
                'scheme': None
            },
            {
                'role': 'EDITOR',
                'name': 'OLEG',
            }
        ],
        'body_html': '<p>Praesent sapien massa, convallis a pellentesque nec, egestas non nisi. '
                     'Curabitur aliquet quam id dui posuere blandit. Curabitur non nulla sit amet '
                     'nisl tempus convallis quis ac lectus.</p>',
        'ednote': 'Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui.',
        'extra': {
            'belga-url': [
                {'url': 'http://example.com/', 'description': 'Example com'},
                {'url': 'https://github.com/superdesk', 'description': 'Superdesk'}
            ],
            "city": "Prague",
            "country": "CZ",
        },
        'fields_meta': {
            'extracountry': {'draftjsState': [{'blocks': [
                {'key': 'cuo9h', 'text': 'Czech Republic', 'type': 'unstyled', 'depth': 0, 'inlineStyleRanges': [],
                 'entityRanges': [], 'data': {'MULTIPLE_HIGHLIGHTS': {}}}], 'entityMap': {}}]
            },
            'extracity': {
                'draftjsState': [{'blocks': [
                    {'key': 'c49mk', 'text': 'Prague', 'type': 'unstyled', 'depth': 0, 'inlineStyleRanges': [],
                     'entityRanges': [], 'data': {'MULTIPLE_HIGHLIGHTS': {}}}], 'entityMap': {}}]
            },
            'headline': {
                'draftjsState': [{'blocks': [
                    {'key': '72fbn', 'text': 'New Skoda Scala', 'type': 'unstyled', 'depth': 0, 'inlineStyleRanges': [],
                     'entityRanges': [], 'data': {'MULTIPLE_HIGHLIGHTS': {}}}], 'entityMap': {}}]
            },
            'body_html': {
                'draftjsState': [{'blocks': [{'key': 'fgaq4',
                                              'text': 'Praesent sapien massa, convallis a pellentesque nec, egestas '
                                                      'non nisi. Curabitur aliquet quam id dui posuere blandit. '
                                                      'Curabitur non nulla sit amet nisl tempus convallis quis ac '
                                                      'lectus.',
                                              'type': 'unstyled', 'depth': 0, 'inlineStyleRanges': [],
                                              'entityRanges': [], 'data': {'MULTIPLE_HIGHLIGHTS': {}}}],
                                  'entityMap': {}}]
            }
        },
        'headline': 'New Skoda Scala',
        'keywords': ['europe', 'Prague', 'CZ', 'Skoda'],
        'slugline': 'skoda scala',
        'subject': [{'name': 'bilingual', 'qcode': 'bilingual', 'scheme': 'distribution'},
                    {'name': 'ANALYSIS', 'qcode': 'ANALYSIS', 'scheme': 'genre'},
                    {'name': 'CURRENT', 'qcode': 'CURRENT', 'scheme': 'genre'},
                    {'name': 'FORECAST', 'qcode': 'FORECAST', 'scheme': 'genre'},
                    {'name': 'A1', 'qcode': 'A1', 'scheme': 'label'}, {'name': 'A2', 'qcode': 'A2', 'scheme': 'label'},
                    {'name': 'R1', 'qcode': 'R1', 'scheme': 'label'},
                    {'name': 'CARS', 'qcode': 'CARS', 'scheme': 'news_products'},
                    {'name': 'CULTURE', 'qcode': 'CULTURE', 'scheme': 'news_products'},
                    {'name': 'BIN', 'qcode': 'BIN', 'scheme': 'news_services'},
                    {'name': 'BRN', 'qcode': 'BRN', 'scheme': 'news_services'},
                    {'name': 'BTL', 'qcode': 'BTL', 'scheme': 'news_services'}],
        'word_count': 28,
        'byline': 'BELGA',
        'administrative': {
            'contributor': 'John',
            'validator': 'John the validator',
            'validation_date': '123123',
            'foreign_id': '4444444'
        },
        'line_type': '1',
        'line_text': 'line text is here',
    }

    subscriber = {
        '_id': 'some_id',
        'name': 'Dev Subscriber',
    }

    def setUp(self):
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
            '20190403T124153'
        )
        self.assertEqual(
            self.newsml.xpath('NewsItem/Identification/NewsIdentifier/NewsItemId')[0].text,
            self.formatter._package_duid
        )
        revisionid = self.newsml.xpath('NewsItem/Identification/NewsIdentifier/RevisionId')[0]
        self.assertEqual(revisionid.text, '2')
        self.assertDictEqual(dict(revisionid.attrib), {'Update': 'N', 'PreviousRevision': '0'})
        self.assertEqual(
            self.newsml.xpath('NewsItem/Identification/NewsIdentifier/PublicIdentifier')[0].text,
            'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5:2N'
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
            '20190403T124153'
        )
        self.assertEqual(
            self.newsml.xpath('NewsItem/NewsManagement/ThisRevisionCreated')[0].text,
            '20190403T124514'
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
                'Duid': 'pkg_urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
                '{http://www.w3.org/XML/1998/namespace}lang': 'en'
            }
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            self.newsml.xpath('NewsItem/NewsComponent/NewsLines/HeadLine')[0].text,
            'New Skoda Scala'
        )
        # NewsML -> NewsItem -> NewsComponent -> AdministrativeMetadata
        self.assertIsNone(
            self.newsml.xpath('NewsItem/NewsComponent/AdministrativeMetadata')[0].text
        )
        # NewsML -> NewsItem -> NewsComponent -> DescriptiveMetadata -> Genre
        self.assertDictEqual(
            dict(self.newsml.xpath('NewsItem/NewsComponent/DescriptiveMetadata/Genre')[0].attrib),
            {'FormalName': 'ANALYSIS'}
        )

    def test_belga_text_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath('NewsItem/NewsComponent/NewsComponent')[0]
        self.assertDictEqual(
            dict(newscomponent_2_level.attrib),
            {
                'Duid': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
                '{http://www.w3.org/XML/1998/namespace}lang': 'en'
            }
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> Role
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('Role')[0].attrib),
            {'FormalName': 'belga_text'}
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines
        self.assertIsNone(
            newscomponent_2_level.xpath('NewsLines/DateLine')[0].text
        )
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'New Skoda Scala'
        )
        self.assertIsNone(
            newscomponent_2_level.xpath('NewsLines/CopyrightLine')[0].text
        )
        self.assertListEqual(
            [kw.text for kw in newscomponent_2_level.xpath('NewsLines/KeywordLine')],
            ['europe', 'Prague', 'CZ', 'Skoda']
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('NewsLines/NewsLine/NewsLineType')[0].attrib),
            {'FormalName': '1'}
        )
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/NewsLine/NewsLineText')[0].text,
            'line text is here'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> AdministrativeMetadata
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Provider/Party')[0].attrib),
            {'FormalName': '1'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Creator/Party')[0].attrib),
            {'FormalName': 'AUTHOR', 'Topic': 'AUTHOR'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Creator/Party')[1].attrib),
            {'FormalName': 'OLEG', 'Topic': 'EDITOR'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Contributor/Party')[0].attrib),
            {'FormalName': 'John'}
        )
        expected_attribs = (
            {'FormalName': 'Validator', 'Value': 'John the validator'},
            {'FormalName': 'ValidationDate', 'Value': '123123'},
            {'FormalName': 'ForeignId', 'Value': '4444444'},
            {'FormalName': 'Priority', 'Value': '6'},
            {'FormalName': 'NewsObjectId', 'Value':
                'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5'},
            {'FormalName': 'NewsPackage'}
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in newscomponent_2_level.xpath('AdministrativeMetadata/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )

        expected_attribs = (
            {'FormalName': 'NewsProduct', 'Value': 'CARS'},
            {'FormalName': 'NewsProduct', 'Value': 'CULTURE'},
            {'FormalName': 'NewsService', 'Value': 'BIN'},
            {'FormalName': 'NewsService', 'Value': 'BRN'},
            {'FormalName': 'NewsService', 'Value': 'BTL'}
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in newscomponent_2_level.xpath('AdministrativeMetadata/Property/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> DescriptiveMetadata
        descriptivemetadata = newscomponent_2_level.xpath('DescriptiveMetadata')[0]
        self.assertDictEqual(
            dict(descriptivemetadata.attrib),
            {'DateAndTime': '20190403T124153'}
        )
        self.assertIsNone(
            descriptivemetadata.xpath('SubjectCode')[0].text
        )
        expected_attribs = (
            {'FormalName': 'City', 'Value': 'Prague'},
            {'FormalName': 'Country', 'Value': 'CZ'},
            {'FormalName': 'CountryArea'},
            {'FormalName': 'WorldRegion'}
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in descriptivemetadata.xpath('Location/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        newscomponent_3_level = newscomponent_2_level.xpath('NewsComponent')[0]
        self.assertDictEqual(
            dict(newscomponent_3_level.attrib),
            {
                'Duid': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
                '{http://www.w3.org/XML/1998/namespace}lang': 'en'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('Role')[0].attrib),
            {
                'FormalName': 'Body',
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('DescriptiveMetadata/Property')[0].attrib),
            {
                'FormalName': 'ComponentClass',
                'Value': 'Text'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('ContentItem/Format')[0].attrib),
            {
                'FormalName': 'Text'
            }
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/DataContent')[0].text,
            '&lt;p&gt;Praesent sapien massa, convallis a pellentesque nec, egestas non nisi. '
            'Curabitur aliquet quam id dui posuere blandit. '
            'Curabitur non nulla sit amet nisl tempus convallis quis ac lectus.&lt;/p&gt;'
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/Characteristics/SizeInBytes')[0].text,
            '203'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        newscomponent_3_level = newscomponent_2_level.xpath('NewsComponent')[1]
        self.assertDictEqual(
            dict(newscomponent_3_level.attrib),
            {
                'Duid': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
                '{http://www.w3.org/XML/1998/namespace}lang': 'en'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('Role')[0].attrib),
            {
                'FormalName': 'Title',
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('DescriptiveMetadata/Property')[0].attrib),
            {
                'FormalName': 'ComponentClass',
                'Value': 'Text'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('ContentItem/Format')[0].attrib),
            {
                'FormalName': 'Text'
            }
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/DataContent')[0].text,
            'New Skoda Scala'
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/Characteristics/SizeInBytes')[0].text,
            '15'
        )

    def test_url_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        self.assertEqual(
            self.newsml.xpath('count(NewsItem/NewsComponent/NewsComponent/Role[@FormalName="URL"])'),
            2
        )
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent/Role[@FormalName="URL"]'
        )[0].getparent()
        self.assertDictEqual(
            dict(newscomponent_2_level.attrib),
            {
                'Duid': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
                '{http://www.w3.org/XML/1998/namespace}lang': 'en'
            }
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> Role
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('Role')[0].attrib),
            {'FormalName': 'URL'}
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines
        self.assertIsNone(
            newscomponent_2_level.xpath('NewsLines/DateLine')[0].text
        )
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'Example com'
        )
        self.assertIsNone(
            newscomponent_2_level.xpath('NewsLines/CopyrightLine')[0].text
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> AdministrativeMetadata
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Provider/Party')[0].attrib),
            {'FormalName': '1'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Creator/Party')[0].attrib),
            {'FormalName': 'AUTHOR', 'Topic': 'AUTHOR'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Creator/Party')[1].attrib),
            {'FormalName': 'OLEG', 'Topic': 'EDITOR'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Contributor/Party')[0].attrib),
            {'FormalName': 'John'}
        )
        expected_attribs = (
            {'FormalName': 'Validator', 'Value': 'John the validator'},
            {'FormalName': 'ValidationDate', 'Value': '123123'},
            {'FormalName': 'ForeignId', 'Value': '4444444'},
            {'FormalName': 'Priority', 'Value': '6'},
            {'FormalName': 'NewsObjectId', 'Value':
                'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5'},
            {'FormalName': 'NewsPackage'}
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in newscomponent_2_level.xpath('AdministrativeMetadata/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )

        expected_attribs = (
            {'FormalName': 'NewsProduct', 'Value': 'CARS'},
            {'FormalName': 'NewsProduct', 'Value': 'CULTURE'},
            {'FormalName': 'NewsService', 'Value': 'BIN'},
            {'FormalName': 'NewsService', 'Value': 'BRN'},
            {'FormalName': 'NewsService', 'Value': 'BTL'}
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in newscomponent_2_level.xpath('AdministrativeMetadata/Property/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> DescriptiveMetadata
        descriptivemetadata = newscomponent_2_level.xpath('DescriptiveMetadata')[0]
        self.assertDictEqual(
            dict(descriptivemetadata.attrib),
            {'DateAndTime': '20190403T124153'}
        )
        self.assertIsNone(
            descriptivemetadata.xpath('SubjectCode')[0].text
        )
        expected_attribs = (
            {'FormalName': 'City', 'Value': 'Prague'},
            {'FormalName': 'Country', 'Value': 'CZ'},
            {'FormalName': 'CountryArea'},
            {'FormalName': 'WorldRegion'}
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in descriptivemetadata.xpath('Location/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        newscomponent_3_level = newscomponent_2_level.xpath('NewsComponent')[0]
        self.assertDictEqual(
            dict(newscomponent_3_level.attrib),
            {
                'Duid': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
                '{http://www.w3.org/XML/1998/namespace}lang': 'en'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('Role')[0].attrib),
            {
                'FormalName': 'Title',
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('DescriptiveMetadata/Property')[0].attrib),
            {
                'FormalName': 'ComponentClass',
                'Value': 'Text'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('ContentItem/Format')[0].attrib),
            {
                'FormalName': 'Text'
            }
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/DataContent')[0].text,
            'Example com'
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/Characteristics/SizeInBytes')[0].text,
            '11'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        newscomponent_3_level = newscomponent_2_level.xpath('NewsComponent')[1]
        self.assertDictEqual(
            dict(newscomponent_3_level.attrib),
            {
                'Duid': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
                '{http://www.w3.org/XML/1998/namespace}lang': 'en'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('Role')[0].attrib),
            {
                'FormalName': 'Locator',
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('DescriptiveMetadata/Property')[0].attrib),
            {
                'FormalName': 'ComponentClass',
                'Value': 'Text'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('ContentItem/Format')[0].attrib),
            {
                'FormalName': 'Text'
            }
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/DataContent')[0].text,
            'http://example.com/'
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/Characteristics/SizeInBytes')[0].text,
            '19'
        )
