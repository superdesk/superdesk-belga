# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

from superdesk import get_resource_service
from superdesk.io.registry import register_feed_parser

from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser


class BelgaEFENewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific EFE NewsML."""

    NAME = "belga_efe_newsml12"
    label = "Belga specific EFE News ML 1.2 Parser"

    MAPPING_PRODUCTS = {
        "SPO": "NEWS/SPORTS",
        "POL": "NEWS/POLITICS",
    }

    # efe related logic goes here
    def parse_contentitem(self, item, content_el):
        super().parse_contentitem(item, content_el)
        categoria = content_el.find('DataContent/nitf/head/meta[@name="categoria"]')
        if categoria is not None:
            content = categoria.attrib.get("content")
            qcode = content.upper() if content is not None else None
            if qcode:
                item.setdefault("anpa_category", []).append({"qcode": qcode})
                qcode = self.MAPPING_PRODUCTS.get(qcode, "NEWS/GENERAL")
                item.setdefault("subject", []).append(
                    {
                        "name": qcode,
                        "qcode": qcode,
                        "parent": "NEWS",
                        "scheme": "services-products",
                    }
                )
            else:
                item.setdefault("subject", []).append(
                    {
                        "name": "NEWS/GENERAL",
                        "qcode": "NEWS/GENERAL",
                        "parent": "NEWS",
                        "scheme": "services-products",
                    }
                )
        # source is EFE
        credit = {"name": "EFE", "qcode": "EFE", "scheme": "sources"}
        item.setdefault("subject", []).append(credit)

        # store data in original_metadata and belga-keyword CV
        for ele in content_el.findall("DataContent/nitf/head/docdata/key-list/keyword"):
            item.setdefault("subject", []).extend(
                self._get_keywords(ele.attrib.get("key"))
            )

        return item


register_feed_parser(BelgaEFENewsMLOneFeedParser.NAME, BelgaEFENewsMLOneFeedParser())
