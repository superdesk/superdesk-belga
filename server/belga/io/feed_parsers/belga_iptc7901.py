# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import re
import logging

from superdesk.errors import ParserError
from superdesk.io.registry import register_feed_parser
from superdesk.io.feed_parsers.dpa_iptc7901 import DPAIPTC7901FeedParser
from superdesk.metadata.utils import generate_guid
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, GUID_TAG
from superdesk.utc import utcnow

logger = logging.getLogger(__name__)


class BelgaIPTC7901FeedParser(DPAIPTC7901FeedParser):
    """
    Feed Parser which can parse if the feed is in IPTC 7901 format.
    """

    NAME = "belgaiptc7901"

    label = "Belga IPTC 7901 Parser"

    types = {
        "dpa": (
            b"([a-zA-Z]*)([0-9]*) (.) ([A-Z]{1,3}) ([0-9]*) ([a-zA-Z0-9 ]*)",
            [" =\n"],
        ),
        "ats": (b"(\x7f\x7f|\x7f)", [" = \r\n"]),
    }
    txt_type = None

    MAPPING_PRODUCTS = {
        "ats": {
            "CL": "NEWS/CULTURE",
            "EC": "NEWS/ECONOMY",
        },
        "dpa": {
            "F": "NEWS/ECONOMY",
            "WI": "NEWS/ECONOMY",
            "I": "NEWS/POLITICS",
            "PL": "NEWS/POLITICS",
            "KU": "NEWS/CULTURE",
            "S": "NEWS/SPORTS",
            "SP": "NEWS/SPORTS",
        },
    }

    def can_parse(self, file_path):
        try:
            BelgaIPTC7901FeedParser.txt_type = None
            with open(file_path, "rb") as f:
                lines = list(f)
                for _type, regex in self.types.items():
                    check_type = re.match(regex[0], lines[0], flags=re.I)
                    if check_type:
                        BelgaIPTC7901FeedParser.txt_type = _type
                        return check_type
        except Exception:
            return False

    def parse(self, file_path, provider=None):
        item = {}
        _type = BelgaIPTC7901FeedParser.txt_type
        if _type == "dpa":
            item = self.parse_content_dpa(file_path, provider)
        if _type == "ats":
            item = self.parse_content_ats(file_path, provider)
        # Slugline and keywords is epmty
        item["slugline"] = None
        item["keywords"] = []
        item = self.dpa_derive_dateline(item)
        # Markup the text and set the content type
        item["body_html"] = (
            "<p>"
            + item["body_html"].replace("\r\n", " ").replace("\n", "</p><p>")
            + "</p>"
        )

        invalid_xmlchars = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "\u0007": " ",
            "\u0003": " ",
            "\u0004": " ",
            "\u001f": " ",
        }
        for char, replace_char in invalid_xmlchars.items():
            item["body_html"].replace(char, replace_char)
            item["headline"].replace(char, replace_char)
            item.get("lead", "").replace(char, replace_char)

        item[ITEM_TYPE] = CONTENT_TYPE.TEXT
        return item

    def parse_content_ats(self, file_path, provider=None):
        try:
            item = {
                ITEM_TYPE: CONTENT_TYPE.TEXT,
                "guid": generate_guid(type=GUID_TAG),
                "versioncreated": utcnow(),
                "language": "fr",
            }

            with open(file_path, "rb") as f:
                lines = list(f)

            # parse first header line
            m = re.match(
                b"\x7f\x01([a-zA-Z]*)([0-9]*) (.) ([A-Z]{1,3}) ([0-9]*) ([a-zA-Z0-9 ]*)",
                lines[1],
                flags=re.I,
            )
            if m:
                qcode = m.group(4).decode().upper()
                item["original_source"] = m.group(1).decode("latin-1", "replace")
                item["ingest_provider_sequence"] = m.group(2).decode()
                item["priority"] = self.map_priority(m.group(3).decode())
                item["anpa_category"] = [{"qcode": self.map_category(qcode)}]
                qcode = self.MAPPING_PRODUCTS["ats"].get(qcode, "NEWS/GENERAL")
                item.setdefault("subject", []).append(
                    {
                        "name": qcode,
                        "qcode": qcode,
                        "parent": "NEWS",
                        "scheme": "services-products",
                    }
                )
                item["subject"].extend(
                    [
                        {"name": "ATS", "qcode": "ATS", "scheme": "sources"},
                        {
                            "name": "default",
                            "qcode": "default",
                            "scheme": "distribution",
                        },
                    ]
                )
                item["word_count"] = int(m.group(5).decode())

            content = b"\n".join(lines[1:]).decode("latin-1", "replace")
            header = re.search(r".*=", content)
            item["headline"] = header.group(0).strip() if header else ""

            body = re.search(r"(?s)=\s{2,}(.*)", content)
            if body:
                body = re.split(r"(?s)\s{3,}", body.group(1), 1)
                if len(body) == 2:
                    item["abstract"], item["body_html"] = body
                    city = re.search(r"^(\S*)", item["abstract"])
                    if city:
                        item.setdefault("extra", {})["city"] = city.group(0).strip()
                else:
                    item["body_html"] = body[0]
            return item
        except Exception as ex:
            raise ParserError.IPTC7901ParserError(exception=ex, provider=provider)

    def parse_content_dpa(self, file_path, provider=None):
        try:
            item = {
                ITEM_TYPE: CONTENT_TYPE.TEXT,
                "guid": generate_guid(type=GUID_TAG),
                "versioncreated": utcnow(),
            }

            with open(file_path, "rb") as f:
                lines = list(f)
            # parse first header line
            m = re.match(
                b"([a-zA-Z]*)([0-9]*) (.) ([A-Z]{1,3}) ([0-9]*) ([a-zA-Z0-9 ]*)",
                lines[0],
                flags=re.I,
            )
            if m:
                qcode = m.group(4).decode().upper()
                item["original_source"] = m.group(1).decode("latin-1", "replace")
                item["ingest_provider_sequence"] = m.group(2).decode()
                item["priority"] = self.map_priority(m.group(3).decode())
                item["anpa_category"] = [{"qcode": self.map_category(qcode)}]
                # mapping product
                qcode = self.MAPPING_PRODUCTS["dpa"].get(qcode, "NEWS/GENERAL")
                item.setdefault("subject", []).append(
                    {
                        "name": qcode,
                        "qcode": qcode,
                        "parent": "NEWS",
                        "scheme": "services-products",
                    }
                )
                # source is DPA
                credit = {"name": "DPA", "qcode": "DPA", "scheme": "sources"}
                item.setdefault("subject", []).append(credit)
                # Distribution is default
                dist = {"name": "default", "qcode": "default", "scheme": "distribution"}
                item.setdefault("subject", []).append(dist)
                item["word_count"] = int(m.group(5).decode())

            inHeader = False
            inBody = False
            inNote = False
            line_count = 0
            item["headline"] = ""
            item["body_html"] = ""
            # start check each line for get information
            for line in lines[1:]:
                line = line.decode("latin-1", "replace")
                line_count += 1
                # slugline is before the header
                if line_count < 3:
                    if "slugline" not in item:
                        item["slugline"] = ""
                    item["slugline"] += line.rstrip("/\r\n")
                    continue
                # dpa start header when line number is 3
                if line_count == 3:
                    inHeader = True
                if inHeader is True:
                    if str.isupper(line):
                        if "anpa_take_key" in item:
                            item["anpa_take_key"] += " " + line.rstrip("\n")
                        else:
                            item["anpa_take_key"] = line.rstrip("\n")
                        continue
                    if line.startswith("(") or line.endswith(")"):
                        if "anpa_header" in item:
                            item["anpa_header"] += " " + line
                        else:
                            item["anpa_header"] = line
                        continue
                    # dpa end header when line end with especially characters (ex '=\r\n')
                    end_string = self.check_mendwith(
                        line, self.types[BelgaIPTC7901FeedParser.txt_type][1]
                    )
                    if end_string:
                        if line.startswith("By "):
                            item["byline"] = line.replace("By ", "").rstrip(end_string)
                        else:
                            item["headline"] += line.rstrip(end_string)
                        inHeader = False
                        # set flag inBody when header is end
                        inBody = True
                    else:
                        item["headline"] += line
                        inHeader = True
                    continue
                # dpa start body when the header is end
                if inBody:
                    if (
                        line.find("The following information is not for publication")
                        != -1
                        or line.find(
                            "The following information is not intended for publication"
                        )
                        != -1
                    ):
                        inNote = True
                        inBody = False
                        item["ednote"] = ""
                        continue
                    item["body_html"] += line
                if inNote:
                    item["ednote"] += line
                    continue
            return item
        except Exception as ex:
            raise ParserError.IPTC7901ParserError(exception=ex, provider=provider)

    def check_mendwith(self, string, end_strings):
        for end_string in end_strings:
            if string.endswith(end_string):
                return end_string
        return None

    def parse_header(self, item):
        """
        Try to pickout the headline, byline and take key from what is seemingly a header
        :param item:
        :return:
        """
        item["headline"] = ""
        headers, divider, the_rest = self.mpartition(
            item.get("body_html", ""), self.types[BelgaIPTC7901FeedParser.txt_type][1]
        )
        # If no divider then there was only one line and that is the headline so clean up the stray '='
        if not divider:
            item["headline"] = item.get("headline").replace(" =", "")
            return

        headerlines = headers.split("\n")

        for line in headerlines:
            if str.isupper(line):
                if "anpa_take_key" in item:
                    item["anpa_take_key"] += " " + line
                else:
                    item["anpa_take_key"] = line
                continue
            if line.startswith("(") or line.endswith(")"):
                if "anpa_header" in item:
                    item["anpa_header"] += " " + line
                else:
                    item["anpa_header"] = line
                continue
            if line == headerlines[-1]:
                if line.startswith("By "):
                    item["byline"] = line.replace("By ", "")
                    continue
            item["headline"] += line + "\n"
        item["body_html"] = the_rest

    def mpartition(self, string, substrings):
        for substring in substrings:
            if substring in string:
                return string.partition(substring)
        return string, None, None


register_feed_parser(BelgaIPTC7901FeedParser.NAME, BelgaIPTC7901FeedParser())
