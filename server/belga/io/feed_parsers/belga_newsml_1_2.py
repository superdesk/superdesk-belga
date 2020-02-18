# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

import logging
from copy import deepcopy
from superdesk.errors import ParserError
from superdesk.io.registry import register_feed_parser
from superdesk.publish.formatters.newsml_g2_formatter import XML_LANG
from superdesk.utc import local_to_utc
from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser, SkipItemException


logger = logging.getLogger(__name__)


class BelgaNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser which can parse specific Belga News ML xml files."""

    NAME = 'belganewsml12'

    label = 'Belga News ML 1.2 Parser'

    SUPPORTED_ASSET_TYPES = ('ALERT', 'SHORT', 'TEXT', 'BRIEF')

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
        try:
            self.root = xml
            self._items = []
            self._item_seed = {}

            # parser the NewsEnvelope element
            self._item_seed.update(
                self.parser_newsenvelop(xml.find('NewsEnvelope'))
            )

            # parser the NewsItem element
            for newsitem_el in xml.findall('NewsItem'):
                try:
                    self.parser_newsitem(newsitem_el)
                except SkipItemException:
                    continue
                # l_item.append(item)
            return self._items

        except Exception as ex:
            raise ParserError.newsmlOneParserError(ex, provider)

    def parser_newsenvelop(self, envelop_el):
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

    def parser_newsitem(self, newsitem_el):
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
            self.parser_identification(newsitem_el.find('Identification'))
        )

        # NewsManagement
        self._item_seed.update(
            self.parser_newsmanagement(newsitem_el.find('NewsManagement'))
        )

        # NewsComponent
        news_component_1 = newsitem_el.find('NewsComponent')
        if news_component_1 is not None:
            # Genre from NewsComponent 1st level
            for element in news_component_1.findall('DescriptiveMetadata/Genre'):
                if element.get('FormalName'):
                    # genre CV
                    self._item_seed.setdefault('subject', []).append({
                        "name": element.get('FormalName'),
                        "qcode": element.get('FormalName'),
                        "scheme": "genre"
                    })

            # NewsComponent 2nd level
            # NOTE: each NewsComponent of 2nd level is a separate item with unique GUID
            for news_component_2 in news_component_1.findall('NewsComponent'):
                # guid
                guid = news_component_2.attrib.get('Duid')
                if guid is None:
                    continue

                # create an item
                # deepcopy to avoid having a pointer to `subject`
                item = deepcopy({**self._item_seed, 'guid': guid})

                # NewsComponent
                try:
                    self.parser_newscomponent(item, news_component_2)
                except SkipItemException:
                    continue

                # type
                self.populate_fields(item)

                self._items.append(item)

    def parser_identification(self, indent_el):
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
                version = int(element.text)
                if version == 0:
                    version = 1
                identification['version'] = version

            element = newsident_el.find('PublicIdentifier')
            if element is not None:
                # public_identifier
                identification['public_identifier'] = element.text

        return identification

    def parser_newsmanagement(self, manage_el):
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

        element = manage_el.find('NewsItemType')
        if element is not None and element.get('FormalName'):
            # news_item_types CV
            newsmanagement.setdefault('subject', []).append({
                "name": element.get('FormalName'),
                "qcode": element.get('FormalName'),
                "scheme": "news_item_types"
            })

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

    def parser_newscomponent(self, item, newscomponent_el):
        """
        Parse NewsComponent in NewsItem element.

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
            if not (role_name and role_name.upper() in self.SUPPORTED_ASSET_TYPES):
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
        self.parser_newslines(item, newslines_el)

        # AdministrativeMetadata
        admin_el = newscomponent_el.find('AdministrativeMetadata')
        self.parser_administrativemetadata(item, admin_el)

        # DescriptiveMetadata
        descript_el = newscomponent_el.find('DescriptiveMetadata')
        self.parser_descriptivemetadata(item, descript_el)

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

        return item

    def parser_newslines(self, item, newslines_el):
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

        # keywords
        for element in newslines_el.findall('KeywordLine'):
            if element is not None and element.text:
                item.setdefault('keywords', []).append(element.text)

    def parser_administrativemetadata(self, item, admin_el):
        """Parse AdministrativeMetadata in 2nd level NewsComponent element."""
        if admin_el is None:
            return

        item['administrative'] = {}

        element = admin_el.find('Provider/Party')
        if element is not None and element.get('FormalName'):
            item['administrative']['provider'] = element.get('FormalName')

        for element in admin_el.findall('Creator/Party'):
            if element is not None and element.get('FormalName'):
                item.setdefault('authors', []).append({
                    'name': element.get('FormalName'),
                    'role': element.get('Topic', '')
                })

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

    def parser_descriptivemetadata(self, item, descript_el):
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
                    item.setdefault('extra', {})['country'] = element.attrib.get('Value')
                # city
                if element.attrib.get('FormalName', '') == 'City' and element.attrib.get('Value'):
                    item.setdefault('extra', {})['city'] = element.attrib.get('Value')


register_feed_parser(BelgaNewsMLOneFeedParser.NAME, BelgaNewsMLOneFeedParser())
