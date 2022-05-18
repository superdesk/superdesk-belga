# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

from superdesk.io.registry import register_feed_parser
from superdesk.text_utils import get_text
from .base_belga_newsml_1_2 import BaseBelgaNewsMLOneFeedParser
import logging
from superdesk import get_resource_service

logger = logging.getLogger(__name__)


class BelgaAFPNewsMLOneFeedParser(BaseBelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific AFP NewsML."""

    NAME = "belga_afp_newsml12"
    label = "Belga specific AFP News ML 1.2 Parser"
    MAPPING_KEYWORDS = {
        "ECONOMY": ["BOURSE", "ECONOMIE", "CONOMIE", "MARCHES", "FINANCE", "BANQUE"],
        "SPORTS": ["HIPPISME", "SPORT", "SPORTS"],
    }
    MAPPING_CATEGORY = {
        "SPO": "NEWS/SPORTS",
        "POL": "NEWS/POLITICS",
        "ECO": "NEWS/ECONOMY",
    }

    def parse_newsitem(self, item, newsitem_el):
        super().parse_newsitem(item, newsitem_el)
        # mapping services-products from category, and have only one product
        matching = False
        for category in item.get("anpa_category", []):
            qcode = self.MAPPING_CATEGORY.get(category.get("qcode"), "NEWS/GENERAL")
            item.setdefault("subject", []).append(
                {
                    "name": qcode,
                    "qcode": qcode,
                    "parent": "NEWS",
                    "scheme": "services-products",
                }
            )
            matching = True
        if not matching:
            item.setdefault("subject", []).append(
                {
                    "name": "NEWS/GENERAL",
                    "qcode": "NEWS/GENERAL",
                    "parent": "NEWS",
                    "scheme": "services-products",
                }
            )

        # add content for headline when it is empty
        if item.get("urgency") in (1, 2) and not item.get("headline"):
            for line in get_text(item.get("body_html", ""), lf_on_block=True).split(
                "\n"
            ):
                if line.strip():
                    item["headline"] = "URGENT: " + line.strip()
                    break
        # Label must be empty
        item["subject"] = [i for i in item["subject"] if i.get("scheme") != "label"]
        # Source is AFP
        credit = {"name": "AFP", "qcode": "AFP", "scheme": "sources"}
        item.setdefault("subject", []).append(credit)

        if item.get("urgency") == 4:
            item["urgency"] = 3

        return item

    def parse_descriptivemetadata(self, item, descript_el):
        """
        Function parser DescriptiveMetadata in NewsComponent element.

        Example:

        <DescriptiveMetadata>
                <Language FormalName="fr" />
                <SubjectCode>
                    <SubjectMatter FormalName="02008000" cat="CLJ" />
                </SubjectCode>
                <SubjectCode>
                    <SubjectDetail FormalName="02001004" cat="SPO" />
                </SubjectCode>
                <SubjectCode>
                    <SubjectMatter FormalName="02007000" cat="CLJ" />
                </SubjectCode>
                <OfInterestTo FormalName="DAB-TFG-1=DAB" />
                <OfInterestTo FormalName="AMN-TFG-1=AMW" />
                <DateLineDate>20190121T104233+0000</DateLineDate>
                <Location HowPresent="Origin">
                    <Property FormalName="Country" Value="FRA" />
                    <Property FormalName="City" Value="Paris" />
                </Location>
                <Property FormalName="GeneratorSoftware" Value="libg2" />
                <Property FormalName="Keyword" Value="procès" />
                <Property FormalName="Keyword" Value="assises" />
                <Property FormalName="Keyword" Value="marches_test" />
            </DescriptiveMetadata>

        :param item:
        :param descript_el:
        :return:
        """
        if descript_el is None:
            return

        element = descript_el.find("Language")
        if element is not None:
            item["language"] = element.get("FormalName", "")

        for element in descript_el.findall("Genre"):
            if element is not None and element.get("FormalName"):
                self._add_genre(item, element.get("FormalName"))

        element = descript_el.find("guid")
        if element is not None:
            item["descriptive_guid"] = element.text

        # parser SubjectCode element
        subjects = descript_el.findall("SubjectCode/SubjectDetail")
        subjects += descript_el.findall("SubjectCode/SubjectMatter")
        subjects += descript_el.findall("SubjectCode/Subject")
        item.setdefault("subject", []).extend(self.format_subjects(subjects))
        for subject in subjects:
            if subject.get("cat"):
                category = {"qcode": subject.get("cat")}
                if category not in item.get("anpa_category", []):
                    item.setdefault("anpa_category", []).append(category)

        # parser OfInterestTo is CV
        for element in descript_el.findall("OfInterestTo"):
            if element is not None and element.get("FormalName"):
                item.setdefault("subject", []).append(
                    {
                        "name": element.get("FormalName"),
                        "qcode": element.get("FormalName"),
                        "scheme": "of_interest_to",
                    }
                )

        element = descript_el.find("DateLineDate")
        if element is not None:
            item.setdefault("dateline", {}).update(
                {"date": self.datetime(element.text)}
            )

        location_el = descript_el.find("Location")
        if location_el is not None:
            item["extra"] = {}

            how_present_el = location_el.get("HowPresent", "")
            if how_present_el is not None:
                item["extra"]["how_present"] = how_present_el

            elements = location_el.findall("Property")
            for element in elements:
                if element.attrib.get("FormalName", "") == "Country":
                    country = element.attrib.get("Value")
                    item["extra"]["country"] = country
                    # country is cv
                    item.setdefault("subject", []).extend(self._get_countries(country))
                if element.attrib.get("FormalName", "") == "City":
                    item["extra"]["city"] = element.attrib.get("Value")
                if element.attrib.get("FormalName", "") == "CountryArea":
                    item["extra"]["country_area"] = element.attrib.get("Value")

        elements = descript_el.findall("Property")
        for element in elements:
            if element.attrib.get("FormalName", "") == "GeneratorSoftware":
                item["generator_software"] = element.attrib.get("Value")

            if element.attrib.get("FormalName", "") == "Tesauro":
                item["tesauro"] = element.attrib.get("Value")

            if element.attrib.get("FormalName", "") == "EfePais":
                item["efe_pais"] = element.attrib.get("Value")

            if element.attrib.get("FormalName", "") == "EfeRegional":
                item["efe_regional"] = element.attrib.get("Value")

            if element.attrib.get("FormalName", "") == "EfeComplemento":
                item["efe_complemento"] = element.attrib.get("Value")

            if element.attrib.get("FormalName", "") == "Keyword":
                data = element.attrib.get("Value")
                if "keywords" in item:
                    item["keywords"].append(data)
                else:
                    item["keywords"] = [data]

                # store data in original_metadata, countries and belga-keyword CV
                belga_keyword = self._get_mapped_keywords(
                    data.upper(), data.upper(), "belga-keywords"
                )
                if belga_keyword:
                    item.setdefault("subject", []).extend(belga_keyword)

                countries = self._get_mapped_keywords(
                    data.lower(), data.title(), "countries"
                )
                if countries:
                    item.setdefault("subject", []).extend(
                        self._get_country(countries[0]["qcode"])
                    )

                if not belga_keyword and not countries:
                    item.setdefault("subject", []).extend(
                        [{"name": data, "qcode": data, "scheme": "original-metadata"}]
                    )


register_feed_parser(BelgaAFPNewsMLOneFeedParser.NAME, BelgaAFPNewsMLOneFeedParser())
