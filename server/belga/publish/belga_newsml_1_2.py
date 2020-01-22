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
import logging
from datetime import datetime
from urllib.parse import urljoin

from eve.utils import ParsedRequest
from flask import current_app as app

import superdesk
from apps.archive.common import get_utc_schedule
from belga.search_providers import BelgaCoverageSearchProvider
from eve.utils import config
from lxml import etree
from lxml.etree import SubElement
from superdesk.errors import FormatterError
from superdesk.metadata.item import (CONTENT_TYPE, EMBARGO, GUID_FIELD,
                                     ITEM_TYPE)
from superdesk.publish.formatters import NewsML12Formatter
from superdesk.publish.formatters.newsml_g2_formatter import XML_LANG
from superdesk.utc import utcnow

logger = logging.getLogger(__name__)


class BelgaNewsML12Formatter(NewsML12Formatter):
    """
    Belga News ML 1.2 Formatter
    """

    ENCODING = "ISO-8859-15"
    XML_ROOT = '<?xml version="1.0" encoding="{}"?>'.format(ENCODING)
    DATETIME_FORMAT = '%Y%m%dT%H%M%S'
    BELGA_TEXT_PROFILE = 'belga_text'
    CP_NAME_ROLE_MAP = {
        'belga_text': 'Text'
    }

    def format(self, article, subscriber, codes=None):
        """
        Create article in Belga NewsML 1.2 format

        :param dict article:
        :param dict subscriber:
        :param list codes:
        :return [(int, str)]: return a List of tuples. A tuple consist of
            publish sequence number and formatted article string.
        :raises FormatterError: if the formatter fails to format an article
        """

        try:
            pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)
            self._newsml = etree.Element('NewsML')
            self._article = article
            self._now = utcnow()
            self._string_now = self._now.strftime(self.DATETIME_FORMAT)
            self._duid = self._article[GUID_FIELD]

            self._format_catalog()
            self._format_newsenvelope()
            self._format_newsitem()

            xml_string = self.XML_ROOT + '\n' + etree.tostring(self._newsml, pretty_print=True).decode('utf-8')

            return [(pub_seq_num, xml_string)]
        except Exception as ex:
            raise FormatterError.newml12FormatterError(ex, subscriber)

    def can_format(self, format_type, article):
        """
        Test if the article can be formatted to Belga NewsML 1.2 or not.

        :param str format_type:
        :param dict article:
        :return: True if article can formatted else False
        """

        if format_type == 'belganewsml12':
            if article[ITEM_TYPE] in (CONTENT_TYPE.TEXT, CONTENT_TYPE.VIDEO):
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
        SubElement(news_identifier, 'DateId').text = self._get_formatted_datetime(self._article.get('firstcreated'))
        SubElement(news_identifier, 'NewsItemId').text = self._duid
        revision = self._process_revision(self._article)
        SubElement(news_identifier, 'RevisionId', attrib=revision).text = str(self._article.get(config.VERSION, ''))
        SubElement(news_identifier, 'PublicIdentifier').text = self._generate_public_identifier(
            self._article[config.ID_FIELD],
            self._article.get(config.VERSION, ''),
            revision.get('Update', '')
        )

    def _format_newsmanagement(self, newsitem):
        """
        Creates the `<NewsManagement>` element and adds it to `<NewsItem>`.
        :param Element newsitem: NewsItem
        """

        news_management = SubElement(newsitem, 'NewsManagement')
        SubElement(news_management, 'NewsItemType', {'FormalName': 'News'})
        SubElement(
            news_management, 'FirstCreated'
        ).text = self._get_formatted_datetime(self._article.get('firstcreated'))
        SubElement(
            news_management, 'ThisRevisionCreated'
        ).text = self._get_formatted_datetime(self._article['versioncreated'])

        if self._article.get(EMBARGO):
            SubElement(news_management, 'Status', {'FormalName': 'Embargoed'})
            status_will_change = SubElement(news_management, 'StatusWillChange')
            SubElement(
                status_will_change, 'FutureStatus',
                {'FormalName': self._article.get('pubstatus', '').upper()}
            )
            SubElement(
                status_will_change, 'DateAndTime'
            ).text = get_utc_schedule(self._article, EMBARGO).isoformat()
        else:
            SubElement(
                news_management, 'Status',
                {'FormalName': self._article.get('pubstatus', '').upper()}
            )

    def _format_newscomponent_1_level(self, newsitem):
        """
        Creates the `<NewsComponent>` element and adds it to `<NewsItem>`.
        :param Element newsitem: NewsItem
        """

        newscomponent_1_level = SubElement(
            newsitem, 'NewsComponent',
            {'Duid': self._duid, XML_LANG: self._article.get('language')}
        )
        newslines = SubElement(newscomponent_1_level, 'NewsLines')
        SubElement(newslines, 'HeadLine').text = self._article.get('headline', '')
        SubElement(newscomponent_1_level, 'AdministrativeMetadata')
        descriptivemetadata = SubElement(newscomponent_1_level, 'DescriptiveMetadata')
        genre_formalname = ''
        for subject in self._article.get('subject', []):
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

        if self._article[ITEM_TYPE] == CONTENT_TYPE.TEXT:
            self._format_text(newscomponent_1_level)
            self._format_belga_urls(newscomponent_1_level)
            self._format_media(newscomponent_1_level)
            self._format_attachments(newscomponent_1_level)
            self._format_related_text_item(newscomponent_1_level)
        elif self._article[ITEM_TYPE] == CONTENT_TYPE.VIDEO:
            self._format_video(newscomponent_1_level, video=self._article)

    def _format_text(self, newscomponent_1_level):
        """
        Creates a `<NewsComponent>` of a 2nd level with information related to content profile.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        """

        newscomponent_2_level = SubElement(
            newscomponent_1_level, 'NewsComponent',
            {XML_LANG: self._article.get('language')}
        )

        # Role
        if self._article.get('profile') in self.CP_NAME_ROLE_MAP:
            role_formal_name = self.CP_NAME_ROLE_MAP[self._article.get('profile')]
        else:
            role_formal_name = self._get_content_profile_name()
        SubElement(newscomponent_2_level, 'Role', {'FormalName': role_formal_name})
        # NewsLines
        self._format_newslines(newscomponent_2_level, item=self._article)
        # AdministrativeMetadata
        self._format_administrative_metadata(newscomponent_2_level, item=self._article)
        # DescriptiveMetadata
        self._format_descriptive_metadata(newscomponent_2_level, item=self._article)
        # NewsComponent 3rd level
        self._format_newscomponent_3_level(newscomponent_2_level, item=self._article)

    def _format_related_text_item(self, newscomponent_1_level):
        """
        Creates a `<NewsComponent>` of a 2nd level with associated related text item.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict picture: picture item
        """

        associations = self._article.get('associations', {})

        # get all associated `text` items where `_type` is `externalsource`.
        items = [
            associations[i] for i in associations
            if (associations[i] and associations[i]['type'] == 'text'
                and associations[i].get('_type') == 'externalsource')
        ]
        # get all associated `text` items ids where `_type` is not `externalsource`.
        items_ids = [
            associations[i]['_id'] for i in associations
            if (associations[i] and associations[i]['type'] == 'text'
                and associations[i].get('_type') != 'externalsource')
        ]
        # fetch associated docs by _id
        if items_ids:
            archive_service = superdesk.get_resource_service('archive')
            items += list(archive_service.find({
                '_id': {'$in': items_ids}}
            ))
        # format items
        for item in items:
            # NewsComponent
            newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
            if item.get(GUID_FIELD):
                newscomponent_2_level.attrib['Duid'] = item.get(GUID_FIELD)
            if item.get('language'):
                newscomponent_2_level.attrib[XML_LANG] = item.get('language')
            # Role
            SubElement(newscomponent_2_level, 'Role', {'FormalName': 'RelatedArticle'})
            # NewsLines
            self._format_newslines(newscomponent_2_level, item=item)
            # AdministrativeMetadata
            self._format_administrative_metadata(newscomponent_2_level, item=item)
            # DescriptiveMetadata
            self._format_descriptive_metadata(newscomponent_2_level, item=item)
            # NewsComponent 3rd level
            self._format_newscomponent_3_level(newscomponent_2_level, item=item)

    def _format_belga_urls(self, newscomponent_1_level):
        """
        Creates a `NewsComponent`(s) of a 2nd level with data from custom url fields.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        """

        for belga_url in self._article.get('extra', {}).get('belga-url', []):
            newscomponent_2_level = SubElement(
                newscomponent_1_level, 'NewsComponent',
                {XML_LANG: self._article.get('language')}
            )
            SubElement(newscomponent_2_level, 'Role', {'FormalName': 'URL'})
            newslines = SubElement(newscomponent_2_level, 'NewsLines')
            SubElement(newslines, 'DateLine')
            SubElement(newslines, 'CreditLine').text = self._article.get('byline')
            SubElement(newslines, 'HeadLine').text = belga_url.get('description')
            SubElement(newslines, 'CopyrightLine').text = self._article.get('copyrightholder')
            self._format_administrative_metadata(newscomponent_2_level, item=self._article)
            self._format_descriptive_metadata(newscomponent_2_level, item=self._article)

            for role, key in (('Title', 'description'), ('Locator', 'url')):
                newscomponent_3_level = SubElement(
                    newscomponent_2_level, 'NewsComponent',
                    {XML_LANG: self._article.get('language')}
                )
                SubElement(newscomponent_3_level, 'Role', {'FormalName': role})
                SubElement(
                    SubElement(newscomponent_3_level, 'DescriptiveMetadata'),
                    'Property',
                    {'FormalName': 'ComponentClass', 'Value': 'Text'}
                )
                contentitem = SubElement(newscomponent_3_level, 'ContentItem')
                SubElement(contentitem, 'Format', {'FormalName': 'Text'})
                SubElement(contentitem, 'DataContent').text = belga_url.get(key)
                characteristics = SubElement(contentitem, 'Characteristics')
                # string's length is used in original belga's newsml
                SubElement(
                    characteristics, 'SizeInBytes'
                ).text = str(len(belga_url[key])) if belga_url.get(key) else '0'
                SubElement(characteristics, 'Property', {'FormalName': 'maxCharCount', 'Value': '0'})

    def _format_attachments(self, newscomponent_1_level):
        """
        Format attached to the article files.
        Creates `<NewsComponent>`(s) of a 2nd level and appends them to `newscomponent_1_level`.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        """

        attachments_ids = [i['attachment'] for i in self._article.get('attachments', [])]
        attachments_service = superdesk.get_resource_service('attachments')
        attachments = list(attachments_service.find({'_id': {'$in': attachments_ids}}))
        for attachment in attachments:
            self._format_attachment(newscomponent_1_level, attachment)

    def _format_media(self, newscomponent_1_level):
        """
        Format media items.
        Creates `<NewsComponent>`(s) of a 2nd level and appends them to `newscomponent_1_level`.

        - Associated items with type `picture` (images from body / related images / related gallery) will be
          converted to Belga360 NewsML representation as an `Image`.
        - Associated items with type `graphic` (belga coverage) will be converted to Belga360 NewsML representation
          as an `Gallery`.
        - Associated items with type `audio` will be converted to Belga360 NewsML representation
          as an `Audio`.
        - Associated items with type `video` will be converted to Belga360 NewsML representation
          as an `Video`.
        - Belga coverage from `belga.coverage` custom field will be converted to Belga360 NewsML
          representation as an `Gallery`.

        :param Element newscomponent_1_level: NewsComponent of 1st level
        """

        # format media from associations
        associations = self._article.get('associations', {})
        for _type, _format in (
                ('picture', self._format_picture),
                ('graphic', self._format_coverage),
                ('audio', self._format_audio),
                ('video', self._format_video)
        ):
            # get all associated items with type `_type` where `renditions` are already IN the items.
            items = [
                associations[i] for i in associations
                if associations[i]
                and associations[i]['type'] == _type
                and 'renditions' in self._article['associations'][i]
            ]
            # get all associated items `_id`s with type `_type` where `renditions` are NOT IN the item
            items_ids = [
                associations[i]['_id'] for i in associations
                if associations[i]
                and associations[i]['type'] == _type
                and 'renditions' not in self._article['associations'][i]
            ]

            # fetch associated docs by _id
            if items_ids:
                archive_service = superdesk.get_resource_service('archive')
                items += list(archive_service.find({
                    '_id': {'$in': items_ids}}
                ))
            # format pictures
            formatted_ids = []
            for item in items:
                if item['_id'] not in formatted_ids:
                    formatted_ids.append(item['_id'])
                    _format(newscomponent_1_level, item)

        # format media item from custom field `belga.coverage`
        extra = self._article.get('extra', {})
        vocabularies_service = superdesk.get_resource_service('vocabularies')
        belga_coverage_field_ids = [
            i['_id'] for i in vocabularies_service.find({'custom_field_type': 'belga.coverage'})
        ]
        for belga_coverage_field_id in belga_coverage_field_ids:
            if belga_coverage_field_id in extra:
                belga_item_id = extra[belga_coverage_field_id]
                belga_cov_search_provider = BelgaCoverageSearchProvider({})
                try:
                    data = belga_cov_search_provider.api_get('/getGalleryById', {'i': belga_item_id.rsplit(':', 1)[-1]})
                except Exception as e:
                    logger.warning("Failed to fetch belga coverage: {}".format(e))
                else:
                    data = belga_cov_search_provider.format_list_item(data)
                    self._format_coverage(newscomponent_1_level, data)

    def _format_picture(self, newscomponent_1_level, picture):
        """
        Creates a `<NewsComponent>` of a 2nd level with associated picture data.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict picture: picture item
        """

        # NewsComponent
        newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
        if picture.get(GUID_FIELD):
            newscomponent_2_level.attrib['Duid'] = picture.get(GUID_FIELD)
        if picture.get('language'):
            newscomponent_2_level.attrib[XML_LANG] = picture.get('language')
        # Role
        SubElement(newscomponent_2_level, 'Role', {'FormalName': 'Picture'})
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
            SubElement(contentitem, 'DataContent').text = picture.get(key)
            characteristics = SubElement(contentitem, 'Characteristics')
            # string's length is used in original belga's newsml
            SubElement(characteristics, 'SizeInBytes').text = str(len(picture[key])) if picture.get(key) else '0'
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

        newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
        if coverage.get(GUID_FIELD):
            newscomponent_2_level.attrib['Duid'] = coverage.get(GUID_FIELD)
        if coverage.get('language'):
            newscomponent_2_level.attrib[XML_LANG] = coverage.get('language')
        SubElement(newscomponent_2_level, 'Role', {'FormalName': 'Gallery'})
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

        newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
        if audio.get(GUID_FIELD):
            newscomponent_2_level.attrib['Duid'] = audio.get(GUID_FIELD)
        if audio.get('language'):
            newscomponent_2_level.attrib[XML_LANG] = audio.get('language')
        SubElement(newscomponent_2_level, 'Role', {'FormalName': 'Audio'})
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

        newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
        if video.get(GUID_FIELD):
            newscomponent_2_level.attrib['Duid'] = video.get(GUID_FIELD)
        if video.get('language'):
            newscomponent_2_level.attrib[XML_LANG] = video.get('language')
        SubElement(newscomponent_2_level, 'Role', {'FormalName': 'Video'})
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
            SubElement(contentitem, 'DataContent').text = video.get(key)
            characteristics = SubElement(contentitem, 'Characteristics')
            # string's length is used in original belga's newsml
            SubElement(characteristics, 'SizeInBytes').text = str(len(video[key])) if video.get(key) else '0'
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
            {'FormalName': 'ComponentClass', 'Value': 'Audio'}
        )
        self._format_media_contentitem(newscomponent_3_level, rendition=video['renditions']['original'])

    def _format_attachment(self, newscomponent_1_level, attachment):
        """
        Creates a `<NewsComponent>` of a 2nd level with file attached to the article.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict attachment: attachment
        """

        attachment['_id'] = str(attachment['_id'])
        attachment[GUID_FIELD] = attachment['_id']
        attachment['headline'] = attachment.pop('title')
        attachment['description_text'] = attachment.pop('description')

        newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
        newscomponent_2_level.attrib['Duid'] = str(attachment.get('_id'))

        SubElement(newscomponent_2_level, 'Role', {'FormalName': 'RelatedDocument'})
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
                'href': urljoin(app.config['MEDIA_PREFIX'] + '/', '{}?resource=attachments'.format(attachment['media']))
            }
        )

    def _format_media_contentitem(self, newscomponent_3_level, rendition):
        """
        Creates a ContentItem for provided rendition.
        :param Element newscomponent_3_level: NewsComponent of 3st level
        :param dict rendition: rendition info
        """
        contentitem = SubElement(
            newscomponent_3_level, 'ContentItem',
            {'Href': r'{}'.format(rendition['href'])}
        )

        filename = rendition['filename'] if rendition.get('filename') else rendition['href'].rsplit('/', 1)[-1]
        SubElement(contentitem, 'Format', {'FormalName': filename.rsplit('.', 1)[-1].capitalize()})
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
        SubElement(newslines, 'CreditLine').text = item.get('creditline', item.get('byline'))
        SubElement(newslines, 'HeadLine').text = item.get('headline')
        SubElement(newslines, 'CopyrightLine').text = item.get('copyrightholder')

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
                break

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
                {'FormalName': author['name'], 'Topic': author['role']}
            )
        if 'contributor' in item.get('administrative', {}):
            SubElement(
                SubElement(administrative_metadata, 'Contributor'), 'Party',
                {'FormalName': item['administrative']['contributor']}
            )
        if 'validator' in item.get('administrative', {}):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'Validator', 'Value': item['administrative']['validator']}
            )
        if 'validation_date' in item.get('administrative', {}):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'ValidationDate', 'Value': item['administrative']['validation_date']}
            )
        if 'foreign_id' in item.get('administrative', {}):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'ForeignId', 'Value': item['administrative']['foreign_id']}
            )
        if 'priority' in item:
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'Priority', 'Value': str(item['priority'])}
            )
        SubElement(
            administrative_metadata,
            'Property',
            {'FormalName': 'NewsObjectId', 'Value': item[GUID_FIELD]}
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

        if 'source' in item:
            SubElement(
                SubElement(administrative_metadata, 'Source'),
                'Party',
                {'FormalName': item['source']}
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

        country_property = SubElement(location, 'Property', {'FormalName': 'Country'})
        if item.get('extra', {}).get('country'):
            country_property.set('Value', item['extra']['country'])

        SubElement(location, 'Property', {'FormalName': 'CountryArea'})
        SubElement(location, 'Property', {'FormalName': 'WorldRegion'})

    def _format_newscomponent_3_level(self, newscomponent_2_level, item):
        """
        Creates the `<NewsComponent>`(s) of a 3rd level element for text item and adds it to `newscomponent_2_level`
        :param Element newscomponent_2_level: NewsComponent of 2nd level
        """

        # Title, Lead, Body
        for formalname, item_key in (('Body', 'body_html'), ('Title', 'headline'), ('Lead', 'abstract')):
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
                text = html.escape(item.get(item_key))
                SubElement(contentitem, 'DataContent').text = text
                characteristics = SubElement(contentitem, 'Characteristics')
                # string's length is used in original belga's newsml
                SubElement(characteristics, 'SizeInBytes').text = str(len(text))
                SubElement(characteristics, 'Property', {'FormalName': 'maxCharCount', 'Value': '0'})

    def _get_author_info(self, author):
        author_info = {
            'name': '',
            'role': ''
        }
        users_service = superdesk.get_resource_service('users')

        if type(author) is str:
            author_id = author
            try:
                user = next(users_service.find({'_id': author_id}))
            except StopIteration:
                logger.warning("unknown user: {user_id}".format(user_id=author_id))
            else:
                if user.get('display_name'):
                    author_info['name'] = user.get('display_name')
                if user.get('role'):
                    roles_service = superdesk.get_resource_service('roles')
                    try:
                        role = next(roles_service.find({'_id': user['role']}))
                    except StopIteration:
                        logger.warning("unknown role: {role_id}".format(role_id=user['role']))
                    else:
                        author_info['role'] = role.get('author_role', '')
        else:
            author_info['name'] = author.get('sub_label', author['name'] if author.get('name') else '')
            author_info['role'] = author['role'] if author.get('role') else ''

            if 'parent' in author:
                try:
                    user = next(users_service.find({'_id': author['parent']}))
                except StopIteration:
                    logger.warning("unknown user: {user_id}".format(user_id=author['parent']))
                else:
                    if user.get('display_name'):
                        author_info['name'] = user.get('display_name')

        return author_info

    def _get_formatted_datetime(self, _datetime):
        if type(_datetime) is str:
            return datetime.strptime(_datetime, '%Y-%m-%dT%H:%M:%S+0000').strftime(self.DATETIME_FORMAT)
        else:
            return _datetime.strftime(self.DATETIME_FORMAT)

    def _get_content_profile_name(self):
        content_types_service = superdesk.get_resource_service('content_types')
        req = ParsedRequest()
        req.args = {}
        req.projection = '{"label": 1}'
        content_type = content_types_service.find_one(
            req=req,
            _id=self._article.get('profile')
        )
        return content_type['label']
