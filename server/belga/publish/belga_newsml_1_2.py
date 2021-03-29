# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import pytz
import logging
from copy import deepcopy
from typing import NamedTuple
from urllib.parse import urljoin
from dateutil import parser as dateutil_parser

from lxml import etree
from lxml.etree import SubElement
from lxml.html.clean import Cleaner
from eve.utils import config
from eve.utils import ParsedRequest
from flask import current_app as app

import superdesk
from superdesk.etree import parse_html, to_string
from superdesk import text_utils
from apps.archive.common import get_utc_schedule
from superdesk.errors import FormatterError
from superdesk.metadata.item import (CONTENT_TYPE, EMBARGO, GUID_FIELD,
                                     ITEM_TYPE, ITEM_STATE, CONTENT_STATE)
from superdesk.publish.formatters import NewsML12Formatter
from superdesk.publish.formatters.newsml_g2_formatter import XML_LANG
from ..search_providers import BelgaImageSearchProvider, BelgaCoverageSearchProvider

logger = logging.getLogger(__name__)


def generate_sequence_number(subscriber):
    """
    Generate a publish sequence number.
    Function is used to mock this part when you call formatter directly from the python script during development.
    Example:
        ```
        from unittest import mock
        from app import get_app
        from belga.publish import belga_newsml_1_2

        app = get_app()
        with app.app_context():
            article = app.data.find_one(
                'archive',
                req=None,
                _id='urn:newsml:localhost:5000:...'
            )
            article['state'] = 'published'
            with mock.patch.object(belga_newsml_1_2, 'generate_sequence_number') as gen_seq_num_mock:
                gen_seq_num_mock.return_value = 1
                result = belga_newsml_1_2.BelgaNewsML12Formatter().format(
                    article=article,
                    subscriber={}
                )
            with open('/path/to/output/result.xml', 'w') as f:
                f.write(result[0][1])
            ```
    """
    return superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)


class NewsComponent2Roles(NamedTuple):
    URL: str
    PICTURE: str
    GALLERY: str
    AUDIO: str
    VIDEO: str
    RELATED_DOCUMENT: str
    RELATED_ARTICLE: str


