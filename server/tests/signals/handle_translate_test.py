from copy import deepcopy

import superdesk
from superdesk.tests import TestCase


class HandleTranslateSignalTestCase(TestCase):
    def test_duplicate_signals(self):
        archive_service = superdesk.get_resource_service("archive")
        original_item = {
            "_id": "original-fr",
            "headline": "original fr",
            "language": "fr",
            "associations": {
                "editor_0": {
                    "renditions": {
                        "original": {
                            "width": 5472,
                            "height": 3648,
                            "href": "https://3.t.cdn.belga.be/belgaimage:154620545:1800x650:w?v=5d5aaa94&m=njopcomo",
                        }
                    },
                    "type": "picture",
                    "pubstatus": "usable",
                    "_id": "urn:belga.be:image:154620545",
                    "guid": "urn:belga.be:image:154620545",
                    "headline": "20190827_zap_d99_014.jpg",
                    "description_text": "August 27, 2019: Gaza, Palestine.",
                    "versioncreated": "2019-08-28T09:22:17+0000",
                    "firstcreated": "2019-08-28T09:22:17+0000",
                    "byline": "NBWBNX",
                    "creditline": "ZUMAPRESS",
                    "source": "ZUMAPRESS",
                },
                "belga_related_images--0": {
                    "renditions": {
                        "original": {
                            "width": 4288,
                            "height": 3012,
                            "href": "https://0.t.cdn.belga.be/belgaimage:154670415:1800x650:w?v=5d5aaa94&m=ablplddf",
                        }
                    },
                    "_links": {
                        "self": {
                            "title": "Search_providers_proxy",
                            "href": "search_providers_proxy/urn:belga.be:image:154670415",
                        }
                    },
                    "type": "picture",
                    "pubstatus": "usable",
                    "_id": "urn:belga.be:image:154670415",
                    "guid": "urn:belga.be:image:154670415",
                    "headline": "urn:newsml:dpa.com:20090101:190829-99-659387",
                    "description_text": "29 August 2019, Hanover: Cycling: UCI Europaserie, Germany Tour.",
                    "versioncreated": "2019-08-29T13:22:02+0000",
                    "firstcreated": "2019-08-29T13:22:02+0000",
                    "byline": "NBYXIU",
                    "creditline": "DPA",
                    "source": "DPA",
                    "_type": "externalsource",
                    "fetch_endpoint": "search_providers_proxy",
                },
                "belga-coverages--0": {
                    "renditions": {
                        "original": {
                            "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                        }
                    },
                    "extra": {"bcoverage": "urn:belga.be:coverage:6690595"},
                    "type": "graphic",
                    "mimetype": "application/vnd.belga.coverage",
                    "pubstatus": "usable",
                    "_id": "urn:belga.be:coverage:6690595",
                    "guid": "urn:belga.be:coverage:6690595",
                    "headline": "RUSSIAN PARAGLIDING CHAMPIONSHIP IN STAVROPOL TERRITORY",
                    "description_text": "STAVROPOL TERRITORY, RUSSIA - AUGUST 28, 2019."
                    " Paragliding Championship on Mount Yutsa. Anton Podgaiko/TASS 0",
                    "versioncreated": "2019-08-29T15:46:39+0000",
                    "firstcreated": "2019-08-29T15:46:39+0000",
                    "byline": "",
                    "creditline": "ITARTASS",
                    "source": "ITARTASS",
                    "_type": "externalsource",
                },
                "belga_related_articles--0": {
                    "extra": {"bcoverage": "urn:belga.be:360archive:77777777"},
                    "type": "text",
                    "mimetype": "application/vnd.belga.360archive",
                    "pubstatus": "usable",
                    "_id": "urn:belga.be:360archive:77777777",
                    "guid": "urn:belga.be:360archive:77777777",
                    "headline": "Vasil Kiryienka (38) doet ondanks hartproblemen verder bij INEOS",
                    "name": "",
                    "description_text": "",
                    "versioncreated": "2019-10-23T09:30:14+0000",
                    "firstcreated": "2019-10-23T09:30:14+0000",
                    "creditline": "BELGA",
                    "source": "BELGA",
                    "language": "nl",
                    "abstract": "Vasil Kiryienka zal ook in 2020 deel uitmaken van het peloton.",
                    "body_html": "Kiryienka werd dit jaar opgeschrikt door een hartprobleem.",
                    "_type": "externalsource",
                    "fetch_endpoint": "search_providers_proxy",
                    "ingest_provider": "5da8572a9e7cb98d13ce1d7b",
                    "selected": False,
                },
                "belga-related-video--1": {
                    "_id": "urn:newsml:localhost:5000:2019-08-14T16:51:06.604540:734d4292-db4f-4358-8b2f-c2273a4925d5",
                    "type": "video",
                },
            },
        }
        archive_service.create([original_item])
        original_item = archive_service.find_one(None, _id="original-fr")

        translate_item = deepcopy(original_item)
        translate_item["language"] = "nl"
        translate_guid = archive_service.duplicate_item(
            translate_item, operation="translate"
        )

        translate_item = archive_service.find_one(None, guid=translate_guid)

        # ensure that there are no belga-360 and videos in associations
        assert "belga-related-video--1" not in translate_item["associations"]
        assert "belga_related_articles--0" not in translate_item["associations"]
