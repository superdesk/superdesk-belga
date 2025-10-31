import datetime

from superdesk.utc import local_to_utc
from superdesk.io.registry import register_feed_parser
from planning.feed_parsers.superdesk_planning_xml import (
    PlanningMLParser,
    get_coverage_status_from_cv,
)


class BelgaPlanningMLParser(PlanningMLParser):
    NAME = "belga_planning_ml"
    label = "Belga PlanningML"

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

    def parse_news_coverage_set(self, tree, item, original):
        item.setdefault("firstcreated", item["versioncreated"])
        return super().parse_news_coverage_set(tree, item, original)

    def get_coverage_details(self, news_coverage_elt, item, original):
        if news_coverage_elt.get("id") is None:
            news_coverage_elt.set(
                "id", f"{item['guid']}-cov-{len(item.get('coverages', [])) + 1}"
            )
        coverage = super().get_coverage_details(news_coverage_elt, item, original)
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
