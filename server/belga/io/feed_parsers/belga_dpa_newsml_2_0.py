# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import pytz

from superdesk.io.feed_parsers.newsml_2_0 import NewsMLTwoFeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.errors import ParserError
from superdesk.metadata.item import CONTENT_TYPE
from superdesk import etree as sd_etree, get_resource_service

import dateutil.parser
import logging

logger = logging.getLogger(__name__)
NS = {'xhtml': 'http://www.w3.org/1999/xhtml',
      'iptc': 'http://iptc.org/std/nar/2006-10-01/'}


class BelgaDPANewsMLTwoFeedParser(NewsMLTwoFeedParser):
    """
    Feed Parser which can parse DPA variant of NewsML
    """

    NAME = 'belga_dpa_newsml20'

    label = 'Belga specific DPA News ML 2.0 Parser'
    SUBJ_QCODE_PREFIXES = {
        'subj': 'iptc_subject_code'
    }

    def can_parse(self, xml):
        return xml.tag.endswith('newsMessage')

    def parse(self, xml, provider=None):
        self.root = xml
        items = []
        try:
            for item_set in xml.findall(self.qname('itemSet')):
                for item_tree in item_set:
                    item = self.parse_item(item_tree)
                    try:
                        published = item_tree.xpath('.//xhtml:body/xhtml:header/'
                                                    'xhtml:time[@class="publicationDate"]/@data-datetime',
                                                    namespaces=NS)[0]
                    except IndexError:
                        item['firstcreated'] = item['versioncreated']
                    else:
                        item['firstcreated'] = dateutil.parser.parse(published)
                    item['firstcreated'] = item['firstcreated'].astimezone(pytz.utc)
                    item['versioncreated'] = item['versioncreated'].astimezone(pytz.utc)
                    items.append(item)
            return items
        except Exception as ex:
            raise ParserError.newsmlTwoParserError(ex, provider)

    def parse_header(self, tree):
        """Parse header element.
        :param tree:
        :return: dict
        """
        data = {}
        header = tree.find(self.qname('header'))
        data['sent'] = dateutil.parser.parse(header.find(self.qname('sent')).text)
        return data

    def parse_inline_content(self, tree, item):
        try:
            body_elt = tree.xpath('//xhtml:body//xhtml:section[contains(@class,"main")]', namespaces=NS)[0]
        except IndexError:
            body_elt = tree.xpath('//xhtml:body', namespaces=NS)[0]
        body_elt = sd_etree.clean_html(body_elt)

        content = dict()
        content['contenttype'] = tree.attrib['contenttype']
        if len(body_elt) > 0:
            content['content'] = sd_etree.to_string(body_elt, method="html")
        elif body_elt.text:
            content['content'] = '<pre>' + body_elt.text + '</pre>'
            content['format'] = CONTENT_TYPE.PREFORMATTED
        return content

    def parse_content_meta(self, tree, item):
        meta = super().parse_content_meta(tree, item)
        elem = meta.find(self.qname('dateline'))
        if elem is not None:
            self.set_dateline(item, text=elem.text)
        elem = meta.find(self.qname('creditline'))
        if elem is not None:
            item['credit_line'] = elem.text
        return meta

    def parse_content_subject(self, tree, item):
        """Parse subj type subjects into subject list."""
        item['subject'] = []
        for subject_elt in tree.findall(self.qname('subject')):
            subject_data = self._get_data_subject(subject_elt)
            if subject_data:
                item['subject'].append(subject_data)
            else:
                same_as_elts = subject_elt.findall(self.qname('sameAs'))
                for same_as_elt in same_as_elts:
                    subject_data = self._get_data_subject(same_as_elt)
                    if subject_data:
                        item['subject'].append(subject_data)
                        break

    def _get_data_subject(self, subject_elt):
        qcode_parts = subject_elt.get('qcode', '').split(':')
        if len(qcode_parts) == 2 and qcode_parts[0] in self.SUBJ_QCODE_PREFIXES:
            scheme = self.SUBJ_QCODE_PREFIXES[qcode_parts[0]]
            if scheme:
                # we use the given name if it exists
                name_elt = subject_elt.find(self.qname('name'))
                name = name_elt.text if name_elt is not None and name_elt.text else ""
                try:
                    name = self.getVocabulary(scheme, qcode_parts[1], name)
                    subject_data = {
                        'qcode': qcode_parts[1],
                        'name': name,
                        "scheme": scheme
                    }
                    return subject_data
                except ValueError:
                    logger.info('Subject element rejected for "{code}"'.format(code=qcode_parts[1]))
        return None


register_feed_parser(BelgaDPANewsMLTwoFeedParser.NAME, BelgaDPANewsMLTwoFeedParser())
