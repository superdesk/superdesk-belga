import datetime

from superdesk import get_resource_service
from superdesk.utc import local_to_utc
from superdesk.io.registry import register_feed_parser
from planning.feed_parsers.superdesk_planning_xml import (
    PlanningMLParser,
    get_coverage_status_from_cv,
)


class BelgaPlanningMLParser(PlanningMLParser):
    NAME = "belga_planning_ml"
    label = "Belga PlanningML"
    EVENT_FIELD_MAP = {
        "name": "name",
        "definition_short": "description_text",
    }

    async def parse_item(self, tree, original):
        item = await super().parse_item(tree, original)
        event_id = (item or {}).get("event_item")
        if not event_id:
            return item

        event = await get_resource_service("events").find_one_async(req=None, _id=event_id)
        if event is None:
            return item

        self._apply_event_metadata(item, event)

        # Set planning_date from event start date and coverage scheduled 1h later
        event_dates = event.get("dates")
        if event_dates and isinstance(event_dates, dict):
            event_start = event_dates.get("start")
            if event_start:
                item["planning_date"] = event_start

                # Set coverage scheduled dates to 1 hour later
                if item.get("coverages"):
                    for coverage in item["coverages"]:
                        if coverage.get("planning"):
                            coverage["planning"]["scheduled"] = (
                                event_start + datetime.timedelta(hours=1)
                            )

        return item

    def _apply_event_metadata(self, item, event):
        """Add multilingual fields from the linked Event to the Planning item."""

        languages = list(item.get("languages") or [])
        for lang in event.get("languages") or []:
            if lang and lang not in languages:
                languages.append(lang)

        event_language = event.get("language")
        if event_language and event_language not in languages:
            languages.append(event_language)

        if languages:
            item["languages"] = languages
            if not item.get("language"):
                item["language"] = languages[0]
        elif event_language and not item.get("language"):
            item["language"] = event_language

        for source_field, target_field in self.EVENT_FIELD_MAP.items():
            if event.get(source_field) and not item.get(target_field):
                item[target_field] = event[source_field]

        event_translations = event.get("translations") or []
        if event_translations:
            translations = item.setdefault("translations", [])

            for translation in event_translations:
                source_field = translation.get("field")
                target_field = self.EVENT_FIELD_MAP.get(source_field)
                language = translation.get("language")
                value = translation.get("value")

                if not target_field or not language or value is None:
                    continue

                translations.append(
                    {"field": target_field, "language": language, "value": value}
                )

    def datetime(self, string):
        try:
            return datetime.datetime.strptime(
                string.strip(), "%Y-%m-%dT%H:%M:%S.000Z"
            ).replace(tzinfo=datetime.timezone.utc)
        except (ValueError, TypeError):
            pass
        try:
            return datetime.datetime.strptime(
                string.strip(), "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=datetime.timezone.utc)
        except (ValueError, TypeError):
            pass
        try:
            parsed = datetime.datetime.fromisoformat(string.strip())
            if parsed.tzinfo is None:
                return local_to_utc("Europe/Brussels", parsed)
            return parsed
        except (ValueError, TypeError):
            pass
        raise ValueError(f"Invalid datetime format: {string}")

    async def parse_news_coverage_set(self, tree, item, original):
        item.setdefault("firstcreated", item["versioncreated"])
        return await super().parse_news_coverage_set(tree, item, original)

    async def get_coverage_details(self, news_coverage_elt, item, original):
        if news_coverage_elt.get("id") is None:
            news_coverage_elt.set(
                "id", f"{item['guid']}-cov-{len(item.get('coverages', [])) + 1}"
            )
        coverage = await super().get_coverage_details(news_coverage_elt, item, original)
        if coverage and coverage.get("planning"):
            if coverage["planning"].get("news_coverage_status"):
                coverage["news_coverage_status"] = coverage["planning"].pop(
                    "news_coverage_status"
                )
            if coverage["planning"].get("scheduled"):
                item["planning_date"] = coverage["planning"]["scheduled"]
        return coverage

    def parse_coverage_planning(self, news_coverage_elt, item):
        planning_elt = news_coverage_elt.find(self.qname("planning"))
        planning = {}
        if planning_elt is not None:
            content = planning_elt.find(self.qname("itemClass")).get("qcode")
            planning["g2_content_type"] = content.split(":")[1]

            description_elt = planning_elt.find(self.qname("description"))
            if description_elt is not None and description_elt.text:
                planning["description_text"] = description_elt.text

            scheduled_elt = planning_elt.find(self.qname("scheduled"))
            if scheduled_elt is not None and scheduled_elt.text:
                planning["scheduled"] = self.datetime(scheduled_elt.text)

            by = planning_elt.find(self.qname("by"))
            if by is not None and by.text:
                planning["internal_note"] = by.text

            ednote = planning_elt.find(self.qname("edNote"))
            if ednote is not None and ednote.text:
                planning["ednote"] = ednote.text

            news_coverage_status_elt = planning_elt.find(
                self.qname("newsCoverageStatus")
            )
            if news_coverage_status_elt is not None:
                qcode = news_coverage_status_elt.get("qcode")
                if qcode:
                    planning["news_coverage_status"] = get_coverage_status_from_cv(
                        qcode
                    )
                    if planning["news_coverage_status"]:
                        planning["news_coverage_status"].pop("is_active", None)

        return planning

    def parse_item_meta(self, tree, item):
        super().parse_item_meta(tree, item)
        meta = tree.find(self.qname("itemMeta"))
        for link in meta.findall(self.qname("link")):
            if link.get("rel") == "irel:associatedWith":
                item["event_item"] = link.get("residref")
                break


register_feed_parser(BelgaPlanningMLParser.NAME, BelgaPlanningMLParser())
