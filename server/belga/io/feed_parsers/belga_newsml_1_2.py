# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

import datetime

from superdesk.errors import ParserError
from superdesk.etree import etree
from superdesk.io.feed_parsers.newsml_1_2 import NewsMLOneFeedParser
from superdesk.io.iptc import subject_codes
from superdesk.io.registry import register_feed_parser


class BelgaNewsMLOneFeedParser(NewsMLOneFeedParser):
    """Feed Parser which can parse if the feed is in NewsML format, specific AFP, ANP, .. Belga xml."""

    NAME = 'belganewsml12'

    label = 'Belga News ML 1.2 Parser'

    def can_parse(self, xml):
        """
        Check NewsML type for file.

        :param xml:
        :return:
        """
        return xml.tag == 'NewsML'

    def parse(self, xml, provider=None):
        """
        Parser content the xml newsml file to json object.

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
            l_item = []
            self.root = xml

            # parser the NewsEnvelope element
            item_envelop = self.parser_newsenvelop(xml.find('NewsEnvelope'))

            # parser the NewsItem element
            l_newsitem_el = xml.findall('NewsItem')
            for newsitem_el in l_newsitem_el:
                item = item_envelop.copy()
                self.parser_newsitem(item, newsitem_el)
                l_item.append(self.populate_fields(item))
            return l_item

        except Exception as ex:
            raise ParserError.BelganewsmlOneParserError(ex, provider)

    def parser_newsenvelop(self, envelop_el):
        """
        Function parser Identification element.

        Example:

         <NewsEnvelope >
            <TransmissionId>0421</TransmissionId>
            <DateAndTime>20181209T112417Z</DateAndTime>
            <NewsService FormalName="DGTE"/>
            <NewsProduct FormalName="DAB"/>
            <NewsProduct FormalName="AMW"/>
            <Priority FormalName="4"/>
          </NewsEnvelope>

        :param envelop_el:
        :return:
        """
        if envelop_el is None:
            return {}
        item = {}
        element = envelop_el.find('TransmissionId')
        if element is not None:
            item['ingest_provider_sequence'] = element.text

        element = envelop_el.find('NewsService')
        if element is not None:
            item['service'] = element.get('FormalName', '')

        elements = envelop_el.findall('NewsProduct')
        if elements is not None:
            item['products'] = []
            for element in elements:
                item['products'].append(element.get('FormalName', ''))

        element = envelop_el.find('Priority')
        if element is not None:
            item['priority'] = element.get('FormalName', 0)

        # EFE
        sentfrom_el = envelop_el.find('SentFrom')
        if sentfrom_el is not None:
            comment_el = sentfrom_el.find('Comment')
            item['sentfrom'] = {}

            if comment_el is not None:
                item['sentfrom']['comment'] = comment_el.text

            party_el = sentfrom_el.find('Party')
            if party_el is not None:
                item['sentfrom']['party'] = party_el.get('FormalName', '')

                element = party_el.find('Property')
                if element is not None:
                    if element.attrib.get('FormalName', '') == 'Organization':
                        item['sentfrom']['organization'] = element.attrib['Value']

        return item

    def parser_newsitem(self, item, newsitem_el):
        """
        Function parser Newsitem element.

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
        if newsitem_el.attrib.get('Duid', '') != '':
            item['duid'] = newsitem_el.attrib.get('Duid', '')

        if newsitem_el.attrib.get('LinkType', '') != '':
            item['link_type'] = newsitem_el.attrib.get('LinkType', '')

        element = newsitem_el.find('Comment')
        if element is not None:
            item['comment'] = {}

            item['comment']['version'] = element.text
            if element.get('FormalName', '') is not None:
                item['comment']['name'] = element.get('FormalName', '')

        # Parser Identification element
        self.parser_identification(item, newsitem_el.find('Identification'))

        # Parser NewsManagement element
        self.parser_newsmanagement(item, newsitem_el.find('NewsManagement'))

        # Parser NewsComponent element
        component_parent = newsitem_el.find('NewsComponent')
        # if have a child NewsComponent, run the parser for TASS xml file.
        if component_parent is not None:
            if component_parent.attrib.get('Duid', '') is not None:
                item['news_component_duid'] = component_parent.attrib.get('Duid', '')

            if component_parent.attrib.get('Essential', '') is not None:
                item['news_component_essential'] = component_parent.attrib.get('Essential', '')

            if component_parent.attrib.get('EquivalentsList', '') is not None:
                item['news_component_equivalentslist'] = component_parent.attrib.get('EquivalentsList', '')

            component_child = component_parent.find('NewsComponent')
            if component_child is not None:
                self.parser_newscomponent(item, component_child.find('NewsComponent'))
            else:
                self.parser_newscomponent(item, component_parent)

    def parser_identification(self, item, indent_el):
        """
        Function parse Identification in NewsItem element.

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
        :return:
        """
        if indent_el is None:
            return

        newsident_el = indent_el.find('NewsIdentifier')
        if newsident_el is not None:
            element = newsident_el.find('ProviderId')
            if element is not None:
                item['provide_id'] = element.text

            element = newsident_el.find('DateId')
            if element is not None:
                item['date_id'] = element.text

            element = newsident_el.find('NewsItemId')
            if element is not None:
                item['item_id'] = element.text

            element = newsident_el.find('RevisionId')
            if element is not None:
                item['version'] = element.text

            element = newsident_el.find('PublicIdentifier')
            if element is not None:
                item['guid'] = element.text

        element = indent_el.find('NameLabel')
        if element is not None:
            item['label'] = element.text

        # ANP
        element = indent_el.find('DateLabel')
        if element is not None:
            item['date_label'] = element.text

        return

    def parser_newsmanagement(self, item, manage_el):
        """
        Function parser NewsManagement in NewsItem element.

        Example:

        <NewsManagement>
          <NewsItemType FormalName="News"/>
          <FirstCreated>20181209T112417+0000</FirstCreated>
          <ThisRevisionCreated>20181209T112417+0000</ThisRevisionCreated>
          <Status FormalName="Usable"/>
          <Urgency FormalName="4"/>
          <AssociatedWith NewsItem="urn:newsml:afp.com:20181209T112417Z:doc-1bg5v6"/>
          <AssociatedWith FormalName="Photo"/>
          <AssociatedWith FormalName="LIVEVIDEO"/>
          <AssociatedWith FormalName="Video"/>
        </NewsManagement>

        :param item:
        :param manage_el:
        :return:
        """
        if manage_el is None:
            return

        element = manage_el.find('NewsItemType')
        if element is not None:
            item['item_type'] = element.get('FormalName', '')

        element = manage_el.find('FirstCreated')
        if element is not None:
            item['firstcreated'] = self.datetime(element.text)

        element = manage_el.find('ThisRevisionCreated')
        if element is not None:
            item['versioncreated'] = self.datetime(element.text)

        element = manage_el.find('Status')
        if element is not None:
            item['status'] = element.get('FormalName', '')

        element = manage_el.find('Urgency')
        if element is not None:
            item['urgency'] = element.get('FormalName', '')

        # parser AssociatedWith element
        elements = manage_el.findall('AssociatedWith')
        if elements:
            item['associated_with'] = {}
            for element in elements:
                data = element.get('NewsItem', '')
                item['associated_with']['item'] = data if data else None
                data = element.get('FormalName')
                if data:
                    if 'type' in item['associated_with']:
                        item['associated_with']['type'].append(data)
                    else:
                        item['associated_with']['type'] = [data]

    def parser_newscomponent(self, item, component_el):
        """
            Function parser NewsComponent in NewsItem element.

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
        if component_el is None:
            return

        if component_el.attrib.get('Duid', '') is not None:
            item['news_component_duid'] = component_el.attrib.get('Duid', '')

        if component_el.attrib.get('Essential', '') is not None:
            item['news_component_essential'] = component_el.attrib.get('Essential', '')

        if component_el.attrib.get('EquivalentsList', '') is not None:
            item['news_component_equivalentslist'] = component_el.attrib.get('EquivalentsList', '')

        role = component_el.find('Role')
        if role is not None:
            if role.attrib.get('FormalName', ''):
                item['role'] = role.attrib.get('FormalName', '')

        newslines_el = component_el.find('NewsLines')
        if newslines_el is not None:
            element = newslines_el.find('DateLine')
            if element is not None:
                self.set_dateline(item, text=element.text)

            element = newslines_el.find('HeadLine')
            if element is not None:
                item['headline'] = element.text

            element = newslines_el.find('NewsLine/NewsLineType')
            if element is not None:
                item['line_type'] = element.get('FormalName', '')

            element = newslines_el.find('NewsLine/NewsLineText')
            if element is not None:
                item['line_text'] = element.text

            # ANP
            element = newslines_el.find('SubHeadLine')
            if element is not None:
                item['sub_head_line'] = element.text

            element = newslines_el.find('ByLine')
            if element is not None:
                item['by_line'] = element.text

            element = newslines_el.find('ByLineTitle')
            if element is not None:
                item['by_line_title'] = element.text

            element = newslines_el.find('DateLine')
            if element is not None:
                item['date_line'] = element.text

            element = newslines_el.find('CopyrightLine')
            if element is not None:
                item['copyright_line'] = element.text

            element = newslines_el.find('SlugLine')
            if element is not None:
                item['slug_line'] = element.text

            element = newslines_el.find('KeywordLine')
            if element is not None:
                item['keyword_line'] = element.text
                # ANP

        admin_el = component_el.find('AdministrativeMetadata')
        if admin_el is not None:
            item['administrative'] = {}

            element = admin_el.find('Provider/Party')
            if element is not None:
                item['administrative']['provider'] = element.get('FormalName', '')

            element = admin_el.find('Creator/Party')
            if element is not None:
                item['administrative']['creator'] = element.get('FormalName', '')

        # parser DescriptiveMetadata element
        if component_el.find('DescriptiveMetadata') is not None:
            self.parser_descriptivemetadata(item, component_el.find('DescriptiveMetadata'))
        else:
            self.parser_descriptivemetadata(item, component_el.find('DescriptiveMetada'))

        # parser ContentItem element
        self.parser_contentitem(item, component_el.find('ContentItem'))

        # parser OfInterestTo element
        keywords = component_el.find('item_keywords')
        if keywords is not None:
            elements = keywords.findall('item_keyword')

            if elements is not None:
                item['item_keywords'] = []
                for element in elements:
                    item['item_keywords'].append(element.text)

    def parser_descriptivemetadata(self, item, descript_el):
        """
        Function parser DescriptiveMetadata in NewsComponent element.

        Example:

        <DescriptiveMetadata>
            <Language FormalName="fr"/>
            <SubjectCode>
              <SubjectMatter FormalName="01011000" cat="CLT"/>
            </SubjectCode>
            <SubjectCode>
              <Subject FormalName="01000000" cat="CLT"/>
            </SubjectCode>
            <SubjectCode>
              <SubjectDetail FormalName="08003002" cat="HUM"/>
            </SubjectCode>
            <OfInterestTo FormalName="DAB-TFG-1=DAB"/>
            <OfInterestTo FormalName="AMN-TFG-1=AMW"/>
            <DateLineDate>20181209T112417+0000</DateLineDate>
            <Location HowPresent="Origin">
              <Property FormalName="Country" Value="FRA"/>
              <Property FormalName="City" Value="Paris"/>
            </Location>
            <Property FormalName="GeneratorSoftware" Value="libg2"/>
            <Property FormalName="Keyword" Value="musique"/>
            <Property FormalName="Keyword" Value="rock"/>
        </DescriptiveMetadata>

        :param item:
        :param descript_el:
        :return:
        """
        if descript_el is None:
            return

        element = descript_el.find('Language')
        if element is not None:
            item['language'] = element.get('FormalName', '')

        elements = descript_el.findall('Genre')
        if elements is not None:
            item['genre'] = []
            for element in elements:
                item['genre'].append({'name': element.get('FormalName')})

        element = descript_el.find('guid')
        if element is not None:
            if 'guid' not in item:
                item['guid'] = element.text
            else:
                item['descriptive_guid'] = element.text

        # parser SubjectCode element
        subjects = descript_el.findall('SubjectCode/SubjectDetail')
        subjects += descript_el.findall('SubjectCode/SubjectMatter')
        subjects += descript_el.findall('SubjectCode/Subject')
        item['subject'] = self.format_subjects(subjects)

        # parser OfInterestTo element
        elements = descript_el.findall('OfInterestTo')
        if elements:
            item['OfInterestTo'] = []
            for element in elements:
                item['OfInterestTo'].append(element.get('FormalName', ''))

        element = descript_el.find('DateLineDate')
        if element is not None:
            if 'dayline' in item:
                item['dateline']['date'] = self.datetime(element.text)
            else:
                item['dateline'] = {}
                item['dateline']['date'] = self.datetime(element.text)

        location_el = descript_el.find('Location')
        if location_el is not None:
            item['location'] = {}

            how_present_el = location_el.get('HowPresent', '')
            if how_present_el is not None:
                item['location']['how_present_el'] = how_present_el

            elements = location_el.findall('Property')
            for element in elements:
                if element.attrib.get('FormalName', '') == 'Country':
                    item['location']['country'] = element.attrib['Value']
                if element.attrib.get('FormalName', '') == 'City':
                    item['location']['city'] = element.attrib['Value']

        elements = descript_el.findall('Property')
        for element in elements:
            if element.attrib.get('FormalName', '') == 'GeneratorSoftware':
                item['generator_software'] = element.attrib['Value']

            if element.attrib.get('FormalName', '') == 'Tesauro':
                item['tesauro'] = element.attrib['Value']

            if element.attrib.get('FormalName', '') == 'EfePais':
                item['efe_pais'] = element.attrib['Value']

            if element.attrib.get('FormalName', '') == 'EfeRegional':
                item['efe_regional'] = element.attrib['Value']

            if element.attrib.get('FormalName', '') == 'EfeComplemento':
                item['efe_complemento'] = element.attrib['Value']

            if element.attrib.get('FormalName', '') == 'Keyword':
                data = element.attrib['Value']
                if 'keywords' in item:
                    item['keywords'].append(data)
                else:
                    item['keywords'] = [data]

    def parser_contentitem(self, item, content_el):
        """
        Function parser DescriptiveMetadata in NewsComponent element.

        Example:
        <ContentItem>
            <MediaType FormalName="Text"/>
            <Format FormalName="NITF3.1"/>
            <Characteristics>
              <SizeInBytes>2520</SizeInBytes>
              <Property FormalName="Words" Value="420"/>
            </Characteristics>
            <DataContent>
              <nitf>
                <body>
                  <body.content>
                    <p>Un an après la mort de Johnny Hallyday, plus d'un millier de fans sont venus assister dimanche
                    <p>A l'intérieur de l'église, plus d'un millier de personnes étaient réunies pour assister à une
                    <p>
                      <org idsrc="isin" value="US38259P5089">GOOGLE</org>
                    </p>
                  </body.content>
                </body>
              </nitf>
            </DataContent>
        </ContentItem>

        :param item:
        :param content_el:
        :return:
        """
        if content_el is None:
            return

        element = content_el.find('MediaType')
        if element is not None:
            item['media_type'] = element.get('FormalName', '')

        element = content_el.find('MimeType')
        if element is not None:
            item['mime_type'] = element.get('FormalName', '')

        element = content_el.find('Format')
        if element is not None:
            item['format'] = element.get('FormalName', '')

        character_el = content_el.find('Characteristics')
        if character_el is not None:
            item['characteristics'] = {}
            element = character_el.find('SizeInBytes')
            if element is not None:
                item['characteristics']['size_bytes'] = element.text
            elements = character_el.findall('Property')
            for element in elements:
                if element.attrib.get('FormalName') == 'Words':
                    item['characteristics']['word_count'] = element.attrib['Value']
                if element.attrib.get('FormalName') == 'SizeInBytes':
                    item['characteristics']['size_bytes'] = element.attrib['Value']
                if element.attrib.get('FormalName') == 'Creator':
                    item['characteristics']['creator'] = element.attrib['Value']
                if element.attrib.get('FormalName') == 'Characters':
                    item['characteristics']['characters'] = element.attrib['Value']

        if content_el.find('DataContent/nitf/body/body.content') is not None:
            item['body_html'] = etree.tostring(content_el.find('DataContent/nitf/body/body.content'),
                                               encoding='unicode').replace('<body.content>', '').replace(
                '</body.content>', '')

        if content_el.find('DataContent/nitf/head') is not None:
            item['header_content'] = etree.tostring(content_el.find('DataContent/nitf/head'), encoding='unicode')

        if content_el.find('DataContent/nitf/body/body.head') is not None:
            item['body_head'] = etree.tostring(content_el.find('DataContent/nitf/body/body.head'), encoding='unicode')

    def datetime(self, string):
        l_format_dt = ['%Y%m%dT%H%M%S%z', '%Y%m%dT%H%M%S', '%Y%m%dT%H%M%SZ']
        for format_dt in l_format_dt:
            converted_dt = self.valid_datetime(string, format_dt)
            if converted_dt:
                return converted_dt
        return None

    def valid_datetime(self, string, format_datetime):
        try:
            return datetime.datetime.strptime(string, format_datetime)
        except ValueError:
            return None

    def format_subjects(self, subjects):
        """Map the ingested Subject Codes to their corresponding names as per IPTC Specification.

        :param subjects: list of dicts where each dict gives the category the article is mapped to.
        :type subjects: list
        :returns [{"qcode": "01001000", "name": "archaeology"}, {"qcode": "01002000", "name": "architecture"}]
        :rtype list
        """
        formatted_subjects = []

        def is_not_formatted(qcode):
            for formatted_subject in formatted_subjects:
                if formatted_subject['qcode'] == qcode:
                    return False

            return True

        for subject in subjects:
            formal_name = subject.get('FormalName')
            scheme = subject.get('Scheme', '')
            if formal_name and is_not_formatted(formal_name):
                formatted_subjects.append(
                    {'qcode': formal_name, 'name': subject_codes.get(formal_name, ''), 'scheme': scheme})

        return formatted_subjects


register_feed_parser(BelgaNewsMLOneFeedParser.NAME, BelgaNewsMLOneFeedParser())
