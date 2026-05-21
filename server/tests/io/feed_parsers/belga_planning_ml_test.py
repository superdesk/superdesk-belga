import os
import datetime

import lxml.etree

from belga.io.feed_parsers.belga_planning_ml import BelgaPlanningMLParser
from tests import TestCase


class BelgaPlanningMLTestCase(TestCase):
    filename = "belga_planning_ml.xml"
    parser = BelgaPlanningMLParser()

    def fixture(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, "../fixtures", self.filename))
        with open(fixture, "r") as f:
            return self.load(f)

    def load(self, _file):
        return lxml.etree.parse(_file)

    async def parse(self):
        xml = self.fixture()
        self.item = (await self.parser.parse(xml.getroot(), {"name": "test"}))[0]

    async def asyncSetUp(self):
        await super().asyncSetUp()
        event_start = datetime.datetime.fromisoformat("2025-05-05T22:00:00+00:00")
        self.event = {
            "_id": "urn:event:123",
            "type": "event",
            "dates": {"start": event_start},
            "language": "en",
            "languages": ["fr", "nl"],
            "name": "Event Name",
            "definition_short": "Short description",
            "translations": [
                {"field": "name", "language": "fr", "value": "Nom FR"},
                {"field": "definition_short", "language": "nl", "value": "Korte NL"},
            ],
        }

        # Store the linked Event so the parser can retrieve it during ingest
        self.app.data.insert("events", [self.event])
        await self.parse()

    async def test_parser(self):
        assert self.item is not None
        assert len(self.item["coverages"]) == 2
        assert self.item["item_class"] == "plinat:newscoverage"
        assert self.item["planning_date"].isoformat() == "2025-05-05T22:00:00+00:00"
        assert self.item["related_events"] == [
            {"_id": "urn:event:123", "link_type": "primary"}
        ]

        assert self.item["coverages"][0]["planning"]["internal_note"] == "John"
        assert self.item["coverages"][0]["planning"]["ednote"] == "Planned coverage"
        assert self.item["coverages"][0]["planning"]["g2_content_type"] == "text"
        assert (
            self.item["coverages"][0]["planning"]["scheduled"].isoformat()
            == "2025-05-05T23:00:00+00:00"
        )
        assert self.item["coverages"][0]["news_coverage_status"] == {
            "name": "coverage intended",
            "qcode": "ncostat:int",
            "label": "Planned",
        }
        assert self.item["coverages"][1]["news_coverage_status"] == {
            "name": "coverage not decided yet",
            "qcode": "ncostat:notdec",
            "label": "On merit",
        }

    async def test_event_metadata_inherited(self):
        assert self.item["languages"] == ["fr", "nl", "en"]
        assert self.item["language"] == "fr"
        assert self.item["name"] == "Event Name"
        assert self.item["description_text"] == "Short description"

        translations = {
            (t["field"], t["language"], t["value"])
            for t in self.item.get("translations", [])
        }
        assert (
            "name",
            "fr",
            "Nom FR",
        ) in translations
        assert (
            "description_text",
            "nl",
            "Korte NL",
        ) in translations
