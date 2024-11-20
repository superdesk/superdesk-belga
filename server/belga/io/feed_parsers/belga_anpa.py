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
from datetime import datetime
from eve.utils import config
from superdesk.errors import ParserError
from superdesk.io.registry import register_feed_parser
from superdesk.io.feed_parsers.anpa import ANPAFeedParser
from superdesk.metadata.item import (
    ITEM_TYPE,
    CONTENT_TYPE,
    GUID_FIELD,
    GUID_TAG,
    FORMAT,
    FORMATS,
)
import pytz
from superdesk.metadata.utils import generate_guid


class BelgaANPAFeedParser(ANPAFeedParser):
    """
    Feed Parser which can parse if the feed is in ANPA 1312 format.
    """

    NAME = "belgaanpa1312"
    label = "Belga anpa1312"

    MAPPING_PRODUCTS = {
        "F": "NEWS/ECONOMY",
        "P": "NEWS/POLITICS",
        "E": "NEWS/CULTURE",
        "S": "NEWS/SPORTS",
    }

    def can_parse(self, file_path):
        try:
            with open(file_path, "rb") as f:
                lines = [line for line in f]
                return re.match(
                    b"\x01([a-z])([0-9]{4})KYODO\x1f([a-z0-9-]+)", lines[0], flags=re.I
                )
        except Exception:
            return False

    def parse(self, file_path, provider=None):
        try:
            item = {
                ITEM_TYPE: CONTENT_TYPE.TEXT,
                GUID_FIELD: generate_guid(type=GUID_TAG),
                FORMAT: FORMATS.HTML,
            }

            with open(file_path, "rb") as f:
                lines = [line for line in f]

            # parse first header line
            m = re.match(
                b"x01([a-z])([0-9]{4})KYODO\x1f([a-z0-9-]+)", lines[0], flags=re.I
            )
            if m:
                item["provider_sequence"] = m.group(2).decode()

            # parse second header line
            m = re.match(
                b"([a-z]) ([a-z])(\x13|\x14)(\x11|\x12) (am-|pm-|bc-|ap-)([a-z-.]+)(.*) "
                b"([0-9]{1,2})-([0-9]{1,2}) ([0-9]{4})",
                lines[1],
                flags=re.I,
            )
            if m:
                item["language"] = "en"
                item["priority"] = 2 if m.group(1).decode() == "u" else 3
                qcode = m.group(2).decode().upper()
                item["anpa_category"] = [{"qcode": qcode}]
                # Mapping product
                qcode = self.MAPPING_PRODUCTS.get(qcode, "NEWS/GENERAL")
                item.setdefault("subject", []).extend(
                    [
                        {
                            "name": qcode,
                            "qcode": qcode,
                            "parent": "NEWS",
                            "scheme": "services-products",
                        },
                        {"name": "KYODO", "qcode": "KYODO", "scheme": "sources"},
                        {
                            "name": "default",
                            "qcode": "default",
                            "scheme": "distribution",
                        },
                    ]
                )
                item["slugline"] = m.group(6).decode("latin-1", "replace")
                item["anpa_take_key"] = m.group(7).decode("latin-1", "replace").strip()
                item["word_count"] = int(m.group(10).decode())
                if m.group(4) == b"\x12":
                    item[FORMAT] = FORMATS.PRESERVED

            # parse created date at the end of file
            m = re.search(
                b"\x03([A-Z]{3})-([0-9]{2}:[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2})",
                lines[-1],
                flags=re.I,
            )
            if m:
                tz = pytz.timezone(config.TIMEZONE_CODE[str.lower(m.group(1).decode())])
                date = datetime.strptime(m.group(2).decode(), "%H:%M-%d-%m-%y").replace(
                    tzinfo=tz
                )
                item["firstcreated"] = date.astimezone(pytz.utc)
                item["versioncreated"] = item["firstcreated"]

            # parse anpa content
            body = b"".join(lines[2:])
            m = re.match(b"\x02(.*)\x03", body, flags=re.M + re.S)
            if m:
                text = m.group(1).decode("latin-1", "replace").split("\n")
                item["keywords"] = text[0].strip("\r").split("-")
                item["abstract"] = (
                    re.split("\\..?", ("".join(line.strip() for line in text[2:-1])))[0]
                    + "."
                )
                item.setdefault("extra", {})["city"] = item.get("abstract", "").split(
                    ","
                )[0]
                is_header = True
                for line in text:
                    if line == text[0]:
                        m = re.match("BC-(.*)", line, flags=re.I)
                        if m:
                            item["slugline"] = str.rstrip(m.group(1), "\r")
                            continue
                    if is_header is True:
                        if line.endswith("+\r"):
                            is_header = False
                        line = (
                            line.rstrip("\r")
                            if is_header is True
                            else line.rstrip("+\r")
                        )
                        line = line
                        if "headline" in item:
                            item["headline"] += line
                        else:
                            item["headline"] = line
                        continue

                    if line == "==Kyodo\r":
                        break
                    line = line.rstrip("\r")

                    if "body_html" in item:
                        item["body_html"] += "<p>" + line + "</p>"
                    else:
                        item["body_html"] = "<p>" + line + "</p>"

                self._parse_ednote(item["headline"], item)
            # Slugline and keywords is epmty
            item["slugline"] = None
            item["keywords"] = []
            return item
        except Exception as ex:
            raise ParserError.anpaParseFileError(file_path, ex)


register_feed_parser(BelgaANPAFeedParser.NAME, BelgaANPAFeedParser())
