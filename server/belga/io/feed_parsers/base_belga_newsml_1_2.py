# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

import itertools
import html
import datetime
import superdesk
from superdesk.errors import ParserError
from superdesk.etree import etree
from superdesk.io.feed_parsers.newsml_1_2 import NewsMLOneFeedParser
from superdesk.io.iptc import subject_codes

from .belga_newsml_mixin import BelgaNewsMLMixin


class SkipItemException(Exception):
    """Raised when we current item must be skipped"""

    pass


class BaseBelgaNewsMLOneFeedParser(BelgaNewsMLMixin, NewsMLOneFeedParser):
    """Base Feed Parser for NewsML format, specific AFP, ANP, .. Belga xml."""

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
            items = []
            self.root = xml

            # parser the NewsEnvelope element
            item_envelop = self.parse_newsenvelop(xml.find('NewsEnvelope'))

            # parser the NewsItem element
            l_newsitem_el = xml.findall('NewsItem')
            for newsitem_el in l_newsitem_el:
                try:
                    item = item_envelop.copy()
                    self.parse_newsitem(item, newsitem_el)
                    # add product is NEWS/GENERAL, if product is empty
                    if not [it for it in item.get('subject', []) if it.get('scheme') == 'services-products']:
                        item.setdefault('subject', []).append({
                            'name': 'NEWS/GENERAL',
                            'qcode': 'NEWS/GENERAL',
                            'parent': 'NEWS',
                            'scheme': 'services-products'
                        })
                    # Distribution is default
                    item.setdefault('subject', []).extend([
                        {"name": 'default', "qcode": 'default', "scheme": "distribution"},
                    ])
                    # Slugline and keywords is epmty
                    item['slugline'] = None
                    item['keywords'] = []
                    # remove duplicated subject
                    item['subject'] = [
                        dict(i) for i, _ in itertools.groupby(sorted(item['subject'], key=lambda k: k['name']))
                    ]
                    item = self.populate_fields(item)
                except SkipItemException:
                    continue
                items.append(item)
            return items

        except Exception as ex:
            raise ParserError.newsmlOneParserError(ex, provider)

    def parse_newsenvelop(self, envelop_el):
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

        element = envelop_el.find('Priority')
        if element is not None:
            item['priority'] = int(element.get('FormalName', 0))

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
                        item['sentfrom']['organization'] = element.attrib.get('Value')

        return item

    def parse_newsitem(self, item, newsitem_el):
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

        # LinkType is CV
        link_type = newsitem_el.attrib.get('LinkType', '')
        if link_type != '':
            item.setdefault('subject', []).append({
                "name": link_type,
                "qcode": link_type,
                "scheme": "link_type"
            })

        element = newsitem_el.find('Comment')
        if element is not None:
            item['comment'] = {}

            item['comment']['version'] = element.text
            if element.get('FormalName', '') is not None:
                item['comment']['name'] = element.get('FormalName', '')

        # Parser Identification element
        self.parse_identification(item, newsitem_el.find('Identification'))

        # Parser NewsManagement element
        self.parse_newsmanagement(item, newsitem_el.find('NewsManagement'))

        # Parser NewsComponent element
        component_parent = newsitem_el.find('NewsComponent')
        if component_parent is not None:
            self.parse_newscomponent(item, component_parent)

    def parse_identification(self, item, indent_el):
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
                item['provider_id'] = element.text

            element = newsident_el.find('DateId')
            if element is not None:
                item['date_id'] = element.text

            element = newsident_el.find('NewsItemId')
            if element is not None:
                item["guid"] = item["item_id"] = element.text

            element = newsident_el.find('RevisionId')
            if element is not None:
                item['version'] = element.text

            element = newsident_el.find('PublicIdentifier')
            if element is not None:
                item['guid'] = element.text

        element = indent_el.find('NameLabel')
        if element is not None and element.text:
            item.setdefault('subject', []).append({
                "name": element.text,
                "qcode": element.text,
                "scheme": "label"
            })

        # ANP
        element = indent_el.find('DateLabel')
        if element is not None:
            item['date_label'] = element.text

    def parse_newsmanagement(self, item, manage_el):
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

        element = manage_el.find('FirstCreated')
        if element is not None:
            item['firstcreated'] = self.datetime(element.text)

        element = manage_el.find('ThisRevisionCreated')
        if element is not None:
            item['versioncreated'] = self.datetime(element.text)

        element = manage_el.find('Status')
        if element is not None:
            item['pubstatus'] = str.lower(element.get('FormalName', ''))

        element = manage_el.find('Urgency')
        if element is not None:
            item['urgency'] = element.get('FormalName', '')
            if item['urgency'] == '':
                item['urgency'] = element.text
            item['urgency'] = int(item['urgency'])

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

    def parse_newscomponent(self, item, component_el):
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

        if component_el.attrib.get('Duid') is not None and "guid" not in item:
            item['guid'] = component_el.attrib.get('Duid', '')

        # Essential is CV
        essential = component_el.attrib.get('Essential')
        if essential:
            item.setdefault('subject', []).append({
                "name": essential,
                "qcode": essential,
                "scheme": "essential"
            })

        # EquivalentsList is CV
        equivalents_list = component_el.attrib.get('EquivalentsList')
        if equivalents_list:
            item.setdefault('subject', []).append({
                "name": equivalents_list,
                "qcode": equivalents_list,
                "scheme": "equivalents_list"
            })

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
                item['byline'] = element.text

            element = newslines_el.find('ByLineTitle')
            if element is not None:
                item['by_line_title'] = element.text

            element = newslines_el.find('CopyrightLine')
            if element is not None:
                item['copyright_line'] = element.text

            element = newslines_el.find('SlugLine')
            if element is not None:
                item['slugline'] = element.text

            element = newslines_el.find('KeywordLine')
            if element is not None:
                item['keyword_line'] = element.text

        admin_el = component_el.find('AdministrativeMetadata')
        if admin_el is not None:
            item['administrative'] = {}

            element = admin_el.find('Provider/Party')
            if element is not None:
                item['administrative']['provider'] = element.get('FormalName', '')

            element = admin_el.find('Creator/Party')
            if element is not None:
                item['administrative']['creator'] = element.get('FormalName', '')

            element = admin_el.find('Source/Party')
            if element is not None:
                item['administrative']['source'] = element.get('FormalName', '')

        # parser DescriptiveMetadata element
        if component_el.find('DescriptiveMetadata') is not None:
            self.parse_descriptivemetadata(item, component_el.find('DescriptiveMetadata'))
        else:
            self.parse_descriptivemetadata(item, component_el.find('DescriptiveMetada'))

        # parser ContentItem element
        self.parse_contentitem(item, component_el.find('ContentItem'))

        # parser item_keywords element
        keywords = component_el.find('item_keywords')
        if keywords is not None:
            elements = keywords.findall('item_keyword')

            if elements is not None:
                item['keywords'] = []
                for element in [e for e in elements if e.text]:
                    item['keywords'].append(element.text)

    def parse_descriptivemetadata(self, item, descript_el):
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

        for element in descript_el.findall('Genre'):
            if element is not None and element.get('FormalName'):
                # genre CV
                item.setdefault('subject', []).append({
                    "name": element.get('FormalName'),
                    "qcode": element.get('FormalName'),
                    "scheme": "genre"
                })

        element = descript_el.find('guid')
        if element is not None:
            item['descriptive_guid'] = element.text

        # parser SubjectCode element
        subjects = descript_el.findall('SubjectCode/SubjectDetail')
        subjects += descript_el.findall('SubjectCode/SubjectMatter')
        subjects += descript_el.findall('SubjectCode/Subject')
        item.setdefault('subject', []).extend(self.format_subjects(subjects))
        for subject in subjects:
            if subject.get('cat'):
                category = {'qcode': subject.get('cat')}
                if category not in item.get('anpa_category', []):
                    item.setdefault('anpa_category', []).append(category)

        # parser OfInterestTo is CV
        for element in descript_el.findall('OfInterestTo'):
            if element is not None and element.get('FormalName'):
                item.setdefault('subject', []).append({
                    "name": element.get('FormalName'),
                    "qcode": element.get('FormalName'),
                    "scheme": "of_interest_to"
                })

        element = descript_el.find('DateLineDate')
        if element is not None:
            item.setdefault('dateline', {}).update({"date": self.datetime(element.text)})

        location_el = descript_el.find('Location')
        if location_el is not None:
            item['extra'] = {}

            how_present_el = location_el.get('HowPresent', '')
            if how_present_el is not None:
                item['extra']['how_present'] = how_present_el

            elements = location_el.findall('Property')
            for element in elements:
                if element.attrib.get('FormalName', '') == 'Country':
                    country = element.attrib.get('Value')
                    item['extra']['country'] = country
                    # country keywords is CV
                    item.setdefault('subject', []).extend(self._get_country(country))
                if element.attrib.get('FormalName', '') == 'City':
                    item['extra']['city'] = element.attrib.get('Value')
                if element.attrib.get('FormalName', '') == 'CountryArea':
                    item['extra']['country_area'] = element.attrib.get('Value')

        elements = descript_el.findall('Property')
        for element in elements:
            if element.attrib.get('FormalName', '') == 'GeneratorSoftware':
                item['generator_software'] = element.attrib.get('Value')

            if element.attrib.get('FormalName', '') == 'Tesauro':
                item['tesauro'] = element.attrib.get('Value')

            if element.attrib.get('FormalName', '') == 'EfePais':
                item['efe_pais'] = element.attrib.get('Value')

            if element.attrib.get('FormalName', '') == 'EfeRegional':
                item['efe_regional'] = element.attrib.get('Value')

            if element.attrib.get('FormalName', '') == 'EfeComplemento':
                item['efe_complemento'] = element.attrib.get('Value')

            if element.attrib.get('FormalName', '') == 'Keyword':
                data = element.attrib.get('Value')
                if 'keywords' in item:
                    item['keywords'].append(data)
                else:
                    item['keywords'] = [data]

    def parse_contentitem(self, item, content_el):
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
            item['type'] = element.get('FormalName', '')

        element = content_el.find('MimeType')
        if element is not None:
            item['mimetype'] = element.get('FormalName', '')

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
                    item['characteristics']['word_count'] = element.attrib.get('Value')
                if element.attrib.get('FormalName') == 'SizeInBytes':
                    item['characteristics']['size_bytes'] = element.attrib.get('Value')
                if element.attrib.get('FormalName') == 'Creator':
                    item['characteristics']['creator'] = element.attrib.get('Value')
                if element.attrib.get('FormalName') == 'Characters':
                    item['characteristics']['characters'] = element.attrib.get('Value')
                if element.attrib.get('FormalName') == 'FormatVersion':
                    item['characteristics']['format_version'] = element.attrib.get('Value')

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

        iptcsc_cv = self._get_cv('iptc_subject_codes')
        for subject in subjects:
            formal_name = subject.get('FormalName')
            for item in iptcsc_cv.get('items', []):
                if item.get('is_active'):
                    #: check formal_name, format formal_name and filter missing subjects
                    if formal_name and is_not_formatted(formal_name) and item.get('qcode') == formal_name:
                        formatted_subjects.append(
                            {'qcode': formal_name, 'name': subject_codes.get(formal_name, ''),
                             'scheme': 'iptc_subject_codes'})

        return formatted_subjects

    def _plain_to_html(self, text):
        # escape characters
        text = html.escape(text)
        # handle newline
        for newline in ('\r\n', '\n', '\r'):
            text = text.replace(newline, '</p><p>')
        # remove redundant whitespaces
        text = ' '.join(text.split())
        return '<p>' + text + '</p>'

    def _get_cv(self, _id):
        return superdesk.get_resource_service('vocabularies').find_one(req=None, _id=_id)
