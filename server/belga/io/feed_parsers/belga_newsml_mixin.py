# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import get_resource_service


class BelgaNewsMLMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._countries = []

    async def _get_country(self, country_code):
        if not self._countries:
            cv = await get_resource_service("vocabularies").find_one_async(req=None, _id="country")
            self._countries = (cv or {}).get("items", [])

        return [
            {
                "name": c["name"],
                "qcode": c["qcode"],
                "translations": c["translations"],
                "scheme": "country",
            }
            for c in self._countries
            if c.get("qcode") == "country_" + country_code.lower()
            and c.get("is_active")
        ]

    async def _get_countries(self, country_code):
        if not country_code:
            return []

        countries = await get_resource_service("vocabularies").get_items_async(
            _id="countries", qcode=country_code.lower()
        )

        return countries

    async def _get_keywords(self, data):
        if not data:
            return []

        belga_keyword = await self._get_mapped_keywords(
            data.upper(), data.upper(), "belga-keywords"
        )
        if belga_keyword:
            return belga_keyword

        countries = await self._get_mapped_keywords(data.lower(), data.title(), "countries")
        if countries:
            return countries + await self._get_country(countries[0]["qcode"])

        return [{"name": data, "qcode": data, "scheme": "original-metadata"}]

    async def _get_mapped_keywords(self, _key, _translation_key, _id_name):
        _all_keywords = await get_resource_service("vocabularies").find_one_async(
            req=None, _id=_id_name
        )
        if not _all_keywords:
            return
        for _keyword in _all_keywords.get("items", []):
            if (
                _keyword["qcode"] == _key
                or _translation_key
                in _keyword.get("translations", {}).get("name", {}).values()
                or _keyword["name"] == _key
            ):
                return [
                    {
                        "name": _keyword["name"],
                        "qcode": _keyword["qcode"],
                        "translations": _keyword["translations"],
                        "scheme": _id_name,
                    }
                ]
        return []
