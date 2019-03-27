# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from lxml import etree
from lxml.etree import SubElement
from eve.utils import config
from flask import current_app as app
import superdesk
from superdesk.utc import utcnow
from superdesk.errors import FormatterError
from superdesk.publish.formatters.newsml_g2_formatter import XML_LANG
from superdesk.publish.formatters import NewsML12Formatter
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, EMBARGO, GUID_FIELD

from apps.archive.common import get_utc_schedule

logger = logging.getLogger(__name__)


class BelgaNewsML12Formatter(NewsML12Formatter):
    """
    Belga News ML 1.2 1.2 Formatter
    """

    ENCODING = "ISO-8859-15"
    XML_ROOT = '<?xml version="1.0" encoding="{}"?>'.format(ENCODING)
    DATETIME_FORMAT = '%Y%m%dT%H%M%S'
    BELGA_TEXT_PROFILE = 'belga_text'

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
            # SD does not have the same structure, there are no packages,
            # but to cover old belga's news ml 1.2 output, this value will be used:
            self._package_duid = 'pkg_{}'.format(self._article[GUID_FIELD])

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

        return format_type == 'belganewsml12' and article[ITEM_TYPE] in {CONTENT_TYPE.TEXT, CONTENT_TYPE.PICTURE}

    def _format_catalog(self):
        """Creates Catalog and add it to `NewsML` container."""
        SubElement(
            self._newsml, 'Catalog',
            {'Href': 'http://www.belga.be/dtd/BelgaCatalog.xml'}
        )

    def _format_newsenvelope(self):
        """Creates NewsEnvelope and add it to `NewsML` container."""

        newsenvelope = SubElement(self._newsml, 'NewsEnvelope')
        SubElement(newsenvelope, 'DateAndTime').text = self._string_now
        SubElement(newsenvelope, 'NewsService', {'FormalName': ''})
        SubElement(newsenvelope, 'NewsProduct', {'FormalName': ''})

    def _format_newsitem(self):
        """Creates NewsItem and add it to `NewsML` container."""

        newsitem = SubElement(self._newsml, 'NewsItem')
        self._format_identification(newsitem)
        self._format_newsmanagement(newsitem)
        self._format_newscomponent_1_level(newsitem)

    def _format_identification(self, newsitem):
        """
        Creates the Identification element and add it to `newsitem`
        :param Element newsitem:
        """

        identification = SubElement(newsitem, 'Identification')
        news_identifier = SubElement(identification, 'NewsIdentifier')
        SubElement(news_identifier, 'ProviderId').text = app.config['NEWSML_PROVIDER_ID']
        SubElement(news_identifier, 'DateId').text = self._article.get('firstcreated').strftime(self.DATETIME_FORMAT)
        SubElement(news_identifier, 'NewsItemId').text = self._package_duid
        revision = self._process_revision(self._article)
        SubElement(news_identifier, 'RevisionId', attrib=revision).text = str(self._article.get(config.VERSION, ''))
        SubElement(news_identifier, 'PublicIdentifier').text = self._generate_public_identifier(
            self._article[config.ID_FIELD],
            self._article.get(config.VERSION, ''),
            revision.get('Update', '')
        )

    def _format_newsmanagement(self, newsitem):
        """
        Creates the NewsManagement element and add it to `newsitem`
        :param Element newsitem:
        """
        news_management = SubElement(newsitem, 'NewsManagement')
        SubElement(news_management, 'NewsItemType', {'FormalName': 'News'})
        SubElement(
            news_management, 'FirstCreated'
        ).text = self._article.get('firstcreated').strftime(self.DATETIME_FORMAT)
        SubElement(
            news_management, 'ThisRevisionCreated'
        ).text = self._article['versioncreated'].strftime(self.DATETIME_FORMAT)

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
        Creates the NewsComponent element and add it to `newsitem`
        :param Element newsitem:
        """

        newscomponent_1_level = SubElement(
            newsitem, 'NewsComponent',
            {'Duid': self._package_duid, XML_LANG: self._article.get('language')}
        )
        newslines = SubElement(newscomponent_1_level, 'NewsLines')
        SubElement(newslines, 'HeadLine').text = self._article.get('headline', '')
        SubElement(newscomponent_1_level, 'AdministrativeMetadata')
        descriptivemetadata = SubElement(newscomponent_1_level, 'DescriptiveMetadata')
        genre_formalname = ''
        for subject in self._article.get('subject', []):
            if subject['scheme'] == 'genre':
                genre_formalname = subject['qcode']
                break
        SubElement(
            descriptivemetadata, 'Genre',
            {'FormalName': genre_formalname}
        )

        self._format_newscomponent_2_level(newscomponent_1_level)

    def _format_newscomponent_2_level(self, newscomponent_1_level):
        """
        Creates the NewsComponent of a 2nd level element and add it to `newscomponent_1_level`
        :param Element newscomponent_1_level:
        """

        newscomponent_2_level = SubElement(
            newscomponent_1_level, 'NewsComponent',
            {'Duid': self._article[GUID_FIELD], XML_LANG: self._article.get('language')}
        )

        _type = self._article.get('type')
        _profile = self._article.get('profile')

        # belga text
        if _type == CONTENT_TYPE.TEXT and _profile == self.BELGA_TEXT_PROFILE:
            self._format_belga_text(newscomponent_2_level)
            self._format_related_newscomponents(newscomponent_1_level)
        # picture
        elif _type == CONTENT_TYPE.PICTURE:
            pass

    def _format_belga_text(self, newscomponent_2_level):
        """
        Fills a NewsComponent of a 2nd level with information related to `belga_text` content profile.
        :param Element newscomponent_2_level:
        """

        # Role
        SubElement(newscomponent_2_level, 'Role', {'FormalName': self.BELGA_TEXT_PROFILE})
        # NewsLines
        self._format_newslines(newscomponent_2_level)
        # AdministrativeMetadata
        self._format_administrative_metadata(newscomponent_2_level)
        # DescriptiveMetadata
        self._format_descriptive_metadata(newscomponent_2_level)
        # NewsComponent 3rd level
        self._format_newscomponent_3_level(newscomponent_2_level)

    def _format_picture(self, newscomponent_2_level):
        raise NotImplementedError

    def _format_newslines(self, newscomponent_2_level):
        """
        Creates the NewsLines element and add it to `newscomponent_2_level`
        :param Element newscomponent_2_level:
        """
        newslines = SubElement(newscomponent_2_level, 'NewsLines')
        SubElement(newslines, 'DateLine')
        SubElement(newslines, 'CreditLine').text = self._article.get('byline')
        SubElement(newslines, 'HeadLine').text = self._article.get('headline')
        SubElement(newslines, 'CopyrightLine').text = self._article.get('copyrightholder')
        for keyword in self._article.get('keywords', []):
            SubElement(newslines, 'KeywordLine').text = keyword
        newsline = SubElement(newslines, 'NewsLine')
        SubElement(newsline, 'NewsLineType', {'FormalName': self._article.get('line_type', '')})
        SubElement(newsline, 'NewsLineText').text = self._article.get('line_text')

    def _format_administrative_metadata(self, newscomponent_2_level):
        """
        Creates the AdministrativeMetadata element and add it to `newscomponent_2_level`
        :param Element newscomponent_2_level:
        """

        administrative_metadata = SubElement(newscomponent_2_level, 'AdministrativeMetadata')
        SubElement(
            SubElement(administrative_metadata, 'Provider'),
            'Party',
            {'FormalName': self._article.get('line_type', '')}
        )
        creator = SubElement(administrative_metadata, 'Creator')
        for author in self._article.get('authors', []):
            SubElement(
                creator, 'Party',
                {'FormalName': author.get('name', ''), 'Topic': author.get('role', '')}
            )
        SubElement(
            SubElement(administrative_metadata, 'Contributor'), 'Party',
            {'FormalName': self._article.get('administrative', {}).get('contributor', '')}
        )
        if 'validator' in self._article.get('administrative', {}):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'Validator', 'Value': self._article['administrative']['validator']}
            )
        if 'validation_date' in self._article.get('administrative', {}):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'ValidationDate', 'Value': self._article['administrative']['validation_date']}
            )
        if 'foreign_id' in self._article.get('administrative', {}):
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'ForeignId', 'Value': self._article['administrative']['foreign_id']}
            )
        if 'priority' in self._article:
            SubElement(
                administrative_metadata, 'Property',
                {'FormalName': 'Priority', 'Value': str(self._article['priority'])}
            )
        SubElement(
            administrative_metadata,
            'Property',
            {'FormalName': 'NewsObjectId', 'Value': self._article[GUID_FIELD]}
        )
        property_newspackage = SubElement(
            administrative_metadata, 'Property',
            {'FormalName': 'NewsPackage'}
        )
        for subject in self._article.get('subject', []):
            if subject['scheme'] == 'news_services':
                SubElement(
                    property_newspackage, 'Property',
                    {'FormalName': 'NewsService', 'Value': subject['qcode']}
                )
            elif subject['scheme'] == 'news_products':
                SubElement(
                    property_newspackage, 'Property',
                    {'FormalName': 'NewsProduct', 'Value': subject['qcode']}
                )

    def _format_descriptive_metadata(self, newscomponent_2_level):
        """
        Creates the DescriptiveMetadata element and add it to `newscomponent_2_level`
        :param Element newscomponent_2_level:
        """

        descriptive_metadata = SubElement(
            newscomponent_2_level, 'DescriptiveMetadata',
            {'DateAndTime': self._article['_created'].strftime(self.DATETIME_FORMAT)}
        )
        SubElement(descriptive_metadata, 'SubjectCode')
        location = SubElement(descriptive_metadata, 'Location')

        city_property = SubElement(location, 'Property', {'FormalName': 'City'})
        if self._article.get('extra', {}).get('city'):
            city_property.set('Value', self._article['extra']['city'])

        country_property = SubElement(location, 'Property', {'FormalName': 'Country'})
        if self._article.get('extra', {}).get('country'):
            country_property.set('Value', self._article['extra']['country'])

        SubElement(location, 'Property', {'FormalName': 'CountryArea'})
        SubElement(location, 'Property', {'FormalName': 'WorldRegion'})

    def _format_newscomponent_3_level(self, newscomponent_2_level):
        """
        Creates the NewsComponent(s) of a 3rd level element and add it to `newscomponent_2_level`
        :param Element newscomponent_2_level:
        """

        # Title, Lead, Body
        for formalname, item_key in (('Body', 'body_html'), ('Title', 'headline'), ('Lead', 'abstract')):
            if self._article.get(item_key):
                newscomponent_3_level = SubElement(
                    newscomponent_2_level, 'NewsComponent',
                    {'Duid': self._article[GUID_FIELD], XML_LANG: self._article.get('language')}
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
                SubElement(contentitem, 'DataContent').text = self._article.get(item_key)
                characteristics = SubElement(contentitem, 'Characteristics')
                # string's length is used in original belga's newsml
                SubElement(characteristics, 'SizeInBytes').text = str(len(self._article.get(item_key)))
                SubElement(characteristics, 'Property', {'FormalName': 'maxCharCount', 'Value': '0'})

    def _format_related_newscomponents(self, newscomponent_1_level):
        """
        Fills a NewsComponent of a 2nd level with information related to main NewsComponent.
        :param Element newscomponent_1_level:
        """

        # belga-url
        for belga_url in self._article.get('extra', {}).get('belga-url', []):
            newscomponent_2_level = SubElement(
                newscomponent_1_level, 'NewsComponent',
                {'Duid': self._article[GUID_FIELD], XML_LANG: self._article.get('language')}
            )
            SubElement(newscomponent_2_level, 'Role', {'FormalName': 'URL'})
            newslines = SubElement(newscomponent_2_level, 'NewsLines')
            SubElement(newslines, 'DateLine')
            SubElement(newslines, 'CreditLine').text = self._article.get('byline')
            SubElement(newslines, 'HeadLine').text = belga_url.get('description')
            SubElement(newslines, 'CopyrightLine').text = self._article.get('copyrightholder')
            self._format_administrative_metadata(newscomponent_2_level)
            self._format_descriptive_metadata(newscomponent_2_level)

            for role, key in (('Title', 'description'), ('Locator', 'url')):
                newscomponent_3_level = SubElement(
                    newscomponent_2_level, 'NewsComponent',
                    {'Duid': self._article[GUID_FIELD], XML_LANG: self._article.get('language')}
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
                SubElement(characteristics, 'SizeInBytes').text = str(len(belga_url.get(key)))
                SubElement(characteristics, 'Property', {'FormalName': 'maxCharCount', 'Value': '0'})
