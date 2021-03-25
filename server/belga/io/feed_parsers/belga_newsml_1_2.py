# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

import os
import hashlib
import logging
from io import BytesIO
from copy import deepcopy
from uuid import uuid4
from ftplib import error_perm
from tempfile import gettempdir
from datetime import datetime

from flask import current_app as app
from xml.etree import ElementTree

from superdesk import get_resource_service
from superdesk.ftp import ftp_connect
from superdesk.errors import ParserError
from superdesk.io.registry import register_feed_parser
from superdesk.io.feeding_services import FileFeedingService, FTPFeedingService
from superdesk.publish.formatters.newsml_g2_formatter import XML_LANG
from superdesk.media.media_operations import process_file_from_stream
from superdesk.utc import local_to_utc
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE

from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser, SkipItemException


logger = logging.getLogger(__name__)


class BelgaNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser which can parse specific Belga News ML xml files."""

    NAME = 'belganewsml12'

    label = 'Belga News ML 1.2 Parser'

    SUPPORTED_TEXT_ASSET_TYPES = ('ALERT', 'SHORT', 'TEXT', 'BRIEF', 'ORIGINAL')
    SUPPORTED_MEDIA_ASSET_TYPES = {
        'VIDEO': {
            'CLIP': 'original',
            'IMAGE': 'thumbnail',
        },
        'AUDIO': {
            'SOUND': 'original',
        }
    }
    SUPPORTED_BINARY_ASSET_SUBTYPES = ('SOUND', 'CLIP', 'COMPONENT', 'IMAGE')
    MOVE_FILE = False

    def __init__(self):
        super().__init__()
        self._provider = None

    def can_parse(self, xml):
        """
        Check NewsML type for file.

        :param xml:
        :return:
        """
        return xml.tag == 'NewsML'

    def parse(self, xml, provider=None):
        """
        Parse content the xml newsml file to json object.

        Example content the xml newsml file:

        <?xml version="1.0" encoding="utf-8"?>
        <NewsML Version="1.2">
          <!--AFP NewsML text-photo profile evolution2-->
          <!--Processed by Xafp1-4ToNewsML1-2 rev21-->
          <Catalog Href="http://www.afp.com/dtd/AFPCatalog.xml"/>
          <NewsEnvelope>
            ......
          </NewsEnvelope>
          <NewsItem xml:lang="fr">
            <Identification>
                .......
            </Identification>
            <NewsManagement>
                ......
            </NewsManagement>
            <NewsComponent>
                ......
            </NewsComponent>
          </NewsItem>
        </NewsML>

        :param xml:
        :param provider:
        :return:
        """

        self._provider = provider
        if self._provider is None:
            self._provider = {}

        try:
            self.root = xml
            self._items = []
            self._item_seed = {}
            # parser the NewsEnvelope element
            self._item_seed.update(
                self.parse_newsenvelop(xml.find('NewsEnvelope'))
            )
            # parser the NewsItem element
            for newsitem_el in xml.findall('NewsItem'):
                try:
                    self.parse_newsitem(newsitem_el)
                except SkipItemException:
                    continue

            return self._items
        except Exception as ex:
            raise ParserError.newsmlOneParserError(ex, self._provider)

    def parse_newsenvelop(self, envelop_el):
        """
        Parser Identification element.

        Example:

         <NewsEnvelope>
            <DateAndTime>20190212T072817</DateAndTime>
            <NewsService FormalName=""/>
            <NewsProduct FormalName=""/>
         </NewsEnvelope>

        :param envelop_el:
        :return:
        """
        # not that much we can get here
        return {}

    def parse_newsitem(self, newsitem_el):
        """
        Parse Newsitem element.

        Example:

         <NewsItem xml:lang="fr">
            <Identification>
                ....
            </Identification>
            <NewsManagement>
                ....
            </NewsManagement>
            <NewsComponent>
                ....
            </NewsComponent>
          </NewsItem>

        :param item:
        :param newsitem_el:
        :return:
        """
        # Identification
        self._item_seed.update(
            self.parse_identification(newsitem_el.find('Identification'))
        )

        # NewsManagement
        self._item_seed.update(
            self.parse_newsmanagement(newsitem_el.find('NewsManagement'))
        )

        # NewsComponent
        news_component_1 = newsitem_el.find('NewsComponent')
        if news_component_1 is None:
            return

        # Genre from NewsComponent 1st level
        for element in news_component_1.findall('DescriptiveMetadata/Genre'):
            if element.get('FormalName'):
                # genre CV
                self._item_seed.setdefault('subject', []).append({
                    "name": element.get('FormalName'),
                    "qcode": element.get('FormalName'),
                    "scheme": "genre"
                })

        # check if all roles are in `SUPPORTED_MEDIA_ASSET_TYPES`
        is_media_roles = [
            el.get('FormalName').upper() in self.SUPPORTED_MEDIA_ASSET_TYPES.keys()
            for el in news_component_1.findall('NewsComponent/Role')
        ]
        # check if all roles are in `SUPPORTED_TEXT_ASSET_TYPES`
        is_text_roles = [
            el.get('FormalName').upper() in self.SUPPORTED_TEXT_ASSET_TYPES
            for el in news_component_1.findall('NewsComponent/Role')
        ]
        # not all 2nd level NewsComponents are media items,
        # save media items as attachments for text items
        if not all(is_text_roles) and not all(is_media_roles):
            # parse attachment
            self._item_seed.update(self.parse_attachments(news_component_1))

        # NewsComponent 2nd level
        # NOTE: each NewsComponent of 2nd level is a separate item with unique GUID
        for news_component_2 in news_component_1.findall('NewsComponent'):
            # guid
            guid = news_component_2.attrib.get('Duid')
            # most probably it's belga remote
            if guid is None or guid == '0':
                guid = str(uuid4())

            # deepcopy to avoid having a pointer to `subject`
            item = deepcopy({**self._item_seed, 'guid': guid})

            try:
                # all 2nd level NewsComponents are media items,
                # ingest them as a standalone media items (not attachments)
                if all(is_media_roles):
                    self.parse_newscomponent_media(item, news_component_2)
                # all 2nd level NewsComponents are text items,
                # ingest them as a text items
                else:
                    self.parse_newscomponent_text(item, news_component_2)
            except SkipItemException:
                continue

            self._items.append(item)

    def parse_identification(self, indent_el):
        """
        Parse Identification in NewsItem element.

        Example:

        <Identification>
          <NewsIdentifier>
            <ProviderId>afp.com</ProviderId>
            <DateId>20181209T112417Z</DateId>
            <NewsItemId>TX-PAR-QCJ26</NewsItemId>
            <RevisionId PreviousRevision="0" Update="N">1</RevisionId>
            <PublicIdentifier>urn:newsml:afp.com:20181209T112417Z:TX-PAR-QCJ26:1</PublicIdentifier>
          </NewsIdentifier>
          <NameLabel>musique-rock-célébrités-religion-France</NameLabel>
        </Identification>

        :param item:
        :param indent_el:
        :return: dict
        """
        identification = {}

        if indent_el is None:
            return identification

        newsident_el = indent_el.find('NewsIdentifier')
        if newsident_el is not None:
            element = newsident_el.find('ProviderId')
            if element is not None:
                # provider_id
                identification['provider_id'] = element.text

            element = newsident_el.find('DateId')
            if element is not None:
                # date_id
                identification['date_id'] = element.text

            element = newsident_el.find('NewsItemId')
            if element is not None:
                # item_id
                identification['item_id'] = element.text

            element = newsident_el.find('RevisionId')
            if element is not None and element.text:
                # version
                try:
                    version = int(element.text)
                except ValueError:
                    version = 1
                if version == 0:
                    version = 1
                identification['version'] = version

            element = newsident_el.find('PublicIdentifier')
            if element is not None:
                # public_identifier
                identification['public_identifier'] = element.text

        return identification

    def parse_newsmanagement(self, manage_el):
        """
        Parse NewsManagement in NewsItem element.

        Example:

        <NewsManagement>
          <NewsItemType FormalName="NEWS"/>
          <FirstCreated>20190212T081049</FirstCreated>
          <ThisRevisionCreated>20190212T083703</ThisRevisionCreated>
          <Status FormalName="USABLE"/>
        </NewsManagement>

        :param item:
        :param manage_el:
        :return: dict
        """
        newsmanagement = {}
        tz = 'Europe/Brussels'

        if manage_el is None:
            return newsmanagement

        element = manage_el.find('FirstCreated')
        if element is not None:
            # firstcreated
            newsmanagement['firstcreated'] = local_to_utc(tz, self.datetime(element.text))

        element = manage_el.find('ThisRevisionCreated')
        if element is not None:
            # versioncreated
            newsmanagement['versioncreated'] = local_to_utc(tz, self.datetime(element.text))

        element = manage_el.find('Status')
        if element is not None and element.get('FormalName'):
            # pubstatus
            newsmanagement['pubstatus'] = element.get('FormalName').lower()

        return newsmanagement

    def parse_newscomponent_text(self, item, newscomponent_el):
        """
        Parse NewsComponent in NewsItem element.
        Supports only text items which roles are in `SUPPORTED_TEXT_ASSET_TYPES`

        Example:

        <NewsComponent>
          <NewsLines>
              <DateLine xml:lang="fr">Paris, 9 déc 2018 (AFP) -</DateLine>
            <HeadLine xml:lang="fr">Un an après, les fans de Johnny lui rendent hommage à Paris</HeadLine>
            <NewsLine>
              <NewsLineType FormalName="ProductLine"/>
              <NewsLineText xml:lang="fr">(Photo+Live Video+Video)</NewsLineText>
            </NewsLine>
          </NewsLines>
          <AdministrativeMetadata>
            <Provider>
              <Party FormalName="AFP"/>
            </Provider>
          </AdministrativeMetadata>
          <DescriptiveMetadata>
            ....
          </DescriptiveMetadata>
          <ContentItem>
            ....
          </ContentItem>
        </NewsComponent>

        :param item:
        :param component_el:
        :return:
        """
        # Role
        role = newscomponent_el.find('Role')
        if role is not None:
            role_name = role.attrib.get('FormalName')
            if not (role_name and role_name.upper() in self.SUPPORTED_TEXT_ASSET_TYPES):
                logger.warning('NewsComponent/Role/FormalName is not supported: "{}". '
                               'Skiping an "{}" item.'.format(role_name, item['guid']))
                raise SkipItemException
        else:
            logger.warning('NewsComponent/Role was not found. Skiping an "{}" item.'.format(
                item['guid']
            ))
            raise SkipItemException

        # language
        item['language'] = newscomponent_el.attrib.get(XML_LANG)

        # NewsLines
        newslines_el = newscomponent_el.find('NewsLines')
        self.parse_newslines(item, newslines_el)

        # AdministrativeMetadata
        admin_el = newscomponent_el.find('AdministrativeMetadata')
        self.parse_administrativemetadata(item, admin_el)

        # DescriptiveMetadata
        descript_el = newscomponent_el.find('DescriptiveMetadata')
        self.parse_descriptivemetadata(item, descript_el)

        # get 3rd level NewsComponent
        # body_html, headline, abstract
        for formalname, item_key in (('Body', 'body_html'), ('Title', 'headline'), ('Lead', 'abstract')):
            role = newscomponent_el.find('NewsComponent/Role[@FormalName="{}"]'.format(formalname))
            if role is not None:
                newscomponent = role.getparent()
                datacontent = newscomponent.find('ContentItem/DataContent')
                format = newscomponent.find('ContentItem/Format')

                if datacontent is not None and format is not None:
                    formalname = format.attrib.get('FormalName')
                    if not formalname or formalname != 'Text':
                        logger.warning(
                            'ContentItem/FormalName was not found or not supported: "{}". '
                            'Skiping an "{}" item.'.format(formalname, item['guid'])
                        )
                        raise SkipItemException
                    if datacontent.text:
                        item[item_key] = datacontent.text.strip()

                        if item_key == 'body_html':
                            item[item_key] = self._plain_to_html(item[item_key])
                else:
                    logger.warning('Mimetype or DataContent was not found. Skiping an "{}" item.'.format(
                        item['guid']
                    ))
                    raise SkipItemException

        # SDBELGA-328
        if item.get('abstract'):
            abstract = '<p>' + item['abstract'] + '</p>'
            item['body_html'] = abstract + item.get('body_html', '')

        # type
        item[ITEM_TYPE] = CONTENT_TYPE.TEXT

        return item

    def parse_newscomponent_media(self, item, newscomponent_el):
        """
        Parse NewsComponent in NewsItem element.
        Supports only text items which roles are in `SUPPORTED_MEDIA_ASSET_TYPES`

        Example:

        <NewsComponent>
          <NewsLines>
              <DateLine xml:lang="fr">Paris, 9 déc 2018 (AFP) -</DateLine>
            <HeadLine xml:lang="fr">Un an après, les fans de Johnny lui rendent hommage à Paris</HeadLine>
            <NewsLine>
              <NewsLineType FormalName="ProductLine"/>
              <NewsLineText xml:lang="fr">(Photo+Live Video+Video)</NewsLineText>
            </NewsLine>
          </NewsLines>
          <AdministrativeMetadata>
            <Provider>
              <Party FormalName="AFP"/>
            </Provider>
          </AdministrativeMetadata>
          <DescriptiveMetadata>
            ....
          </DescriptiveMetadata>
          <ContentItem>
            ....
          </ContentItem>
        </NewsComponent>

        :param item:
        :param component_el:
        :return:
        """

        # language
        item['language'] = newscomponent_el.attrib.get(XML_LANG)

        # NewsLines
        newslines_el = newscomponent_el.find('NewsLines')
        self.parse_newslines(item, newslines_el)

        # AdministrativeMetadata
        admin_el = newscomponent_el.find('AdministrativeMetadata')
        self.parse_administrativemetadata(item, admin_el)

        # DescriptiveMetadata
        descript_el = newscomponent_el.find('DescriptiveMetadata')
        self.parse_descriptivemetadata(item, descript_el)

        # description_text, headline
        for formalname, item_key in (('Body', 'description_text'), ('Title', 'headline')):
            role = newscomponent_el.find('NewsComponent/Role[@FormalName="{}"]'.format(formalname))
            if role is not None:
                newscomponent = role.getparent()
                datacontent = newscomponent.find('ContentItem/DataContent')
                format = newscomponent.find('ContentItem/Format')

                if datacontent is not None and format is not None:
                    formalname = format.attrib.get('FormalName')
                    if not formalname or formalname not in ('Text', 'ascii'):
                        logger.warning(
                            'ContentItem/FormalName was not found or not supported: "{}". '
                            'Skiping an "{}" item.'.format(formalname, item['guid'])
                        )
                        raise SkipItemException
                    if datacontent.text:
                        item[item_key] = datacontent.text.strip()

                        if item_key == 'description_text':
                            item[item_key] = self._plain_to_html(item[item_key])
                else:
                    logger.warning('Mimetype or DataContent was not found. Skiping an "{}" item.'.format(
                        item['guid']
                    ))
                    raise SkipItemException

        # type
        role = newscomponent_el.find('Role')
        if role is not None:
            role_name = role.attrib.get('FormalName')
            if not role_name:
                logger.warning('NewsComponent/Role was not found. Skiping an "{}" item.'.format(
                    item['guid']
                ))
                raise SkipItemException
            role_name = role_name.upper()
            item[ITEM_TYPE] = getattr(CONTENT_TYPE, role_name)

        # read files and save them into the storage
        for newscomponent in newscomponent_el.findall('NewsComponent'):
            component_role = self._get_role(newscomponent)
            if component_role and component_role.upper() in self.SUPPORTED_MEDIA_ASSET_TYPES[role_name].keys():
                content_item = newscomponent.find('ContentItem')
                if content_item is None:
                    continue

                filename = content_item.attrib.get('Href')
                if filename is None:
                    continue

                format_name = ''
                format_el = content_item.find('Format')
                if format_el is not None:
                    format_name = format_el.attrib.get('FormalName')

                content = self._get_file(filename)
                if not content:
                    continue

                _, content_type, metadata = process_file_from_stream(content, 'application/' + format_name)
                content.seek(0)
                media_id = app.media.put(
                    content,
                    filename=filename,
                    content_type=content_type,
                    metadata=metadata
                )

                rendition_key = self.SUPPORTED_MEDIA_ASSET_TYPES[role_name][component_role.upper()]
                item.setdefault('renditions', {})[rendition_key] = {
                    'media': media_id,
                    'mimetype': content_type,
                    'href': app.media.url_for_media(media_id, content_type),
                }

        # this attibutes are redundand for media item
        attrs_to_be_removed = ('date_id', 'item_id', 'provider_id', 'public_identifier')
        for attr in attrs_to_be_removed:
            if attr in item:
                del item[attr]

        # clean subject
        subject_to_be_removed = (
            'genre',
        )
        item['subject'] = [i for i in item.get('subject', []) if i['scheme'] not in subject_to_be_removed]

    def parse_newslines(self, item, newslines_el):
        """Parse NewsLines in 2nd level NewsComponent element."""
        if newslines_el is None:
            return

        # dateline
        element = newslines_el.find('DateLine')
        if element is not None and element.text:
            self.set_dateline(item, text=element.text)

        # byline
        element = newslines_el.find('CreditLine')
        if element is not None and element.text:
            item['byline'] = element.text

        # headline
        element = newslines_el.find('HeadLine')
        if element is not None and element.text:
            item['headline'] = element.text.strip()

        # copyrightholder
        element = newslines_el.find('CopyrightLine')
        if element is not None and element.text:
            item['copyrightholder'] = element.text

        # line_type
        element = newslines_el.find('NewsLine/NewsLineType')
        if element is not None and element.get('FormalName'):
            item['line_type'] = element.get('FormalName')

        # line_text
        element = newslines_el.find('NewsLine/NewsLineText')
        if element is not None and element.text:
            item['line_text'] = element.text

        # belga-keywords
        for element in newslines_el.findall('KeywordLine'):
            if element is not None and element.text:
                belga_keywords = get_resource_service("vocabularies").get_items(
                    _id='belga-keywords',
                    name=element.text.strip(),
                    lang=item['language'],
                )

                try:
                    item.setdefault('subject', []).append(belga_keywords[0])
                except (StopIteration, IndexError) as e:
                    logger.error(e)

    def parse_administrativemetadata(self, item, admin_el):
        """Parse AdministrativeMetadata in 2nd level NewsComponent element."""
        if admin_el is None:
            return

        item['administrative'] = {}

        element = admin_el.find('Provider/Party')
        if element is not None and element.get('FormalName'):
            item['administrative']['provider'] = element.get('FormalName')

        self.parse_sources(item, admin_el)

        for element in admin_el.findall('Creator/Party'):
            if element is not None and element.get('FormalName'):
                author = {
                    'name': element.get('FormalName', '').replace(' ', ''),
                    'role': element.get('Topic', '')
                }
                # try to find an author in DB
                user = get_resource_service('users').find_one(req=None, username=author['name'])
                if user:
                    author['_id'] = [
                        str(user['_id']),
                        author['role'],
                    ]
                    author['sub_label'] = user.get('display_name', author['name'])
                    author['parent'] = str(user['_id'])
                    author['name'] = author['role']
                    item.setdefault('authors', []).append(author)

        element = admin_el.find('Contributor/Party')
        if element is not None and element.get('FormalName'):
            item['administrative']['contributor'] = element.get('FormalName')

        element = admin_el.find('Property[@FormalName="Validator"]')
        if element is not None and element.get('Value'):
            item['administrative']['validator'] = element.get('Value')

        element = admin_el.find('Property[@FormalName="ValidationDate"]')
        if element is not None and element.get('Value'):
            item['administrative']['validation_date'] = element.get('Value')

        element = admin_el.find('Property[@FormalName="ForeignId"]')
        if element is not None and element.get('Value'):
            item['administrative']['foreign_id'] = element.get('Value')

        # priority
        # urgency
        element = admin_el.find('Property[@FormalName="Priority"]')
        if element is not None and element.get('Value'):
            try:
                item['priority'] = int(element.get('Value'))
            except ValueError:
                item['priority'] = element.get('Value')
            item['urgency'] = item['priority']

        # source
        element = admin_el.find('Source/Party')
        if element is not None and element.get('FormalName'):
            item['source'] = element.get('FormalName')

        # services-products CV
        for news_package_elem in admin_el.findall('Property[@FormalName="NewsPackage"]'):
            news_service = news_package_elem.find('Property[@FormalName="NewsService"]')
            news_product = news_package_elem.find('Property[@FormalName="NewsProduct"]')
            if news_service is not None and news_product is not None:
                qcode = '{}/{}'.format(news_service.get('Value'), news_product.get('Value'))
                item.setdefault('subject', []).append({
                    'name': qcode,
                    'qcode': qcode,
                    'parent': news_service.get('Value'),
                    'scheme': 'services-products'
                })

        # label CV
        for element in admin_el.findall('Property[@FormalName="Label"]'):
            if element is not None and element.get('Value'):
                item.setdefault('subject', []).append({
                    "name": element.get('Value'),
                    "qcode": element.get('Value'),
                    "scheme": "label"
                })

        # slugline
        element = admin_el.find('Property[@FormalName="Topic"]')
        if element is not None and element.get('Value'):
            item['slugline'] = element.get('Value')

        # editorial note
        element = admin_el.find('Property[@FormalName="EditorialInfo"]')
        if element is not None and element.get('Value'):
            item['ednote'] = element.get('Value')

    def parse_descriptivemetadata(self, item, descript_el):
        """
        Parse DescriptiveMetadata in NewsComponent element.

        Example:

        <DescriptiveMetadata DateAndTime="20190213T184245">
          <SubjectCode>
            <Subject FormalName="11"/>
          </SubjectCode>
          <Location>
            <Property FormalName="City" Value="NAMUR"/>
            <Property FormalName="Country" Value="BELGIUM"/>
            <Property FormalName="CountryArea"/>
            <Property FormalName="SubLocation"/>
            <Property FormalName="WorldRegion"/>
          </Location>
        </DescriptiveMetadata>

        :param item:
        :param descript_el:
        :return:
        """
        if descript_el is None:
            return

        location_el = descript_el.find('Location')
        if location_el is not None:
            elements = location_el.findall('Property')
            for element in elements:
                # country
                if element.attrib.get('FormalName', '') == 'Country' and element.attrib.get('Value'):
                    countries = get_resource_service('vocabularies').get_items(
                        _id='countries',
                        name=element.attrib.get('Value'),
                        lang=item['language']
                    )
                    try:
                        item.setdefault('subject', []).append(countries[0])
                    except (StopIteration, IndexError) as e:
                        logger.error(e)
                # city
                if element.attrib.get('FormalName', '') == 'City' and element.attrib.get('Value'):
                    item.setdefault('extra', {})['city'] = element.attrib.get('Value')

    def parse_attachments(self, news_component_1):
        attachments = []
        for news_component_2 in news_component_1.findall('NewsComponent'):
            role_name = self._get_role(news_component_2)
            if role_name and role_name.upper() not in self.SUPPORTED_TEXT_ASSET_TYPES:
                for newscomponent in news_component_2.findall('NewsComponent'):
                    component_role = self._get_role(newscomponent)
                    if component_role and component_role.upper() in self.SUPPORTED_BINARY_ASSET_SUBTYPES:
                        attachment = self.parse_attachment(newscomponent)
                        if attachment:
                            attachments.append(attachment)
                # remove element to avoid parsing it as news item
                news_component_1.remove(news_component_2)
        if attachments:
            return {
                'attachments': attachments,
                'ednote': 'The story has {} attachment(s)'.format(len(attachments)),
            }
        return {}

    def parse_attachment(self, newscomponent_el):
        """
        Parse attachment component, save it to storage and return attachment id

        <NewsComponent Duid="0" xml:lang="nl">
            <Role FormalName="Image"/>
            <DescriptiveMetadata>
                <Property FormalName="ComponentClass" Value="Image"/>
            </DescriptiveMetadata>
            <ContentItem Href="IMG_0182.jpg">
                <Format FormalName="Jpeg"/>
                <Characteristics>
                    <SizeInBytes>2267043</SizeInBytes>
                    <Property FormalName="Width" Value="4032"/>
                    <Property FormalName="Height" Value="3024"/>
                </Characteristics>
            </ContentItem>
        </NewsComponent>
        """
        content_item = newscomponent_el.find('ContentItem')
        if content_item is None:
            return

        # avoid re-adding media after item is ingested
        guid = hashlib.md5(ElementTree.tostring(content_item)).hexdigest()
        attachment_service = get_resource_service('attachments')
        old_attachment = attachment_service.find_one(req=None, guid=guid)
        if old_attachment:
            return {'attachment': old_attachment['_id']}

        filename = content_item.attrib.get('Href')
        if filename is None:
            return

        format_name = ''
        format_el = content_item.find('Format')
        if format_el is not None:
            format_name = format_el.attrib.get('FormalName')

        content = self._get_file(filename)
        if not content:
            return
        _, content_type, metadata = process_file_from_stream(content, 'application/' + format_name)
        content.seek(0)
        media_id = app.media.put(content,
                                 filename=filename,
                                 content_type=content_type,
                                 metadata=metadata,
                                 resource='attachments')
        try:
            ids = attachment_service.post([{
                'media': media_id,
                'filename': filename,
                'title': filename,
                'description': 'belga remote attachment',
                'guid': guid,
            }])
            return {'attachment': next(iter(ids), None)}
        except Exception as ex:
            app.media.delete(media_id)

    def parse_sources(self, item, admin_el):
        names = []
        source = admin_el.find('Source/Party')
        if source is not None and source.get('FormalName'):
            names.extend(source.get('FormalName').split('/'))
        if not names:
            names.append('BELGA')
        sources = get_resource_service('vocabularies').get_items('sources')
        for source in sources:
            if source['name'] in names:
                item.setdefault('subject', []).append(source)

    def _get_role(self, newscomponent_el):
        role = newscomponent_el.find('Role')
        if role is not None:
            return role.attrib.get('FormalName')

    def _get_file(self, filename):
        config = self._provider.get('config', {})
        path = config.get('path', '')
        file_dir = os.path.join(path, 'attachments')
        file_path = os.path.join(file_dir, filename)
        try:
            if self._provider.get('feeding_service') == 'ftp':
                file_path = self._download_file(filename, file_path, config)
            with open(file_path, 'rb') as f:
                content = f.read()
                if self.MOVE_FILE:
                    self._move_file(file_dir, filename, config)
                return BytesIO(content)
        except (FileNotFoundError, error_perm) as e:
            logger.warning('File %s not found', file_path)
        except Exception as e:
            logger.error(e)

    def _download_file(self, filename, file_path, config):
        tmp_dir = os.path.join(gettempdir(), filename)
        with ftp_connect(config) as ftp, open(tmp_dir, 'wb') as f:
            ftp.retrbinary('RETR ' + file_path, f.write)
            return tmp_dir

    def _move_file(self, file_dir, filename, config):
        if self._provider.get('feeding_service') == 'ftp':
            with ftp_connect(config) as ftp:
                if config.get('move', False):
                    ftp_service = FTPFeedingService()
                    move_path, _ = ftp_service._create_move_folders(config, ftp)
                    ftp_service._move(
                        ftp, os.path.join(file_dir, filename), os.path.join(move_path, filename),
                        datetime.now(), False
                    )
        else:
            file_service = FileFeedingService()
            # move processed attachments to the same folder with XML
            file_dir = os.path.dirname(file_dir)
            file_service.move_file(file_dir, 'attachments/' + filename, self._provider)


register_feed_parser(BelgaNewsMLOneFeedParser.NAME, BelgaNewsMLOneFeedParser())
