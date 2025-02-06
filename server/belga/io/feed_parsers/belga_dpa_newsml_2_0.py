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
import logging
import itertools
import dateutil.parser
from xml.etree import ElementTree

from superdesk import etree as sd_etree
from superdesk.io.feed_parsers.newsml_2_0 import NewsMLTwoFeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.errors import ParserError
from superdesk.metadata.item import CONTENT_TYPE

from .belga_newsml_mixin import BelgaNewsMLMixin
from superdesk import get_resource_service

logger = logging.getLogger(__name__)
NS = {
    "xhtml": "http://www.w3.org/1999/xhtml",
    "iptc": "http://iptc.org/std/nar/2006-10-01/",
}


class BelgaDPANewsMLTwoFeedParser(BelgaNewsMLMixin, NewsMLTwoFeedParser):
    """
    Feed Parser which can parse DPA variant of NewsML
    """

    NAME = "belga_dpa_newsml20"

    label = "Belga specific DPA News ML 2.0 Parser"
    SUBJ_QCODE_PREFIXES = {"subj": "iptc_subject_code"}
    MAPPING_CATEGORY = {
        "F": "NEWS/ECONOMY",
        "WI": "NEWS/ECONOMY",
        "I": "NEWS/POLITICS",
        "PL": "NEWS/POLITICS",
        "KU": "NEWS/CULTURE",
        "S": "NEWS/SPORTS",
        "SP": "NEWS/SPORTS",
    }

    def can_parse(self, xml):
        return xml.tag.endswith("newsMessage")

    def parse(self, xml, provider=None):
        self.root = xml
        items = []
        try:
            for item_set in xml.findall(self.qname("itemSet")):
                for item_tree in item_set:
                    item = self.parse_item(item_tree)
                    try:
                        published = item_tree.xpath(
                            ".//xhtml:body/xhtml:header/"
                            'xhtml:time[@class="publicationDate"]/@data-datetime',
                            namespaces=NS,
                        )[0]
                    except IndexError:
                        item["firstcreated"] = item["versioncreated"]
                    else:
                        item["firstcreated"] = dateutil.parser.parse(published)
                    item["firstcreated"] = item["firstcreated"].astimezone(pytz.utc)
                    item["versioncreated"] = item["versioncreated"].astimezone(pytz.utc)

                    if item["urgency"] == 4:
                        item["urgency"] = 3

                    # mapping services-products
                    for cat in item.get("anpa_category", []):
                        qcode = self.MAPPING_CATEGORY.get(
                            cat.get("qcode", "").upper(), "NEWS/GENERAL"
                        )
                        item.setdefault("subject", []).append(
                            {
                                "name": qcode,
                                "qcode": qcode,
                                "parent": "NEWS",
                                "scheme": "services-products",
                            }
                        )
                        break
                    else:
                        item.setdefault("subject", []).append(
                            {
                                "name": "NEWS/GENERAL",
                                "qcode": "NEWS/GENERAL",
                                "parent": "NEWS",
                                "scheme": "services-products",
                            }
                        )

                    # Source is DPA
                    credit = {"name": "DPA", "qcode": "DPA", "scheme": "sources"}
                    item.setdefault("subject", []).append(credit)
                    # Distribution is default
                    dist = {
                        "name": "default",
                        "qcode": "default",
                        "scheme": "distribution",
                    }
                    item.setdefault("subject", []).append(dist)
                    # Slugline and keywords is epmty
                    item["slugline"] = None
                    item["keywords"] = []
                    # Find genres and verify their roles and qcodes to acceptance criteria.
                    genres = item_tree.xpath("//iptc:genre", namespaces=NS)
                    for genre in genres:
                        genre_qcode = genre.get("qcode")
                        if genre_qcode and genre_qcode != "dpatextgenre:1":
                            genre_names = genre.findall(self.qname("name"))
                            if genre_names:
                                for genre_name in genre_names:
                                    try:
                                        genre_role = genre_name.attrib["role"]
                                        if genre_role == "nrol:display":
                                            item["headline"] = (
                                                "({genre}): {headline}".format(
                                                    genre=genre_name.text,
                                                    headline=item["headline"],
                                                )
                                            )
                                            break
                                    except KeyError:
                                        continue

                    # remove duplicated subject
                    item["subject"] = [
                        dict(i)
                        for i, _ in itertools.groupby(
                            sorted(item["subject"], key=lambda k: k["qcode"])
                        )
                    ]
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
        header = tree.find(self.qname("header"))
        data["sent"] = dateutil.parser.parse(header.find(self.qname("sent")).text)
        return data

    def parse_inline_content(self, tree, item):
        try:
            body_elt = tree.xpath(
                '//xhtml:body//xhtml:section[contains(@class,"main")]', namespaces=NS
            )[0]
        except IndexError:
            body_elt = tree.xpath("//xhtml:body", namespaces=NS)[0]
        body_elt = sd_etree.clean_html(body_elt)
        content = dict()
        content["contenttype"] = tree.attrib["contenttype"]
        if len(body_elt) > 0:
            content["content"] = sd_etree.to_string(body_elt, method="html")
        elif body_elt.text:
            content["content"] = "<pre>" + body_elt.text + "</pre>"
            content["format"] = CONTENT_TYPE.PREFORMATTED
        return content

    def parse_item_meta(self, tree, item):
        super().parse_item_meta(tree, item)

        meta = tree.find(self.qname("itemMeta"))
        item["ednote"] = "\n".join(
            edNote.text.strip()
            for edNote in meta.findall(self.qname("edNote"))
            if "dpaednoterole:correctionshort" == edNote.attrib.get("role", "")
            and edNote.text
        )

    def parse_content_meta(self, tree, item):
        meta = super().parse_content_meta(tree, item)
        elem = meta.find(self.qname("dateline"))
        if elem is not None:
            self.set_dateline(item, text=elem.text)
        elem = meta.find(self.qname("creditline"))
        if elem is not None:
            item["credit_line"] = elem.text
        elem = meta.find(self.qname("located"))
        if elem is not None:
            name_elt = elem.find(self.qname("name"))
            if name_elt is not None:
                item.setdefault("extra", {})["city"] = name_elt.text

        for elem in meta.findall(self.qname("keyword")):
            data = elem.text.strip()
            # store data in original_metadata and belga-keyword CV
            item.setdefault("subject", []).extend(self._get_keywords(data))
        return meta

    def parse_content_subject(self, tree, item):
        """Parse subj type subjects into subject list."""
        item["subject"] = []
        item["extra"] = {}
        for subject_elt in tree.findall(self.qname("subject")):
            sub_type = subject_elt.get("type", "")
            if sub_type == "dpatype:dpasubject":
                same_as_elts = subject_elt.findall(self.qname("sameAs"))
                for same_as_elt in same_as_elts:
                    subject_data = self._get_data_subject(same_as_elt)
                    if subject_data:
                        item.setdefault("subject", []).append(subject_data)
                        break
            if sub_type == "dpatype:category":
                qcode_parts = subject_elt.get("qcode", "").split(":")
                if qcode_parts:
                    item.setdefault("anpa_category", []).append(
                        {"qcode": qcode_parts[1]}
                    )
            if sub_type == "cpnat:geoArea":
                name_elt = subject_elt.find(self.qname("name"))
                if name_elt is not None and not item["extra"].get("country"):
                    item.setdefault("extra", {})["country"] = name_elt.text
                # looking for ISO 3166-1 alpha-3 code
                for i in subject_elt.findall(self.qname("sameAs")):
                    name_as_elt = i.find(self.qname("name"))
                    code = (
                        i.get("qcode").split(":")[1]
                        if i.get("qcode").startswith("iso3166-1a3")
                        else ""
                    )
                    if len(code) == 3:
                        country_keyword = self._get_country(code)
                        item.setdefault("subject", []).extend(country_keyword)
                        # country is cv
                        item.setdefault("subject", []).extend(self._get_countries(code))
                        break

    def parse_authors(self, meta, item):
        item["authors"] = []
        return

    def _get_data_subject(self, subject_elt):
        qcode_parts = subject_elt.get("qcode", "").split(":")
        if len(qcode_parts) == 2 and qcode_parts[0] in self.SUBJ_QCODE_PREFIXES:
            scheme = self.SUBJ_QCODE_PREFIXES[qcode_parts[0]]
            if scheme:
                # we use the given name if it exists
                name_elt = subject_elt.find(self.qname("name"))
                name = name_elt.text if name_elt is not None and name_elt.text else ""
                try:
                    name = self.getVocabulary(scheme, qcode_parts[1], name)
                    subject_data = {
                        "qcode": qcode_parts[1],
                        "name": name,
                        "scheme": scheme,
                    }
                    return subject_data
                except ValueError:
                    logger.info(
                        'Subject element rejected for "{code}"'.format(
                            code=qcode_parts[1]
                        )
                    )
        return None


register_feed_parser(BelgaDPANewsMLTwoFeedParser.NAME, BelgaDPANewsMLTwoFeedParser())
