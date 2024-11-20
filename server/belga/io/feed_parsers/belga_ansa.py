# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.io.registry import register_feed_parser
from superdesk.io.feed_parsers.nitf import NITFFeedParser
from lxml import etree
from superdesk.io.iptc import subject_codes
from superdesk import get_resource_service
import pytz
from superdesk.utc import local_to_utc
import arrow


class BelgaANSAFeedParser(NITFFeedParser):
    """
    Feed Parser which can parse if the feed is in ANSA News format.
    """

    NAME = "belga_ansa_newsml"
    label = "Belga ANSA"

    PRIORITY_TABLE = {
        "Flash": 1,
        "Delayed": 2,
        "Bulletin": 3,
        "Urgent": 4,
        "Routine": 5,
    }

    MAPPING_PRODUCT = {
        "NS042": "English Media Service",
    }

    def __init__(self):
        super().__init__()
        self._provider = None

    def can_parse(self, xml):
        return xml.tag.endswith("nitf")

    def parse(self, xml, provider=None):
        # removes unwanted comments
        uncommented_xml = etree.fromstring(
            etree.tostring(xml, encoding="unicode"),
            parser=etree.XMLParser(remove_comments=True),
        )
        item = super().parse(uncommented_xml, provider)
        self.meta_parse(uncommented_xml, item)
        return item

    def meta_parse(self, xml, item):
        """
        Mapped meta tag items
        """
        # Word Count
        wordcount_elem = xml.find("head/meta[@name='wordcount']")
        item["word_count"] = wordcount_elem.attrib.get("content")

        # author and writer
        author_elem = xml.find("head/meta[@name='author']")
        self.parse_author(author_elem, item)

        writer_elem = xml.find("head/meta[@name='writer']")
        self.parse_author(writer_elem, item)

        # keywords
        keywords_elem = xml.find("head/meta[@name='keyword']")
        keyword_text = keywords_elem.attrib.get("content")
        item["keywords"] = [self.remove_prefix(keyword_text)]

        # priority
        priority_elem = xml.find("head/meta[@name='priority']")
        item["priority"] = self.parse_priority(priority_elem)
        item["urgency"] = item["priority"]

        # category
        category_elem = xml.find("head/meta[@name='category']")
        category = {
            "qcode": category_elem.attrib.get("content", ""),
            "name": category_elem.attrib.get("content", ""),
        }
        if category not in item.get("anpa_category", []):
            item.setdefault("anpa_category", []).append(category)

        # IPTC subject
        subjects = xml.findall("head/meta[@name='category_iptc']")
        subjects += xml.findall("head/meta[@name='category']")
        item["subject"] = self.parse_subjects(subjects)

        # Service - Products
        product_elem = xml.find("head/meta[@name='product-id']")
        code = product_elem.attrib.get("content")
        qcode = self.MAPPING_PRODUCT.get(code[0:5], "English Media Servicem")
        item.setdefault("subject", []).append(
            {
                "name": qcode,
                "qcode": qcode,
                "parent": "NEWS",
                "scheme": "services-products",
            }
        )

        # dateline
        dateline_elem = xml.find("body/body.head/dateline/location")
        if dateline_elem is not None:
            self.set_dateline(item, city=(dateline_elem.text).strip())

        # source
        source_elem = xml.find("body/body.head/distributor/org")
        item["source"] = (source_elem.text).strip()

        # headline
        headline_text = self.get_headline(xml).strip()
        item["headline"] = self.remove_prefix(headline_text)

        # byline
        item["byline"] = self.get_byline(xml).strip()

        # body_html
        item["body_html"] = self.parse_content(xml).strip()

    def parse_author(self, author_elem, item):
        """
        Parse author/writer fields
        """
        author_name = author_elem.attrib.get("content", "")
        topic = author_elem.attrib.get("name", "")
        author = {
            "_id": [author_name, topic.upper()],
            "role": topic.upper(),
            "name": topic.upper(),
            "sub_label": author_name,
        }
        # try to find an author in DB
        user = get_resource_service("users").find_one(req=None, username=author_name)
        if user:
            author["_id"] = [
                str(user["_id"]),
                author["role"],
            ]
            author["sub_label"] = user.get("display_name", author["name"])
            author["parent"] = str(user["_id"])
            author["name"] = author["role"]

        item.setdefault("authors", []).append(author)

    def parse_priority(self, priority_elem):
        """
        Function for mapping Priority
        """
        value = {
            "F": "Flash",
            "D": "Delayed",
            "B": "Bulletin",
            "U": "Urgent",
            "R": "Routine",
        }
        priority = priority_elem.attrib.get("content", "")
        return self.PRIORITY_TABLE[value[priority]]

    def parse_subjects(self, subjects):
        """
        Function for Mapping IPTC Subject
        """
        formatted_subjects = []

        def is_not_formatted(qcode):
            for formatted_subject in formatted_subjects:
                if formatted_subject["qcode"] == qcode:
                    return False
            return True

        iptcsc_cv = self._get_cv("iptc_subject_codes")
        for subject in subjects:
            content = subject.attrib.get("content")
            for item in iptcsc_cv.get("items", []):
                if item.get("is_active"):
                    #: check formal_name, format formal_name and filter missing subjects
                    if (
                        content
                        and is_not_formatted(content)
                        and item.get("qcode") == content
                    ):
                        formatted_subjects.append(
                            {
                                "qcode": content,
                                "name": subject_codes.get(content, ""),
                                "scheme": "iptc_subject_codes",
                            }
                        )

        return formatted_subjects

    def _get_cv(self, _id):
        return get_resource_service("vocabularies").find_one(req=None, _id=_id)

    def parse_content(self, xml):
        elements = []
        for elem in xml.findall("body/body.content/block/p"):
            elements.append(etree.tostring(elem, encoding="unicode"))
        content = "".join(elements)
        if self.get_anpa_format(xml) == "t":
            if not content.startswith("<pre>"):
                # convert content to text in a pre tag
                content = "<pre>{}</pre>".format(self.parse_to_preformatted(content))
            else:
                content = self.parse_to_preformatted(content)
        return content

    def remove_prefix(self, text: str) -> str:
        if text.startswith(">>>ANSA/"):
            return text[len(">>>ANSA/") :]
        return text

    def get_norm_datetime(self, tree):
        value = super().get_norm_datetime(tree)
        return local_to_utc("Europe/Rome", value)


register_feed_parser(BelgaANSAFeedParser.NAME, BelgaANSAFeedParser())
