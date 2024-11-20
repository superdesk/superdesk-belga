# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.io.feeding_services import RSSFeedingService
from superdesk.io.registry import (
    register_feeding_service,
    register_feeding_service_parser,
)


class RSSBelgaFeedingService(RSSFeedingService):
    NAME = "rss-belga"
    label = "RSS BELGA"

    def _create_item(self, data, field_aliases=None, source="source"):
        item = super()._create_item(data, field_aliases, source)

        # get Belga anp atom data
        provider_id = data.get("anp_provider", None)
        if provider_id == "ANP":
            item["provider_id"] = provider_id
            item["char_count"] = data.get("anp_charcount")
            item["location"] = {
                "city": data.get("anp_city"),
                "country": data.get("anp_country"),
            }
            item["codes"] = data.get("anp_codes")
            item["copyright"] = data.get("anp_copyright")
            item["financial"] = data.get("anp_financial")
            item["keywords"] = [data.get("anp_keywords")]
            item["language"] = data.get("anp_lang")
            item["priority"] = data.get("anp_priority")
            item["updated_date"] = data.get("anp_updated")
            item["version"] = data.get("anp_version")
            item["word_count"] = data.get("anp_wordcount")
            author_name = data.get("author")
            if author_name:
                author = {
                    "uri": None,
                    "parent": None,
                    "name": author_name,
                    "role": None,
                    "jobtitle": None,
                }
                item["authors"] = [author]
        return item


register_feeding_service(RSSBelgaFeedingService)
register_feeding_service_parser(RSSBelgaFeedingService.NAME, None)