class BelgaNewsML12Formatter(NewsML12Formatter):
    """
    Belga News ML 1.2 Formatter
    """

    ENCODING = "UTF-8"
    XML_ROOT = '<?xml version="1.0" encoding="{}"?>'.format(ENCODING)
    DATETIME_FORMAT = '%Y%m%dT%H%M%S'
    BELGA_TEXT_PROFILE = 'belga_text'
    DEFAULT_CREDITLINE = 'BELGA'

    SD_BELGA_IMAGE_RENDITIONS_MAP = {
        'original': 'full',
        'thumbnail': 'thumbnail',
        'viewImage': 'preview'
    }
    SD_CP_NAME_ROLE_MAP = {
        'belga_text': 'Belga text'
    }
    NEWSCOMPONENT2_ROLES: NewsComponent2Roles = NewsComponent2Roles('URL', 'Picture', 'Gallery', 'Audio',
                                                                    'Video', 'RelatedDocument', 'RelatedArticle')
    SD_MEDIA_TYPE_ROLE_MAP = {
        CONTENT_TYPE.PICTURE: NEWSCOMPONENT2_ROLES.PICTURE,
        CONTENT_TYPE.GRAPHIC: NEWSCOMPONENT2_ROLES.GALLERY,
        CONTENT_TYPE.VIDEO: NEWSCOMPONENT2_ROLES.VIDEO,
        CONTENT_TYPE.AUDIO: NEWSCOMPONENT2_ROLES.AUDIO,
    }

    def format(self, article, subscriber, codes=None):
        """
        Create output in Belga NewsML 1.2 format

        :param dict article:
        :param dict subscriber:
        :param list codes:
        :return [(int, str)]: return a List of tuples. A tuple consist of
            publish sequence number and formatted output string.
        :raises FormatterError: if the formatter fails to format an article
        """

        try:
            self.arhive_service = superdesk.get_resource_service('archive')
            self.content_types_service = superdesk.get_resource_service('content_types')
            self.roles_service = superdesk.get_resource_service('roles')
            self.users_service = superdesk.get_resource_service('users')
            self.vocabularies_service = superdesk.get_resource_service('vocabularies')
            self.attachments_service = superdesk.get_resource_service('attachments')
            self._belga_coverage_field_ids = [
                i['_id'] for i in self.vocabularies_service.find({'custom_field_type': 'belga.coverage'})
            ]

            # original/initial item
            items_chain = self.arhive_service.get_items_chain(article)
            self._original_item = items_chain[0]
            # the actual item which was selected for publishing in the UI.
            # just fetched doc from the db (the one in `items_chain`) is used instead of `article` to avoid
            # a possible difference in `versioncreated` datetime
            for item in items_chain:
                if item['guid'] == article['guid']:
                    self._current_item = item
                    break
            else:
                # in theory, it'll never happen
                logger.warning('Published item was not found in the items chain')
                self._current_item = article

            # items chain in context of Belga NewsML
            self._newsml_items_chain = self._get_newsml_items_chain(items_chain)
            # `NewsItemId` and `Duid` must always use guid of original item
            # SDBELGA-348
            self._duid = self._original_item[GUID_FIELD]

            self._tz = pytz.timezone(superdesk.app.config['DEFAULT_TIMEZONE'])
            self._string_now = self._get_formatted_datetime(self._current_item['firstpublished'])

            self._newsml = etree.Element('NewsML')
            self._format_catalog()
            self._format_newsenvelope()
            self._format_newsitem()

            xml_string = self.XML_ROOT + '\n' + etree.tostring(
                self._newsml, pretty_print=True,
                encoding=self.ENCODING
            ).decode(self.ENCODING)
            pub_seq_num = generate_sequence_number(subscriber)

            return [(pub_seq_num, xml_string)]
        except Exception as ex:
            raise FormatterError.newml12FormatterError(ex, subscriber)

    def can_format(self, format_type, item):
        """
        Test if the item can be formatted to Belga NewsML 1.2 or not.

        :param str format_type:
        :param dict item:
        :return: True if item can formatted else False
        """

        if format_type == 'belganewsml12':
            if item[ITEM_TYPE] in (
                    CONTENT_TYPE.TEXT,
                    CONTENT_TYPE.VIDEO,
                    CONTENT_TYPE.PICTURE,
                    CONTENT_TYPE.AUDIO,
                    CONTENT_TYPE.GRAPHIC,
            ):
                return True
        return False

    def _format_catalog(self):
        """Creates `<Catalog>` and adds it to `<NewsML>`."""

        SubElement(
            self._newsml, 'Catalog',
            {'Href': 'http://www.belga.be/dtd/BelgaCatalog.xml'}
        )

    def _format_newsenvelope(self):
        """Creates `<NewsEnvelope>` and adds it to `<NewsML>`."""

        newsenvelope = SubElement(self._newsml, 'NewsEnvelope')
        SubElement(newsenvelope, 'DateAndTime').text = self._string_now
        SubElement(newsenvelope, 'NewsService', {'FormalName': ''})
        SubElement(newsenvelope, 'NewsProduct', {'FormalName': ''})

    def _format_newsitem(self):
        """Creates `<NewsItem>` and all internal elements and adds it to `<NewsML>`."""

        newsitem = SubElement(self._newsml, 'NewsItem')
        self._format_identification(newsitem)
        self._format_newsmanagement(newsitem)
        self._format_newscomponent_1_level(newsitem)

    def _format_identification(self, newsitem):
        """
        Creates the `<Identification>` element and adds it to `<NewsItem>`.
        :param Element newsitem: NewsItem
        """

        identification = SubElement(newsitem, 'Identification')
        news_identifier = SubElement(identification, 'NewsIdentifier')
        SubElement(news_identifier, 'ProviderId').text = app.config['NEWSML_PROVIDER_ID']
        SubElement(news_identifier, 'DateId').text = self._get_formatted_datetime(
            self._current_item.get('firstcreated')
        )
        SubElement(news_identifier, 'NewsItemId').text = self._duid
        revision = self._process_revision(self._current_item)
        SubElement(news_identifier, 'RevisionId', attrib=revision).text = \
            str(self._current_item.get(config.VERSION, ''))
        SubElement(news_identifier, 'PublicIdentifier').text = self._generate_public_identifier(
            self._current_item[config.ID_FIELD],
            self._current_item.get(config.VERSION, ''),
            revision.get('Update', '')
        )

    def _format_newsmanagement(self, newsitem):
        """
        Creates the `<NewsManagement>` element and adds it to `<NewsItem>`.
        :param Element newsitem: NewsItem
        """

        news_management = SubElement(newsitem, 'NewsManagement')
        SubElement(news_management, 'NewsItemType', {'FormalName': 'NEWS'})
        SubElement(
            news_management, 'FirstCreated'
        ).text = self._get_formatted_datetime(self._current_item.get('firstcreated'))
        SubElement(
            news_management, 'ThisRevisionCreated'
        ).text = self._string_now

        if self._current_item.get(EMBARGO):
            SubElement(news_management, 'Status', {'FormalName': 'Embargoed'})
            status_will_change = SubElement(news_management, 'StatusWillChange')
            SubElement(
                status_will_change, 'FutureStatus',
                {'FormalName': self._current_item.get('pubstatus', '').upper()}
            )
            SubElement(
                status_will_change, 'DateAndTime'
            ).text = get_utc_schedule(self._current_item, EMBARGO).isoformat()
        else:
            SubElement(
                news_management, 'Status',
                {'FormalName': self._current_item.get('pubstatus', '').upper()}
            )

    def _format_newscomponent_1_level(self, newsitem):
        """
        Creates the `<NewsComponent>` element and adds it to `<NewsItem>`.
        :param Element newsitem: NewsItem
        """

        newscomponent_1_level = SubElement(
            newsitem, 'NewsComponent',
            {'Duid': self._duid, XML_LANG: self._current_item.get('language')}
        )
        newslines = SubElement(newscomponent_1_level, 'NewsLines')
        SubElement(newslines, 'HeadLine').text = self._current_item.get('headline', '')
        SubElement(newscomponent_1_level, 'AdministrativeMetadata')
        descriptivemetadata = SubElement(newscomponent_1_level, 'DescriptiveMetadata')
        genre_formalname = ''
        for subject in self._current_item.get('subject', []):
            if subject.get('scheme') == 'genre':
                genre_formalname = subject['qcode']
                break
        SubElement(
            descriptivemetadata, 'Genre',
            {'FormalName': genre_formalname}
        )

        self._format_newscomponent_2_level(newscomponent_1_level)

    def _format_newscomponent_2_level(self, newscomponent_1_level):
        """
        Creates the `<NewsComponent>`(s) of a 2nd level and appends them to `newscomponent_1_level`.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        """

        ROLE_FORMATTER_MAP = {
            self.NEWSCOMPONENT2_ROLES.PICTURE: self._format_picture,
            self.NEWSCOMPONENT2_ROLES.VIDEO: self._format_video,
            self.NEWSCOMPONENT2_ROLES.AUDIO: self._format_audio,
            self.NEWSCOMPONENT2_ROLES.GALLERY: self._format_coverage,
            self.NEWSCOMPONENT2_ROLES.RELATED_ARTICLE: self._format_related_text_item,
            self.NEWSCOMPONENT2_ROLES.RELATED_DOCUMENT: self._format_attachment,
            self.NEWSCOMPONENT2_ROLES.URL: self._format_url
        }

        for item in self._newsml_items_chain:
            _format = ROLE_FORMATTER_MAP.get(item['_role'], self._format_text)
            _format(newscomponent_1_level, item)

    def _format_text(self, newscomponent_1_level, item):
        """
        Creates a `<NewsComponent>` of a 2nd level with information related to content profile.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict item: item
        """

        newscomponent_2_level = SubElement(
            newscomponent_1_level, 'NewsComponent',
            {XML_LANG: item.get('language')}
        )
        if item.get(GUID_FIELD):
            newscomponent_2_level.attrib['Duid'] = item[GUID_FIELD]

        # Role
        SubElement(newscomponent_2_level, 'Role', {'FormalName': item['_role']})
        # NewsLines
        self._format_newslines(newscomponent_2_level, item=item)
        # AdministrativeMetadata
        self._format_administrative_metadata(newscomponent_2_level, item=item)
        # DescriptiveMetadata
        self._format_descriptive_metadata(newscomponent_2_level, item=item)
        # NewsComponent 3rd level
        self._format_newscomponent_3_level(newscomponent_2_level, item=item)

    def _format_related_text_item(self, newscomponent_1_level, item):
        """
        Creates a `<NewsComponent>` of a 2nd level with associated related text item.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict picture: picture item
        :param dict item: item
        """

        # NewsComponent
        newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
        if item.get(GUID_FIELD):
            newscomponent_2_level.attrib['Duid'] = item.get(GUID_FIELD)
        if item.get('language'):
            newscomponent_2_level.attrib[XML_LANG] = item.get('language')
        # Role
        SubElement(newscomponent_2_level, 'Role', {'FormalName': item['_role']})
        # NewsLines
        self._format_newslines(newscomponent_2_level, item=item)
        # AdministrativeMetadata
        self._format_administrative_metadata(newscomponent_2_level, item=item)
        # DescriptiveMetadata
        self._format_descriptive_metadata(newscomponent_2_level, item=item)
        # NewsComponent 3rd level
        self._format_newscomponent_3_level(newscomponent_2_level, item=item)

    def _format_url(self, newscomponent_1_level, item_url):
        """
        Creates a `NewsComponent`(s) of a 2nd level with belga url item.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict item_url: newsml url item
        """

        newscomponent_2_level = SubElement(
            newscomponent_1_level, 'NewsComponent',
            {XML_LANG: item_url.get('language')}
        )
        if item_url.get(GUID_FIELD):
            newscomponent_2_level.attrib['Duid'] = item_url[GUID_FIELD]

        SubElement(newscomponent_2_level, 'Role', {'FormalName': 'URL'})
        newslines = SubElement(newscomponent_2_level, 'NewsLines')
        SubElement(newslines, 'DateLine')
        SubElement(newslines, 'HeadLine').text = item_url.get('description')
        SubElement(newslines, 'CopyrightLine').text = item_url.get('copyrightholder')
        SubElement(newslines, 'CreditLine').text = self.DEFAULT_CREDITLINE
        self._format_administrative_metadata(newscomponent_2_level, item=item_url)
        self._format_descriptive_metadata(newscomponent_2_level, item=item_url)

        for role, key in (('Title', 'description'), ('Locator', 'url')):
            newscomponent_3_level = SubElement(
                newscomponent_2_level, 'NewsComponent',
                {XML_LANG: item_url.get('language')}
            )
            SubElement(newscomponent_3_level, 'Role', {'FormalName': role})
            SubElement(
                SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
                'Property',
                {'FormalName': 'ComponentClass', 'Value': 'Text'}
            )
            contentitem = SubElement(newscomponent_3_level, 'ContentItem')
            SubElement(contentitem, 'Format', {'FormalName': 'Text'})
            SubElement(contentitem, 'DataContent').text = item_url.get(key)
            characteristics = SubElement(contentitem, 'Characteristics')
            # string's length is used in original belga's newsml
            SubElement(
                characteristics, 'SizeInBytes'
            ).text = str(len(item_url[key])) if item_url.get(key) else '0'
            SubElement(characteristics, 'Property', {'FormalName': 'maxCharCount', 'Value': '0'})

    def _format_picture(self, newscomponent_1_level, picture):
        """
        Creates a `<NewsComponent>` of a 2nd level with associated picture data.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict picture: picture item
        """

        self._set_belga_urn(picture)

        # NewsComponent
        newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
        if picture.get(GUID_FIELD):
            newscomponent_2_level.attrib['Duid'] = picture.get(GUID_FIELD)
        if picture.get('language'):
            newscomponent_2_level.attrib[XML_LANG] = picture.get('language')
        # Role
        SubElement(newscomponent_2_level, 'Role', {'FormalName': picture['_role']})
        # NewsLines
        self._format_newslines(newscomponent_2_level, item=picture)
        # AdministrativeMetadata
        self._format_administrative_metadata(newscomponent_2_level, item=picture)
        self._format_descriptive_metadata(newscomponent_2_level, item=picture)

        for role, key in (('Title', 'headline'), ('Caption', 'description_text')):
            newscomponent_3_level = SubElement(newscomponent_2_level, 'NewsComponent')
            if picture.get('language'):
                newscomponent_3_level.attrib[XML_LANG] = picture.get('language')
            SubElement(newscomponent_3_level, 'Role', {'FormalName': role})
            SubElement(
                SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
                'Property',
                {'FormalName': 'ComponentClass', 'Value': 'Text'}
            )
            contentitem = SubElement(newscomponent_3_level, 'ContentItem')
            SubElement(contentitem, 'Format', {'FormalName': 'Text'})

            if key == 'description_text' \
                    and picture.get('extra', {}).get('people') \
                    and picture.get('extra', {}).get('event_description'):
                # format caption using `people` and `event_description` fields
                data_content = '{} on the picture regarding {}'.format(
                    picture['extra']['people'], picture['extra']['event_description']
                )
            elif key == 'description_text' and picture.get('extra', {}).get('people'):
                # format caption using `people` field
                data_content = 'Picture showing {}'.format(picture['extra']['people'])
            elif key == 'description_text' and picture.get('extra', {}).get('event_description'):
                # format caption using `event_description` field
                data_content = 'Picture showing {}'.format(picture['extra']['event_description'])
            else:
                data_content = picture.get(key)

            SubElement(contentitem, 'DataContent').text = data_content
            characteristics = SubElement(contentitem, 'Characteristics')
            # string's length is used in original belga's newsml
            SubElement(characteristics, 'SizeInBytes').text = str(len(data_content)) if data_content else '0'
            SubElement(characteristics, 'Property', {'FormalName': 'maxCharCount', 'Value': '0'})

        # original, thumbnail, preview
        for role, key in (('Image', 'original'), ('Thumbnail', 'thumbnail'), ('Preview', 'viewImage')):
            if key not in picture['renditions']:
                continue
            newscomponent_3_level = SubElement(newscomponent_2_level, 'NewsComponent')
            if picture.get('language'):
                newscomponent_3_level.attrib[XML_LANG] = picture.get('language')

            SubElement(newscomponent_3_level, 'Role', {'FormalName': role})
            SubElement(
                SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
                'Property',
                {'FormalName': 'ComponentClass', 'Value': 'Image'}
            )

            self._format_media_contentitem(newscomponent_3_level, rendition=picture['renditions'][key])

    def _format_coverage(self, newscomponent_1_level, coverage):
        """
        Creates a `<NewsComponent>` of a 2nd level with associated graphic item's data
        or with data from `belga.coverage` field.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict coverage: coverage data
        """

        self._set_belga_urn(coverage)

        newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
        if coverage.get(GUID_FIELD):
            newscomponent_2_level.attrib['Duid'] = coverage.get(GUID_FIELD)
        if coverage.get('language'):
            newscomponent_2_level.attrib[XML_LANG] = coverage.get('language')
        SubElement(newscomponent_2_level, 'Role', {'FormalName': coverage['_role']})
        self._format_newslines(newscomponent_2_level, item=coverage)
        self._format_administrative_metadata(newscomponent_2_level, item=coverage)
        self._format_descriptive_metadata(newscomponent_2_level, item=coverage)

        for role, key in (('Title', 'headline'), ('Caption', 'description_text')):
            newscomponent_3_level = SubElement(newscomponent_2_level, 'NewsComponent')
            if coverage.get('language'):
                newscomponent_3_level.attrib[XML_LANG] = coverage.get('language')
            SubElement(newscomponent_3_level, 'Role', {'FormalName': role})
            SubElement(
                SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
                'Property',
                {'FormalName': 'ComponentClass', 'Value': 'Text'}
            )
            contentitem = SubElement(newscomponent_3_level, 'ContentItem')
            SubElement(contentitem, 'Format', {'FormalName': 'Text'})
            SubElement(contentitem, 'DataContent').text = coverage.get(key)
            characteristics = SubElement(contentitem, 'Characteristics')
            # string's length is used in original belga's newsml
            SubElement(characteristics, 'SizeInBytes').text = str(len(coverage[key])) if coverage.get(key) else '0'
            SubElement(characteristics, 'Property', {'FormalName': 'maxCharCount', 'Value': '0'})

        newscomponent_3_level = SubElement(newscomponent_2_level, 'NewsComponent')
        if coverage.get(GUID_FIELD):
            newscomponent_3_level.attrib['Duid'] = coverage.get(GUID_FIELD)
        if coverage.get('language'):
            newscomponent_3_level.attrib[XML_LANG] = coverage.get('language')

        SubElement(newscomponent_3_level, 'Role', {'FormalName': 'Component'})
        SubElement(
            SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
            'Property',
            {'FormalName': 'ComponentClass', 'Value': 'Image'}
        )
        self._format_media_contentitem(newscomponent_3_level, rendition=coverage['renditions']['original'])

    def _format_audio(self, newscomponent_1_level, audio):
        """
        Creates a `<NewsComponent>` of a 2nd level with associated audio data.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict audio: audio item
        """

        self._set_belga_urn(audio)

        newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
        if audio.get(GUID_FIELD):
            newscomponent_2_level.attrib['Duid'] = audio.get(GUID_FIELD)
        if audio.get('language'):
            newscomponent_2_level.attrib[XML_LANG] = audio.get('language')
        SubElement(newscomponent_2_level, 'Role', {'FormalName': audio['_role']})
        self._format_newslines(newscomponent_2_level, item=audio)
        self._format_administrative_metadata(newscomponent_2_level, item=audio)
        self._format_descriptive_metadata(newscomponent_2_level, item=audio)

        for role, key in (('Title', 'headline'), ('Body', 'description_text')):
            newscomponent_3_level = SubElement(newscomponent_2_level, 'NewsComponent')
            if audio.get('language'):
                newscomponent_3_level.attrib[XML_LANG] = audio.get('language')
            SubElement(newscomponent_3_level, 'Role', {'FormalName': role})
            SubElement(
                SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
                'Property',
                {'FormalName': 'ComponentClass', 'Value': 'Text'}
            )
            contentitem = SubElement(newscomponent_3_level, 'ContentItem')
            SubElement(contentitem, 'Format', {'FormalName': 'Text'})
            SubElement(contentitem, 'DataContent').text = audio.get(key)
            characteristics = SubElement(contentitem, 'Characteristics')
            # string's length is used in original belga's newsml
            SubElement(characteristics, 'SizeInBytes').text = str(len(audio[key])) if audio.get(key) else '0'
            SubElement(characteristics, 'Property', {'FormalName': 'maxCharCount', 'Value': '0'})

        # sound
        newscomponent_3_level = SubElement(newscomponent_2_level, 'NewsComponent')
        if audio.get(GUID_FIELD):
            newscomponent_3_level.attrib['Duid'] = audio.get(GUID_FIELD)
        if audio.get('language'):
            newscomponent_3_level.attrib[XML_LANG] = audio.get('language')

        SubElement(newscomponent_3_level, 'Role', {'FormalName': 'Sound'})
        SubElement(
            SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
            'Property',
            {'FormalName': 'ComponentClass', 'Value': 'Audio'}
        )
        self._format_media_contentitem(newscomponent_3_level, rendition=audio['renditions']['original'])

    def _format_video(self, newscomponent_1_level, video):
        """
        Creates a `<NewsComponent>` of a 2nd level with associated video data.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict audio: video item
        """

        self._set_belga_urn(video)

        newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
        if video.get(GUID_FIELD):
            newscomponent_2_level.attrib['Duid'] = video.get(GUID_FIELD)
        if video.get('language'):
            newscomponent_2_level.attrib[XML_LANG] = video.get('language')
        SubElement(newscomponent_2_level, 'Role', {'FormalName': video['_role']})
        self._format_newslines(newscomponent_2_level, item=video)
        self._format_administrative_metadata(newscomponent_2_level, item=video)
        self._format_descriptive_metadata(newscomponent_2_level, item=video)

        for role, key in (('Title', 'headline'), ('Body', 'description_text')):
            newscomponent_3_level = SubElement(newscomponent_2_level, 'NewsComponent')
            if video.get('language'):
                newscomponent_3_level.attrib[XML_LANG] = video.get('language')
            SubElement(newscomponent_3_level, 'Role', {'FormalName': role})
            SubElement(
                SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
                'Property',
                {'FormalName': 'ComponentClass', 'Value': 'Text'}
            )
            contentitem = SubElement(newscomponent_3_level, 'ContentItem')
            SubElement(contentitem, 'Format', {'FormalName': 'Text'})

            if key == 'description_text' \
                    and video.get('extra', {}).get('people') \
                    and video.get('extra', {}).get('event_description'):
                # format caption using `people` and `event_description` fields
                data_content = '{} on the video regarding {}'.format(
                    video['extra']['people'], video['extra']['event_description']
                )
            elif key == 'description_text' and video.get('extra', {}).get('people'):
                # format caption using `people` field
                data_content = 'Video showing {}'.format(video['extra']['people'])
            elif key == 'description_text' and video.get('extra', {}).get('event_description'):
                # format caption using `event_description` field
                data_content = 'Video showing {}'.format(video['extra']['event_description'])
            else:
                data_content = video.get(key)

            SubElement(contentitem, 'DataContent').text = data_content
            characteristics = SubElement(contentitem, 'Characteristics')
            # string's length is used in original belga's newsml
            SubElement(characteristics, 'SizeInBytes').text = str(len(data_content)) if data_content else '0'
            SubElement(characteristics, 'Property', {'FormalName': 'maxCharCount', 'Value': '0'})

        # clip
        newscomponent_3_level = SubElement(newscomponent_2_level, 'NewsComponent')
        if video.get(GUID_FIELD):
            newscomponent_3_level.attrib['Duid'] = video.get(GUID_FIELD)
        if video.get('language'):
            newscomponent_3_level.attrib[XML_LANG] = video.get('language')

        SubElement(newscomponent_3_level, 'Role', {'FormalName': 'Clip'})
        SubElement(
            SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
            'Property',
            {'FormalName': 'ComponentClass', 'Value': 'Video'}
        )
        self._format_media_contentitem(newscomponent_3_level, rendition=video['renditions']['original'])

        # video image thumbnail
        for role, key in (('Image', 'viewImage'), ('Thumbnail', 'thumbnail')):
            if key not in video['renditions']:
                continue
            newscomponent_3_level = SubElement(newscomponent_2_level, 'NewsComponent')
            if video.get(GUID_FIELD):
                newscomponent_3_level.attrib['Duid'] = video.get(GUID_FIELD)
            if video.get('language'):
                newscomponent_3_level.attrib[XML_LANG] = video.get('language')

            SubElement(newscomponent_3_level, 'Role', {'FormalName': role})
            SubElement(
                SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
                'Property',
                {'FormalName': 'ComponentClass', 'Value': 'Image'}
            )

            self._format_media_contentitem(newscomponent_3_level, rendition=video['renditions'][key])

    def _format_attachment(self, newscomponent_1_level, attachment):
        """
        Creates a `<NewsComponent>` of a 2nd level with file attached to the item.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict attachment: attachment
        """

        attachment['_id'] = str(attachment['_id'])
        attachment[GUID_FIELD] = attachment['_id']
        attachment['headline'] = attachment.pop('title')
        attachment['description_text'] = attachment.pop('description', '')
        attachment['firstcreated'] = attachment['_created']

        newscomponent_2_level = SubElement(
            newscomponent_1_level, 'NewsComponent',
            {
                XML_LANG: attachment.get('language'),
                'Duid': str(attachment.get('_id'))
            }
        )

        SubElement(newscomponent_2_level, 'Role', {'FormalName': attachment['_role']})
        self._format_newslines(newscomponent_2_level, item=attachment)
        self._format_administrative_metadata(newscomponent_2_level, item=attachment)
        self._format_descriptive_metadata(newscomponent_2_level, item=attachment)

        for role, key in (('Title', 'headline'), ('Body', 'description_text')):
            newscomponent_3_level = SubElement(newscomponent_2_level, 'NewsComponent')
            SubElement(newscomponent_3_level, 'Role', {'FormalName': role})
            SubElement(
                SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
                'Property',
                {'FormalName': 'ComponentClass', 'Value': 'Text'}
            )
            contentitem = SubElement(newscomponent_3_level, 'ContentItem')
            SubElement(contentitem, 'Format', {'FormalName': 'Text'})
            SubElement(contentitem, 'DataContent').text = attachment.get(key)
            characteristics = SubElement(contentitem, 'Characteristics')
            # string's length is used in original belga's newsml
            SubElement(characteristics, 'SizeInBytes').text = str(len(attachment[key])) if attachment.get(key) else '0'
            SubElement(characteristics, 'Property', {'FormalName': 'maxCharCount', 'Value': '0'})

        # Component
        newscomponent_3_level = SubElement(newscomponent_2_level, 'NewsComponent')
        newscomponent_3_level.attrib['Duid'] = attachment.get(GUID_FIELD)

        SubElement(newscomponent_3_level, 'Role', {'FormalName': 'Component'})
        SubElement(
            SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
            'Property',
            {'FormalName': 'ComponentClass', 'Value': 'Binary'}
        )

        self._format_media_contentitem(
            newscomponent_3_level,
            rendition={
                'filename': attachment['filename'],
                'media': attachment['media'],
                'mimetype': attachment['mimetype'],
                'href': urljoin(app.config['MEDIA_PREFIX'] + '/', '{}'.format(attachment['media'])),
                'belga-urn': 'urn:www.belga.be:superdesk:{}:{}'.format(
                    app.config['OUTPUT_BELGA_URN_SUFFIX'],
                    attachment['media']
                )
            }
        )

    def _set_belga_urn(self, media_item):
        """
        Set internal Belga URN media reference to all `media_item` renditions.
        All media items, uploaded and external should use belga's internal URN as media reference.
        SDBELGA-345, SDBELGA-352
        :param media_item: media item
        :type media_item: dict
        """

        for key, rendition in media_item.get('renditions', {}).items():
            # rendition is from Belga image search provider
            if BelgaImageSearchProvider.GUID_PREFIX in media_item.get(GUID_FIELD, ''):
                if key in self.SD_BELGA_IMAGE_RENDITIONS_MAP:
                    belga_id = media_item[GUID_FIELD].split(BelgaImageSearchProvider.GUID_PREFIX, 1)[-1]
                    rendition['belga-urn'] = 'urn:www.belga.be:picturestore:{}:{}:true'.format(
                        belga_id,
                        self.SD_BELGA_IMAGE_RENDITIONS_MAP[key]
                    )
                    rendition['filename'] = '{}.jpeg'.format(belga_id)
            # rendition is from Belga coverage search provider
            elif BelgaCoverageSearchProvider.GUID_PREFIX in media_item.get(GUID_FIELD, ''):
                belga_id = media_item[GUID_FIELD].split(BelgaCoverageSearchProvider.GUID_PREFIX, 1)[-1]
                rendition['belga-urn'] = 'urn:www.belga.be:belgagallery:{}'.format(belga_id)
            # the rest are internaly uploaded media: pictures, video and audio
            elif 'media' in rendition:
                rendition['belga-urn'] = 'urn:www.belga.be:superdesk:{}:{}'.format(
                    app.config['OUTPUT_BELGA_URN_SUFFIX'],
                    rendition['media']
                )

    def _format_media_contentitem(self, newscomponent_3_level, rendition):
        """
        Creates a ContentItem for provided rendition.
        :param Element newscomponent_3_level: NewsComponent of 3st level
        :param dict rendition: rendition info
        """

        FORMAT_MAP = {
            'Mp4': 'Mpeg4',
            'Jpg': 'Jpeg',
        }

        contentitem = SubElement(
            newscomponent_3_level, 'ContentItem',
            {'Href': r'{}'.format(rendition.get('belga-urn', rendition['href']))}
        )

        filename = rendition['filename'] if rendition.get('filename') else rendition['href'].rsplit('/', 1)[-1]

        format_name = filename.rsplit('.', 1)[-1].capitalize()
        format_name = FORMAT_MAP.get(format_name, format_name)
        if 'belgagallery' in rendition.get('belga-urn'):
            format_name = FORMAT_MAP['Jpg']

        SubElement(contentitem, 'Format', {'FormalName': format_name})
        if rendition.get('mimetype'):
            SubElement(contentitem, 'MimeType', {'FormalName': rendition['mimetype']})
        characteristics = SubElement(contentitem, 'Characteristics')

        if rendition.get('media'):
            media = app.media.get(str(rendition['media']))
            length = media.length if media.length else media.metadata.get('length')
            SubElement(characteristics, 'SizeInBytes').text = str(length)
        if rendition.get('width'):
            SubElement(
                characteristics, 'Property',
                {'FormalName': 'Width', 'Value': str(rendition['width'])}
            )
        if rendition.get('height'):
            SubElement(
                characteristics, 'Property',
                {'FormalName': 'Height', 'Value': str(rendition['height'])}
            )

    def _format_newslines(self, newscomponent_2_level, item):
        """
        Creates the `<NewsLines>` element for text item and add it to `newscomponent_2_level`
        :param Element newscomponent_2_level: NewsComponent of 2nd level
        :param dict item: item
        """
        newslines = SubElement(newscomponent_2_level, 'NewsLines')
        SubElement(newslines, 'DateLine')
        SubElement(newslines, 'HeadLine').text = item.get('headline')
        SubElement(newslines, 'CopyrightLine').text = item.get('copyrightholder')
        SubElement(newslines, 'CreditLine').text = self.DEFAULT_CREDITLINE

        # KeywordLine from country
        for subject in item.get('subject', []):
            if subject.get('scheme') == 'country':
                try:
                    SubElement(
                        newslines, 'KeywordLine'
                    ).text = subject['translations']['name'][item.get('language')]
                except KeyError:
                    logger.warning(
                        'There is no "{}" translation for country cv. Subject: {}'.format(
                            item.get('language'), subject
                        )
                    )
                    SubElement(newslines, 'KeywordLine').text = subject['name']

        # KeywordLine from belga-keywords
        for subject in item.get('subject', []):
            if subject.get('scheme') == 'belga-keywords':
                try:
                    SubElement(
                        newslines, 'KeywordLine'
                    ).text = subject['translations']['name'][item.get('language')]
                except KeyError:
                    logger.warning(
                        'There is no "{}" translation for belga-keywords cv. Subject: {}'.format(
                            item.get('language'), subject
                        )
                    )
                    SubElement(newslines, 'KeywordLine').text = subject['name']

        # KeywordLine from belga-keywords custom field
        # just in case if old custom belga-keywords field is used or item has data from it
        if item.get('extra', {}).get('belga-keywords'):
            for keyword in [i.strip() for i in item['extra']['belga-keywords'].split(',')]:
                SubElement(newslines, 'KeywordLine').text = keyword

        # KeywordLine from keywords
        for keyword in item.get('keywords', []):
            SubElement(newslines, 'KeywordLine').text = keyword

        newsline = SubElement(newslines, 'NewsLine')
        SubElement(newsline, 'NewsLineType', {'FormalName': item.get('line_type', '')})
        SubElement(newsline, 'NewsLineText').text = item.get('line_text')

    def _format_administrative_metadata(self, newscomponent_2_level, item):
        """
        Creates the `<AdministrativeMetadata>` element and add it to `newscomponent_2_level`
        :param Element newscomponent_2_level: NewsComponent of 2nd level
        :param dict item: item
        """

        administrative_metadata = SubElement(newscomponent_2_level, 'AdministrativeMetadata')
        SubElement(
            SubElement(administrative_metadata, 'Provider'),
            'Party',
            {'FormalName': item.get('line_type', '')}
        )
        creator = SubElement(administrative_metadata, 'Creator')

        if item.get('type') == CONTENT_TYPE.PICTURE:
            authors = (item['original_creator'],) if item.get('original_creator') else tuple()
        else:
            authors = item.get('authors', tuple())
        for author in authors:
            author = self._get_author_info(author)
            SubElement(
                creator, 'Party',
                {'FormalName': author['initials'], 'Topic': author['role']}
            )
        if item.get('administrative', {}).get('contributor'):
            SubElement(
                SubElement(administrative_metadata, 'Contributor'), 'Party',
                {'FormalName': item['administrative']['contributor']}
            )
        # initials of user who published an item is `Validator`
        if item.get('version_creator'):
            SubElement(
                administrative_metadata, 'Property',
                {
                    'FormalName': 'Validator',
                    'Value': self._get_author_info(str(item['version_creator']))['initials']
                }
            )
        elif item.get('administrative', {}).get('validator'):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'Validator', 'Value': item['administrative']['validator']}
            )
        SubElement(
            administrative_metadata, 'Property',
            {'FormalName': 'ValidationDate', 'Value': self._get_formatted_datetime(item['firstpublished'])}
        )
        if item.get('administrative', {}).get('foreign_id'):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'ForeignId', 'Value': item['administrative']['foreign_id']}
            )
        if item.get('urgency'):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'Priority', 'Value': str(item['urgency'])}
            )
        if item.get('slugline'):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'Topic', 'Value': item['slugline']}
            )
        if item.get(GUID_FIELD):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'NewsObjectId', 'Value': item[GUID_FIELD]}
            )
        if item.get('ednote'):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'EditorialInfo', 'Value': item['ednote']}
            )

        for subject in item.get('subject', []):
            if subject.get('scheme') == 'services-products':
                try:
                    news_service_value, news_product_value = subject.get('qcode').split('/')
                except ValueError:
                    # ignore
                    continue
                property_newspackage = SubElement(
                    administrative_metadata, 'Property',
                    {'FormalName': 'NewsPackage'}
                )
                SubElement(
                    property_newspackage, 'Property',
                    {'FormalName': 'NewsService', 'Value': news_service_value}
                )
                SubElement(
                    property_newspackage, 'Property',
                    {'FormalName': 'NewsProduct', 'Value': news_product_value}
                )
            if subject.get('scheme') == 'label':
                SubElement(
                    administrative_metadata, 'Property',
                    {'FormalName': 'Label', 'Value': str(subject['qcode'])}
                )
            if subject.get('scheme') == 'distribution':
                SubElement(
                    administrative_metadata, 'Property',
                    {'FormalName': 'Distribution', 'Value': get_distribution_value(subject['qcode'])}
                )

        sources = [subj['qcode'] for subj in item.get('subject', []) if subj.get('scheme') == 'sources']
        sources += [subj['qcode'] for subj in item.get('subject', []) if subj.get('scheme') == 'media-source']
        sources += [item['creditline']] if item.get('creditline') else []
        if sources:
            source_element = SubElement(administrative_metadata, 'Source')
            SubElement(
                source_element,
                'Party',
                {'FormalName': '/'.join([source for source in sources])},
            )

    def _format_descriptive_metadata(self, newscomponent_2_level, item):
        """
        Creates the `<DescriptiveMetadata>` element and add it to `newscomponent_2_level`
        :param Element newscomponent_2_level: NewsComponent of 2nd level
        :param dict item: item
        """

        descriptive_metadata = SubElement(newscomponent_2_level, 'DescriptiveMetadata')
        if item.get('firstcreated'):
            descriptive_metadata.attrib['DateAndTime'] = self._get_formatted_datetime(item['firstcreated'])

        SubElement(descriptive_metadata, 'SubjectCode')
        location = SubElement(descriptive_metadata, 'Location')

        city_property = SubElement(location, 'Property', {'FormalName': 'City'})
        if item.get('extra', {}).get('city'):
            city_property.set('Value', item['extra']['city'])

        countries = [subj for subj in item.get('subject', []) if subj.get('scheme') == 'countries']
        for country in countries:
            country_property = SubElement(location, 'Property', {'FormalName': 'Country'})
            try:
                country_property.set('Value', country['translations']['name'][item.get('language')])
            except KeyError:
                logger.warning(
                    'There is no "{}" translation for countries cv. Country: {}'.format(item.get('language'), country)
                )
            # for now we output only one country
            break

        SubElement(location, 'Property', {'FormalName': 'CountryArea'})
        SubElement(location, 'Property', {'FormalName': 'WorldRegion'})

    def _format_newscomponent_3_level(self, newscomponent_2_level, item):
        """
        Creates the `<NewsComponent>`(s) of a 3rd level element for text item and adds it to `newscomponent_2_level`
        :param Element newscomponent_2_level: NewsComponent of 2nd level
        """

        # output first paragraph of the body as a lead
        item['lead'] = ''
        if item.get('body_html'):
            tree = parse_html(item['body_html'])
            for el in tree:
                if el.tag == 'p':
                    item['lead'] = to_string(el)
                    tree.remove(el)
                    item['body_html'] = to_string(tree, pretty_print=True)
                break

        # Title, Lead, Body
        for formalname, item_key in (('Body', 'body_html'), ('Title', 'headline'), ('Lead', 'lead')):
            if item.get(item_key):
                newscomponent_3_level = SubElement(
                    newscomponent_2_level, 'NewsComponent',
                    {XML_LANG: item.get('language')}
                )
                # Role
                SubElement(newscomponent_3_level, 'Role', {'FormalName': formalname})
                # DescriptiveMetadata > Property
                SubElement(
                    SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
                    'Property', {'FormalName': 'ComponentClass', 'Value': 'Text'}
                )
                # ContentItem
                contentitem = SubElement(newscomponent_3_level, 'ContentItem')
                SubElement(contentitem, 'Format', {'FormalName': 'Text'})

                # cut off all tags except paragraph and headings
                cleaner = Cleaner(
                    allow_tags=('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'),
                    remove_unknown_tags=False
                )
                html_str = cleaner.clean_html(item.get(item_key))
                text = text_utils.get_text(html_str, content='html', space_on_elements=True, space='   ')
                text = text.strip()

                SubElement(contentitem, 'DataContent').text = text
                characteristics = SubElement(contentitem, 'Characteristics')
                # string's length is used in original belga's newsml
                SubElement(characteristics, 'SizeInBytes').text = str(len(text))
                SubElement(characteristics, 'Property', {'FormalName': 'maxCharCount', 'Value': '0'})

    def _get_author_info(self, author):
        author_info = {'initials': '', 'role': ''}
        author_type = type(author)

        # most probably that author info was ingested
        if author_type is dict and '_id' not in author:
            author_info['initials'] = author.get('name', author.get('uri', ''))
            author_info['role'] = author.get('role', '')
        # manually added author
        elif author_type is dict:
            author_info['role'] = author['_id'][1]
            try:
                user = next(self.users_service.find({'_id': author['_id'][0]}))
            except StopIteration:
                logger.warning("unknown user: {user_id}".format(user_id=author['_id'][0]))
            else:
                author_info['initials'] = user.get('username')
        # in case of version_creator
        elif author_type is str:
            author_id = author
            try:
                user = next(self.users_service.find({'_id': author_id}))
            except StopIteration:
                logger.warning("unknown user: {user_id}".format(user_id=author_id))
            else:
                if user.get('role'):
                    try:
                        role = next(self.roles_service.find({'_id': user['role']}))
                    except StopIteration:
                        logger.warning("unknown role: {role_id}".format(role_id=user['role']))
                    else:
                        author_info['role'] = role.get('author_role', '')
                author_info['initials'] = user.get('username')
        else:
            logger.warning("Unsupported author format: {author}".format(author=author))

        return author_info

    def _get_formatted_datetime(self, _datetime):
        if type(_datetime) is str:
            _datetime = dateutil_parser.parse(_datetime)

        return _datetime.astimezone(self._tz).strftime(self.DATETIME_FORMAT)

    def _get_content_profile_name(self, item):
        if item.get('profile') in self.SD_CP_NAME_ROLE_MAP:
            return self.SD_CP_NAME_ROLE_MAP[item.get('profile')]

        req = ParsedRequest()
        req.args = {}
        req.projection = '{"label": 1}'
        content_type = self.content_types_service.find_one(
            req=req,
            _id=item.get('profile')
        )
        return content_type['label'].capitalize()

    def _get_newsml_items_chain(self, items_chain):
        """
        Get the whole items chain in context of Belga NewsML.
        Entities which are treated as a standalone items (NewsComponent 2nd level) in Belga NewsML:
        - sd item
        - every association of sd item:
            - related internal/external image
            - related internal/external video
            - related internal/external audio
            - related internal/external coverage
            - related internal/external text items
        - every item.extra.belga-url
        - every attachment

        :param items_chain: chain of items
        :type items_chain: list
        :return: tuple where every item represents a 2nd level NewsComponent in Belga NewsML
        :rtype: tuple
        """

        KEYS_TO_INHERIT = (
            GUID_FIELD,
            'language',
            'copyrightholder',
            'line_type',
            'administrative',
            'version_creator',
            'firstpublished',
            'firstcreated',
            'versioncreated',
            'slugline',
            'creditline',
            'extra',
            'authors',
            'original_creator',
        )
        # sd items chain including updates and translations
        sd_items_chain = deepcopy(tuple(
            i for i in items_chain
            if i.get(ITEM_STATE) in (CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED)
        ))

        # newsml items chain
        newsml_items_chain = []

        for sd_item in sd_items_chain:
            # get newscomponent role
            try:
                sd_item['_role'] = self.SD_MEDIA_TYPE_ROLE_MAP[sd_item[ITEM_TYPE]]
            except KeyError:
                # for text items `Role` is defined by content profile name
                sd_item['_role'] = self._get_content_profile_name(sd_item)
            newsml_items_chain.append(sd_item)

            sd_item_associations = sd_item.get('associations', {})
            sd_item_extra = sd_item.get('extra', {})

            # belga urls
            for belga_url in sd_item_extra.get('belga-url', []):
                newsml_item = {k: v for k, v in sd_item.items() if k in KEYS_TO_INHERIT}
                newsml_item.update(belga_url)
                newsml_item['_role'] = self.NEWSCOMPONENT2_ROLES.URL
                newsml_items_chain.append(newsml_item)
            # media items
            # get all associated media items where `renditions` are already IN the items.
            media_items = [
                sd_item_associations[i] for i in sd_item_associations
                if sd_item_associations[i]
                and sd_item_associations[i].get(ITEM_TYPE) in (CONTENT_TYPE.PICTURE, CONTENT_TYPE.GRAPHIC,
                                                               CONTENT_TYPE.AUDIO, CONTENT_TYPE.VIDEO)
                and 'renditions' in sd_item_associations[i]
            ]
            # get all associated media items `_id`s where `renditions` are NOT IN the item
            media_items_ids = [
                sd_item_associations[i]['_id'] for i in sd_item_associations
                if sd_item_associations[i]
                and sd_item_associations[i].get(ITEM_TYPE) in (CONTENT_TYPE.PICTURE, CONTENT_TYPE.GRAPHIC,
                                                               CONTENT_TYPE.AUDIO, CONTENT_TYPE.VIDEO)
                and 'renditions' not in sd_item_associations[i]
            ]
            # fetch associated docs by _id
            if media_items_ids:
                media_items += list(self.arhive_service.find({
                    '_id': {'$in': media_items_ids}}
                ))
            # pictures
            used_ids = []
            for picture in [i for i in media_items if i[ITEM_TYPE] == CONTENT_TYPE.PICTURE]:
                if picture['_id'] in used_ids:
                    continue
                used_ids.append(picture['_id'])
                newsml_item = {k: v for k, v in sd_item.items() if k in KEYS_TO_INHERIT}
                newsml_item.update(picture)
                newsml_item['language'] = sd_item.get('language', newsml_item.get('language'))
                newsml_item['_role'] = self.NEWSCOMPONENT2_ROLES.PICTURE
                newsml_items_chain.append(newsml_item)
            # graphics
            used_ids = []
            for graphic in [i for i in media_items if i[ITEM_TYPE] == CONTENT_TYPE.GRAPHIC]:
                if graphic['_id'] in used_ids:
                    continue
                used_ids.append(graphic['_id'])
                newsml_item = {k: v for k, v in sd_item.items() if k in KEYS_TO_INHERIT}
                newsml_item.update(graphic)
                newsml_item['language'] = sd_item.get('language', newsml_item.get('language'))
                newsml_item['_role'] = self.NEWSCOMPONENT2_ROLES.GALLERY
                newsml_items_chain.append(newsml_item)
            # audios
            used_ids = []
            for audio in [i for i in media_items if i[ITEM_TYPE] == CONTENT_TYPE.AUDIO]:
                if audio['_id'] in used_ids:
                    continue
                used_ids.append(audio['_id'])
                newsml_item = {k: v for k, v in sd_item.items() if k in KEYS_TO_INHERIT}
                newsml_item.update(audio)
                newsml_item['language'] = sd_item.get('language', newsml_item.get('language'))
                newsml_item['_role'] = self.NEWSCOMPONENT2_ROLES.AUDIO
                newsml_items_chain.append(newsml_item)
            # videos
            used_ids = []
            for video in [i for i in media_items if i[ITEM_TYPE] == CONTENT_TYPE.VIDEO]:
                if video['_id'] in used_ids:
                    continue
                used_ids.append(video['_id'])
                newsml_item = {k: v for k, v in sd_item.items() if k in KEYS_TO_INHERIT}
                newsml_item.update(video)
                newsml_item['language'] = sd_item.get('language', newsml_item.get('language'))
                newsml_item['_role'] = self.NEWSCOMPONENT2_ROLES.VIDEO
                newsml_items_chain.append(newsml_item)
            # belga.coverage custom fields
            for field_id in self._belga_coverage_field_ids:
                if field_id in sd_item_extra:
                    belga_item_id = sd_item_extra[field_id]
                    belga_cov_search_provider = BelgaCoverageSearchProvider({})
                    try:
                        data = belga_cov_search_provider.api_get('/getGalleryById',
                                                                 {'i': belga_item_id.rsplit(':', 1)[-1]})
                    except Exception as e:
                        logger.warning("Failed to fetch belga coverage: {}".format(e))
                    else:
                        newsml_item = {k: v for k, v in sd_item.items() if k in KEYS_TO_INHERIT}
                        newsml_item.update(
                            belga_cov_search_provider.format_list_item(data)
                        )
                        newsml_item['_role'] = self.NEWSCOMPONENT2_ROLES.GALLERY
                        newsml_items_chain.append(newsml_item)
            # attachments
            attachments_ids = [i['attachment'] for i in sd_item.get('attachments', [])]
            attachments = list(self.attachments_service.find({'_id': {'$in': attachments_ids}}))
            for attachment in attachments:
                newsml_item = {k: v for k, v in sd_item.items() if k in KEYS_TO_INHERIT}
                newsml_item.update(attachment)
                newsml_item['_role'] = self.NEWSCOMPONENT2_ROLES.RELATED_DOCUMENT
                newsml_items_chain.append(newsml_item)
            # related text items
            # get all associated `text` items where `_type` is `externalsource`.
            rel_text_items = [
                sd_item_associations[i] for i in sd_item_associations
                if (sd_item_associations[i] and sd_item_associations[i].get(ITEM_TYPE) == 'text'
                    and sd_item_associations[i].get('_type') == 'externalsource')
            ]
            # get all associated `text` items ids where `_type` is not `externalsource`.
            rel_text_items_ids = [
                sd_item_associations[i]['_id'] for i in sd_item_associations
                if (sd_item_associations[i] and sd_item_associations[i].get(ITEM_TYPE) == 'text'
                    and sd_item_associations[i].get('_type') != 'externalsource')
            ]
            # fetch associated docs by _id
            if rel_text_items_ids:
                rel_text_items += list(self.arhive_service.find({'_id': {'$in': rel_text_items_ids}}))
            for rel_text_item in rel_text_items:
                newsml_item = {k: v for k, v in sd_item.items() if k in KEYS_TO_INHERIT}
                newsml_item.update(rel_text_item)
                newsml_item['_role'] = self.NEWSCOMPONENT2_ROLES.RELATED_ARTICLE
                newsml_items_chain.append(newsml_item)

            # no need to store this data anymore
            sd_item.pop('associations', None)
            sd_item.pop('attachments', None)
            sd_item.pop('fields_meta', None)

        return tuple(newsml_items_chain)


def get_distribution_value(qcode):
    if str(qcode).lower() == 'bilingual':
        return 'B'
    return 'Default'
