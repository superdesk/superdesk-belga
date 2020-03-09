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
                                     ITEM_TYPE, ITEM_STATE, CONTENT_STATE)
from superdesk.publish.formatters import NewsML12Formatter
from superdesk.publish.formatters.newsml_g2_formatter import XML_LANG
from superdesk.utc import utcnow
from ..search_providers import BelgaImageSearchProvider

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
        'belga_text': 'Belga text'
    }
    SD_BELGA_IMAGE_RENDITIONS_MAP = {
        'original': 'full',
        'thumbnail': 'thumbnail',
        'viewImage': 'preview'
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

            self._newsml = etree.Element('NewsML')
            # current item
            self._item = article
            # the whole items chain including updates and translations with `published` state
            self._items_chain = [
                i for i in self.arhive_service.get_items_chain(self._item)
                if i.get(ITEM_STATE) in (CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED)
            ]
            # original/initial item
            self._original_item = self._items_chain[0]
            self._duid = self._original_item[GUID_FIELD]
            self._now = utcnow()
            # it's done to avoid difference between latest item's `ValidationDate` and `DateAndTime` in `NewsEnvelope`.
            # Theoretically it may happen
            if self._item.get('firstpublished'):
                self._string_now = self._get_formatted_datetime(self._item['firstpublished'])
            else:
                self._string_now = self._now.strftime(self.DATETIME_FORMAT)

            self._format_catalog()
            self._format_newsenvelope()
            self._format_newsitem()

            xml_string = self.XML_ROOT + '\n' + etree.tostring(self._newsml, pretty_print=True).decode('utf-8')
            pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)

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
            if item[ITEM_TYPE] in (CONTENT_TYPE.TEXT, CONTENT_TYPE.VIDEO):
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
        SubElement(news_identifier, 'DateId').text = self._get_formatted_datetime(self._item.get('firstcreated'))
        SubElement(news_identifier, 'NewsItemId').text = self._duid
        revision = self._process_revision(self._item)
        SubElement(news_identifier, 'RevisionId', attrib=revision).text = str(self._item.get(config.VERSION, ''))
        SubElement(news_identifier, 'PublicIdentifier').text = self._generate_public_identifier(
            self._item[config.ID_FIELD],
            self._item.get(config.VERSION, ''),
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
        ).text = self._get_formatted_datetime(self._item.get('firstcreated'))
        SubElement(
            news_management, 'ThisRevisionCreated'
        ).text = self._get_formatted_datetime(self._item['versioncreated'])

        if self._item.get(EMBARGO):
            SubElement(news_management, 'Status', {'FormalName': 'Embargoed'})
            status_will_change = SubElement(news_management, 'StatusWillChange')
            SubElement(
                status_will_change, 'FutureStatus',
                {'FormalName': self._item.get('pubstatus', '').upper()}
            )
            SubElement(
                status_will_change, 'DateAndTime'
            ).text = get_utc_schedule(self._item, EMBARGO).isoformat()
        else:
            SubElement(
                news_management, 'Status',
                {'FormalName': self._item.get('pubstatus', '').upper()}
            )

    def _format_newscomponent_1_level(self, newsitem):
        """
        Creates the `<NewsComponent>` element and adds it to `<NewsItem>`.
        :param Element newsitem: NewsItem
        """

        newscomponent_1_level = SubElement(
            newsitem, 'NewsComponent',
            {'Duid': self._duid, XML_LANG: self._item.get('language')}
        )
        newslines = SubElement(newscomponent_1_level, 'NewsLines')
        SubElement(newslines, 'HeadLine').text = self._item.get('headline', '')
        SubElement(newscomponent_1_level, 'AdministrativeMetadata')
        descriptivemetadata = SubElement(newscomponent_1_level, 'DescriptiveMetadata')
        genre_formalname = ''
        for subject in self._item.get('subject', []):
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

        for item in self._items_chain:
            if self._item[ITEM_TYPE] == CONTENT_TYPE.TEXT:
                self._format_text(newscomponent_1_level, item)
                self._format_belga_urls(newscomponent_1_level, item)
                self._format_media(newscomponent_1_level, item)
                self._format_attachments(newscomponent_1_level, item)
                self._format_related_text_item(newscomponent_1_level, item)
            elif self._item[ITEM_TYPE] == CONTENT_TYPE.VIDEO:
                self._format_video(newscomponent_1_level, video=self._item)

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
        if item.get('profile') in self.CP_NAME_ROLE_MAP:
            role_formal_name = self.CP_NAME_ROLE_MAP[item.get('profile')]
        else:
            role_formal_name = self._get_content_profile_name(item)
        SubElement(newscomponent_2_level, 'Role', {'FormalName': role_formal_name})
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

        associations = item.get('associations', {})

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
            items += list(self.arhive_service.find({
                '_id': {'$in': items_ids}}
            ))
        # format items
        for _item in items:
            # TODO: remove _format_related_text_item method and handle all items independently from
            #  the self._items_chain including associations, since every item in association is a
            #  standalone newscomponent of a 2nd level
            # SDBELGA-322
            # this is a case when _item is an external belga 360 archive.
            # parent's firstpublished is used in this case
            if not _item.get('firstpublished'):
                _item['firstpublished'] = item['firstpublished'] if item.get('firstpublished') else self._now

            # NewsComponent
            newscomponent_2_level = SubElement(newscomponent_1_level, 'NewsComponent')
            if _item.get(GUID_FIELD):
                newscomponent_2_level.attrib['Duid'] = _item.get(GUID_FIELD)
            if _item.get('language'):
                newscomponent_2_level.attrib[XML_LANG] = _item.get('language')
            # Role
            SubElement(newscomponent_2_level, 'Role', {'FormalName': 'RelatedArticle'})
            # NewsLines
            self._format_newslines(newscomponent_2_level, item=_item)
            # AdministrativeMetadata
            self._format_administrative_metadata(newscomponent_2_level, item=_item)
            # DescriptiveMetadata
            self._format_descriptive_metadata(newscomponent_2_level, item=_item)
            # NewsComponent 3rd level
            self._format_newscomponent_3_level(newscomponent_2_level, item=_item)

    def _format_belga_urls(self, newscomponent_1_level, item):
        """
        Creates a `NewsComponent`(s) of a 2nd level with data from custom url fields.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict item: item
        """

        for belga_url in item.get('extra', {}).get('belga-url', []):
            newscomponent_2_level = SubElement(
                newscomponent_1_level, 'NewsComponent',
                {XML_LANG: item.get('language')}
            )
            if item.get(GUID_FIELD):
                newscomponent_2_level.attrib['Duid'] = item[GUID_FIELD]

            SubElement(newscomponent_2_level, 'Role', {'FormalName': 'URL'})
            newslines = SubElement(newscomponent_2_level, 'NewsLines')
            SubElement(newslines, 'DateLine')
            SubElement(newslines, 'HeadLine').text = belga_url.get('description')
            SubElement(newslines, 'CopyrightLine').text = item.get('copyrightholder')
            SubElement(newslines, 'CreditLine').text = self._get_creditline(item)
            self._format_administrative_metadata(newscomponent_2_level, item=item)
            self._format_descriptive_metadata(newscomponent_2_level, item=item)

            for role, key in (('Title', 'description'), ('Locator', 'url')):
                newscomponent_3_level = SubElement(
                    newscomponent_2_level, 'NewsComponent',
                    {XML_LANG: item.get('language')}
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

    def _format_attachments(self, newscomponent_1_level, item):
        """
        Format attached to the item files.
        Creates `<NewsComponent>`(s) of a 2nd level and appends them to `newscomponent_1_level`.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict item: item
        """

        attachments_ids = [i['attachment'] for i in item.get('attachments', [])]
        attachments = list(self.attachments_service.find({'_id': {'$in': attachments_ids}}))
        for attachment in attachments:
            # attachment does not have a language, it inherits language from the main item
            if item.get('language'):
                attachment['language'] = item['language']
            self._format_attachment(newscomponent_1_level, attachment)

    def _format_media(self, newscomponent_1_level, item):
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
        :param dict item: item
        """

        # format media from associations
        associations = item.get('associations', {})
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
                and 'renditions' in item['associations'][i]
            ]
            # get all associated items `_id`s with type `_type` where `renditions` are NOT IN the item
            items_ids = [
                associations[i]['_id'] for i in associations
                if associations[i]
                and associations[i]['type'] == _type
                and 'renditions' not in item['associations'][i]
            ]

            # fetch associated docs by _id
            if items_ids:
                items += list(self.arhive_service.find({
                    '_id': {'$in': items_ids}}
                ))
            # format pictures
            formatted_ids = []
            for _item in items:
                # TODO: remove _format_media method and handle all items independently from
                #  the self._items_chain including associations, since every item in association is a
                #  standalone newscomponent of a 2nd level
                # SDBELGA-322
                # this is a case when _item is an external belga image or coverage.
                # parent's firstpublished is used in this case
                if not _item.get('firstpublished'):
                    _item['firstpublished'] = item['firstpublished'] if item.get('firstpublished') else self._now

                # if media does not have a language (search provider) it inherits language from the main item
                if not _item.get('language'):
                    _item['language'] = item['language']

                if _item['_id'] not in formatted_ids:
                    formatted_ids.append(_item['_id'])
                    _format(newscomponent_1_level, _item)

        # format media item from custom field `belga.coverage`
        extra = item.get('extra', {})
        belga_coverage_field_ids = [
            i['_id'] for i in self.vocabularies_service.find({'custom_field_type': 'belga.coverage'})
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

                    # if belga coverage does not have a language it inherits language from the main item
                    # NOTE: `belga.coverage` field is deprecated
                    if not data.get('language'):
                        data['language'] = item['language']

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

            # SDBELGA-345
            # if image is from "belga image", URN schema should be exported instead of URL
            if BelgaImageSearchProvider.GUID_PREFIX in picture.get(GUID_FIELD, ''):
                belga_image_id = picture[GUID_FIELD].split(BelgaImageSearchProvider.GUID_PREFIX, 1)[-1]
                picture['renditions'][key]['href'] = 'urn:www.belga.be:picturestore:' \
                                                     '{belga_image_id}:' \
                                                     '{belga_image_rendition}:true'.format(
                    belga_image_id=belga_image_id,
                    belga_image_rendition=self.SD_BELGA_IMAGE_RENDITIONS_MAP[key]
                )
                picture['renditions'][key]['filename'] = '{}.jpeg'.format(belga_image_id)

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
            {'FormalName': 'ComponentClass', 'Value': 'Audio'}
        )
        self._format_media_contentitem(newscomponent_3_level, rendition=video['renditions']['original'])

    def _format_attachment(self, newscomponent_1_level, attachment):
        """
        Creates a `<NewsComponent>` of a 2nd level with file attached to the item.
        :param Element newscomponent_1_level: NewsComponent of 1st level
        :param dict attachment: attachment
        """

        attachment['_id'] = str(attachment['_id'])
        attachment[GUID_FIELD] = attachment['_id']
        attachment['headline'] = attachment.pop('title')
        attachment['description_text'] = attachment.pop('description')
        attachment['firstcreated'] = attachment['_created']

        newscomponent_2_level = SubElement(
            newscomponent_1_level, 'NewsComponent',
            {
                XML_LANG: attachment.get('language'),
                'Duid': str(attachment.get('_id'))
            }
        )

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
        SubElement(newslines, 'HeadLine').text = item.get('headline')
        SubElement(newslines, 'CopyrightLine').text = item.get('copyrightholder')
        SubElement(newslines, 'CreditLine').text = self._get_creditline(item)

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
        # SDBELGA-322
        validation_date = self._string_now
        if item.get('firstpublished'):
            validation_date = self._get_formatted_datetime(item['firstpublished'])
        elif item.get('administrative', {}).get('validation_date'):
            validation_date = item['administrative']['validation_date']
        SubElement(
            administrative_metadata, 'Property',
            {'FormalName': 'ValidationDate', 'Value': validation_date}
        )
        if item.get('administrative', {}).get('foreign_id'):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'ForeignId', 'Value': item['administrative']['foreign_id']}
            )
        if item.get('priority'):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'Priority', 'Value': str(item['priority'])}
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

        if item.get('source'):
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
            'initials': '',
            'role': ''
        }

        # get author_id
        if type(author) is str:
            author_id = author
        else:
            try:
                author_id = author['_id'][0]
            except (KeyError, IndexError):
                author_id = None

        # most probably that author info was ingested
        if not author_id:
            author_info = {
                'initials': author.get('name', author.get('uri', '')),
                'role': author.get('role', ''),
            }
            return author_info

        # retrieve sd author info by id
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

        return author_info

    def _get_formatted_datetime(self, _datetime):
        if type(_datetime) is str:
            return datetime.strptime(_datetime, '%Y-%m-%dT%H:%M:%S+0000').strftime(self.DATETIME_FORMAT)
        else:
            return _datetime.strftime(self.DATETIME_FORMAT)

    def _get_content_profile_name(self, item):
        req = ParsedRequest()
        req.args = {}
        req.projection = '{"label": 1}'
        content_type = self.content_types_service.find_one(
            req=req,
            _id=item.get('profile')
        )
        return content_type['label'].capitalize()

    def _get_creditline(self, item):
        """
        Return a creditline for an `item`
        :param item: item
        :type item: dict
        :return: creditnline
        :rtype: str
        """

        # internal text item
        creditline = '/'.join([subj['qcode'] for subj in item.get('subject', []) if subj['scheme'] == 'credits'])
        if creditline:
            return creditline

        # internal picture/video/audio item
        creditline = [subj['qcode'] for subj in item.get('subject', []) if subj['scheme'] == 'media-credit']
        if creditline:
            return creditline[0]

        # external item i.e ingested, belga 360 archive, belga coverage or belga image
        return item.get('creditline')
