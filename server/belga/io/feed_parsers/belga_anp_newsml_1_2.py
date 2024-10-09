# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

import pytz
import re
import itertools

from superdesk.io.registry import register_feed_parser

from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser
import logging
from superdesk import get_resource_service

logger = logging.getLogger(__name__)


class BelgaANPNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific ANP NewsML."""

    NAME = "belga_anp_newsml12"
    label = "Belga specific ANP News ML 1.2 Parser"

    MAPPING_PRODUCTS = {
        "SPO": "NEWS/SPORTS",
        "ECO": "NEWS/ECONOMY",
    }

    # anp related logic goes here
    def parse_newsmanagement(self, item, manage_el):
        super().parse_newsmanagement(item, manage_el)
        item["firstcreated"] = item["firstcreated"].astimezone(pytz.utc)
        item["versioncreated"] = item["versioncreated"].astimezone(pytz.utc)

    def parse_newsitem(self, item, newsitem_el):
        super().parse_newsitem(item, newsitem_el)
        for genre in self._get_genre(item):
            qcode = self.MAPPING_PRODUCTS.get(genre.get("name"), "NEWS/GENERAL")
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
        # Source is ANP
        credit = {"name": "ANP", "qcode": "ANP", "scheme": "sources"}
        item.setdefault("subject", []).append(credit)

        # SDBELGA-689
        for subject in item["subject"]:
            if (
                subject["scheme"] == "original-metadata"
                and subject["name"].find(";") != -1
            ):
                for keyword in set(re.split("[-;]", subject["name"])):
                    # SDBELGA-713
                    item.setdefault("subject", []).extend(self._get_keywords(keyword))
                item["subject"].remove(subject)
                item["subject"] = [
                    dict(i)
                    for i, _ in itertools.groupby(
                        sorted(item["subject"], key=lambda k: k["qcode"])
                    )
                ]

        # SDBELGA-530
        if not item.get("extra", {}).get("city"):
            item.get("extra")["city"] = self.extract_city(item)

        return item

    def extract_city(self, item):
        """
        extract city from body_html
        """
        location_match = re.search(
            r"([A-Z][A-Za-z ]+)\s*\(\s*[A-Z/]+\s*\)", item["body_html"]
        )
        if location_match:
            return location_match.group(1).strip()
        return ""


register_feed_parser(BelgaANPNewsMLOneFeedParser.NAME, BelgaANPNewsMLOneFeedParser())
