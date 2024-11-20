# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import pytz
import json
import datetime
from pathlib import Path
from lxml import etree
from unittest import mock
from bson.objectid import ObjectId

from superdesk.publish import init_app
from belga.publish.belga_newsml_1_2 import BelgaNewsML12Formatter
from .. import TestCase


fixtures_path = Path(__file__).parent.parent / "fixtures"


belga_apiget_response = {
    "galleryId": 6666666,
    "active": True,
    "type": "C",
    "name": "JUDO   JPN   WORLD",
    "description": "Noel Van T End of Netherlands (L) celebrates after winning the gold medal.",
    "createDate": "2019-08-30T14:33:10Z",
    "deadlineDate": None,
    "author": "auto",
    "credit": "AFP",
    "category": None,
    "tagAuthor": None,
    "iconImageId": 777777777,
    "iconThumbnailUrl": "https://2.t.cdn.belga.be/belgaimage:154669691:800x800:w?v=6666666&m=aaaaaaaa",
    "nrImages": 364,
    "themes": ["all", "news", "sports"],
}


class BelgaNewsML12Formatter_ItemsChainTest(TestCase):
    article = {
        "_id": "update-2",
        "guid": "update-2",
        "type": "text",
        "version": 1,
        "profile": "belga_text",
        "pubstatus": "usable",
        "format": "HTML",
        "template": ObjectId("5c94ead2fe985e1c5776ddca"),
        "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
        "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
        "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
        "versioncreated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
        "firstpublished": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
        "original_creator": "5d385f31fe985ec67a0ca583",
        "state": "corrected",
        "source": "Belga",
        "priority": 6,
        "urgency": 4,
        "language": "nl",
        "headline": "New Skoda Scala 2",
        "keywords": ["europe", "Prague", "CZ", "Skoda"],
        "slugline": "skoda scala",
        "byline": "BELGA",
        "rewrite_of": "update-1",
        "rewrite_sequence": 2,
    }

    archive = (
        {
            "_id": "original",
            "guid": "original",
            "type": "text",
            "version": 1,
            "profile": "belga_text",
            "pubstatus": "usable",
            "format": "HTML",
            "template": ObjectId("5c94ead2fe985e1c5776ddca"),
            "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
            "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "firstpublished": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "state": "corrected",
            "source": "Belga",
            "priority": 6,
            "urgency": 4,
            "language": "nl",
            "headline": "New Skoda Scala",
            "keywords": ["europe", "Prague", "CZ", "Skoda"],
            "slugline": "skoda scala",
            "byline": "BELGA",
            "rewritten_by": "update-1",
            "translation_id": "original",
            "translations": ["original-fr"],
            "associations": {
                "editor_0": {
                    "renditions": {
                        "original": {
                            "width": 5472,
                            "height": 3648,
                            "href": "https://3.t.cdn.belga.be/belgaimage:154620545:1800x650:w?v=5d5aaa94&m=njopcomo",
                        },
                        "thumbnail": {
                            "href": "http://p.cdn.belga.be/belgaimage:154620545:600x140?v=5d5aaa94&m=kmjjblom"
                        },
                        "viewImage": {
                            "href": "https://3.t.cdn.belga.be/belgaimage:154620545:800x800:w?v=5d5aaa94&m=hdccpkpj"
                        },
                        "baseImage": {
                            "href": "https://3.t.cdn.belga.be/belgaimage:154620545:1800x650:w?v=5d5aaa94&m=njopcomo"
                        },
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
                        },
                        "thumbnail": {
                            "href": "http://p.cdn.belga.be/belgaimage:154670415:600x140?v=5d5aaa94&m=fcgloioh"
                        },
                        "viewImage": {
                            "href": "https://2.t.cdn.belga.be/belgaimage:154670415:800x800:w?v=5d5aaa94&m=ebedljnc"
                        },
                        "baseImage": {
                            "href": "https://0.t.cdn.belga.be/belgaimage:154670415:1800x650:w?v=5d5aaa94&m=ablplddf"
                        },
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
                        },
                        "thumbnail": {
                            "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                        },
                        "viewImage": {
                            "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                        },
                        "baseImage": {
                            "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                        },
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
            },
        },
        {
            "_id": "original-fr",
            "guid": "original-fr",
            "type": "text",
            "version": 1,
            "profile": "belga_text",
            "pubstatus": "usable",
            "format": "HTML",
            "template": ObjectId("5c94ead2fe985e1c5776ddca"),
            "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
            "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "firstpublished": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "state": "published",
            "source": "Belga",
            "priority": 6,
            "urgency": 4,
            "language": "fr",
            "headline": "Old my beer",
            "keywords": ["europe", "Prague", "CZ", "Skoda"],
            "slugline": "skoda scala",
            "byline": "BELGA",
            "translation_id": "original",
            "translated_from": "original",
            "associations": {
                "editor_0": {
                    "renditions": {
                        "original": {
                            "width": 5472,
                            "height": 3648,
                            "href": "https://3.t.cdn.belga.be/belgaimage:154620545:1800x650:w?v=5d5aaa94&m=njopcomo",
                        },
                        "thumbnail": {
                            "href": "http://p.cdn.belga.be/belgaimage:154620545:600x140?v=5d5aaa94&m=kmjjblom"
                        },
                        "viewImage": {
                            "href": "https://3.t.cdn.belga.be/belgaimage:154620545:800x800:w?v=5d5aaa94&m=hdccpkpj"
                        },
                        "baseImage": {
                            "href": "https://3.t.cdn.belga.be/belgaimage:154620545:1800x650:w?v=5d5aaa94&m=njopcomo"
                        },
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
                        },
                        "thumbnail": {
                            "href": "http://p.cdn.belga.be/belgaimage:154670415:600x140?v=5d5aaa94&m=fcgloioh"
                        },
                        "viewImage": {
                            "href": "https://2.t.cdn.belga.be/belgaimage:154670415:800x800:w?v=5d5aaa94&m=ebedljnc"
                        },
                        "baseImage": {
                            "href": "https://0.t.cdn.belga.be/belgaimage:154670415:1800x650:w?v=5d5aaa94&m=ablplddf"
                        },
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
                        },
                        "thumbnail": {
                            "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                        },
                        "viewImage": {
                            "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                        },
                        "baseImage": {
                            "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                        },
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
            },
        },
        {
            "_id": "update-1",
            "guid": "update-1",
            "type": "text",
            "version": 1,
            "profile": "belga_text",
            "pubstatus": "usable",
            "format": "HTML",
            "template": ObjectId("5c94ead2fe985e1c5776ddca"),
            "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
            "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "firstpublished": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "state": "published",
            "source": "Belga",
            "priority": 6,
            "urgency": 4,
            "language": "nl",
            "headline": "New Skoda Scala 1",
            "keywords": ["europe", "Prague", "CZ", "Skoda"],
            "slugline": "skoda scala",
            "byline": "BELGA",
            "rewritten_by": "update-2",
            "rewrite_of": "original",
            "rewrite_sequence": 1,
            "translations": ["update-1-fr"],
        },
        {
            "_id": "update-1-fr",
            "guid": "update-1-fr",
            "type": "text",
            "version": 1,
            "profile": "belga_text",
            "pubstatus": "usable",
            "format": "HTML",
            "template": ObjectId("5c94ead2fe985e1c5776ddca"),
            "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
            "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "firstpublished": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "state": "in_progress",
            "source": "Belga",
            "priority": 6,
            "urgency": 4,
            "language": "fr",
            "headline": "Old my beer",
            "keywords": ["europe", "Prague", "CZ", "Skoda"],
            "slugline": "skoda scala",
            "byline": "BELGA",
            "translation_id": "update-1",
            "translated_from": "update-1",
            "associations": {
                "editor_0": {
                    "renditions": {
                        "original": {
                            "width": 5472,
                            "height": 3648,
                            "href": "https://3.t.cdn.belga.be/belgaimage:154620545:1800x650:w?v=5d5aaa94&m=njopcomo",
                        },
                        "thumbnail": {
                            "href": "http://p.cdn.belga.be/belgaimage:154620545:600x140?v=5d5aaa94&m=kmjjblom"
                        },
                        "viewImage": {
                            "href": "https://3.t.cdn.belga.be/belgaimage:154620545:800x800:w?v=5d5aaa94&m=hdccpkpj"
                        },
                        "baseImage": {
                            "href": "https://3.t.cdn.belga.be/belgaimage:154620545:1800x650:w?v=5d5aaa94&m=njopcomo"
                        },
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
                        },
                        "thumbnail": {
                            "href": "http://p.cdn.belga.be/belgaimage:154670415:600x140?v=5d5aaa94&m=fcgloioh"
                        },
                        "viewImage": {
                            "href": "https://2.t.cdn.belga.be/belgaimage:154670415:800x800:w?v=5d5aaa94&m=ebedljnc"
                        },
                        "baseImage": {
                            "href": "https://0.t.cdn.belga.be/belgaimage:154670415:1800x650:w?v=5d5aaa94&m=ablplddf"
                        },
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
                        },
                        "thumbnail": {
                            "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                        },
                        "viewImage": {
                            "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                        },
                        "baseImage": {
                            "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                        },
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
            },
        },
        {
            "_id": "update-2",
            "guid": "update-2",
            "type": "text",
            "version": 1,
            "profile": "belga_text",
            "pubstatus": "usable",
            "format": "HTML",
            "template": ObjectId("5c94ead2fe985e1c5776ddca"),
            "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
            "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "firstpublished": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "state": "published",
            "source": "Belga",
            "priority": 6,
            "urgency": 4,
            "language": "nl",
            "headline": "New Skoda Scala 2",
            "keywords": ["europe", "Prague", "CZ", "Skoda"],
            "slugline": "skoda scala",
            "byline": "BELGA",
            "rewrite_of": "update-1",
            "rewrite_sequence": 2,
        },
    )

    users = (
        {
            "_id": ObjectId("5d385f31fe985ec67a0ca583"),
            "username": "adm",
            "password": "blabla",
            "email": "admin@example.com",
            "user_type": "administrator",
            "is_active": True,
            "needs_activation": False,
            "is_author": True,
            "is_enabled": True,
            "display_name": "John Smith",
            "sign_off": "ADM",
            "first_name": "John",
            "last_name": "Smith",
            "role": ObjectId("5d542206c04280bc6d6157f9"),
        },
    )

    roles = (
        {
            "_id": ObjectId("5d542206c04280bc6d6157f9"),
            "author_role": "AUTHOR",
            "editor_role": "AUTHOR",
        },
    )

    vocabularies = (
        {
            "_id": "belga-coverage-new",
            "field_type": "custom",
            "items": [],
            "type": "manageable",
            "schema": {"name": {}, "qcode": {}, "parent": {}},
            "service": {"all": 1},
            "custom_field_type": "belga.coverage",
            "display_name": "belga coverage new",
            "unique_field": "qcode",
        },
    )

    subscriber = {
        "_id": "some_id",
        "name": "Dev Subscriber",
    }

    @mock.patch(
        "superdesk.publish.subscribers.SubscribersService.generate_sequence_number",
        lambda s, sub: 1,
    )
    def setUp(self):
        init_app(self.app)
        self.app.data.insert("users", self.users)
        self.app.data.insert("archive", self.archive)
        self.app.data.insert("roles", self.roles)
        self.app.data.insert("vocabularies", self.vocabularies)

        self.article["state"] = "published"
        self.formatter = BelgaNewsML12Formatter()
        seq, doc = self.formatter.format(self.article, self.subscriber)[0]
        self.newsml = etree.XML(
            bytes(bytearray(doc, encoding=BelgaNewsML12Formatter.ENCODING))
        )

    def test_newsitemid(self):
        # NewsML -> NewsItem -> Identification
        self.assertEqual(
            self.newsml.xpath("NewsItem/Identification/NewsIdentifier/NewsItemId")[
                0
            ].text,
            "original",
        )

    def test_1_level_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent
        newscomponent_1_level = self.newsml.xpath("NewsItem/NewsComponent")[0]
        self.assertDictEqual(
            dict(newscomponent_1_level.attrib),
            {"Duid": "original", "{http://www.w3.org/XML/1998/namespace}lang": "nl"},
        )

    def test_belga_text_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        expected = (
            ("original", "nl"),
            ("urn:belga.be:image:154620545", "nl"),
            ("urn:belga.be:image:154670415", "nl"),
            ("urn:belga.be:coverage:6690595", "nl"),
            ("urn:belga.be:360archive:77777777", "nl"),
            ("original-fr", "fr"),
            ("urn:belga.be:image:154620545", "fr"),
            ("urn:belga.be:image:154670415", "fr"),
            ("urn:belga.be:coverage:6690595", "fr"),
            ("urn:belga.be:360archive:77777777", "nl"),
            ("update-1", "nl"),
            ("update-2", "nl"),
        )
        for i, newscomponent_2_level in enumerate(
            self.newsml.xpath("NewsItem/NewsComponent/NewsComponent")
        ):
            self.assertDictEqual(
                dict(newscomponent_2_level.attrib),
                {
                    "Duid": expected[i][0],
                    "{http://www.w3.org/XML/1998/namespace}lang": expected[i][1],
                },
            )


class BelgaNewsML12Formatter_NotPublishedItemsChainTest(
    BelgaNewsML12Formatter_ItemsChainTest
):
    archive = (
        {
            "_id": "original",
            "guid": "original",
            "type": "text",
            "version": 1,
            "profile": "belga_text",
            "pubstatus": "usable",
            "format": "HTML",
            "template": ObjectId("5c94ead2fe985e1c5776ddca"),
            "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
            "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "firstpublished": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "state": "in_progress",
            "source": "Belga",
            "priority": 6,
            "urgency": 4,
            "language": "nl",
            "headline": "New Skoda Scala",
            "keywords": ["europe", "Prague", "CZ", "Skoda"],
            "slugline": "skoda scala",
            "byline": "BELGA",
            "rewritten_by": "update-1",
            "translation_id": "original",
            "translations": ["original-fr"],
            "associations": {},
        },
        {
            "_id": "original-fr",
            "guid": "original-fr",
            "type": "text",
            "version": 1,
            "profile": "belga_text",
            "pubstatus": "usable",
            "format": "HTML",
            "template": ObjectId("5c94ead2fe985e1c5776ddca"),
            "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
            "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "firstpublished": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "state": "published",
            "source": "Belga",
            "priority": 6,
            "urgency": 4,
            "language": "fr",
            "headline": "Old my beer",
            "keywords": ["europe", "Prague", "CZ", "Skoda"],
            "slugline": "skoda scala",
            "byline": "BELGA",
            "translation_id": "original",
            "translated_from": "original",
            "associations": {},
        },
        {
            "_id": "update-1",
            "guid": "update-1",
            "type": "text",
            "version": 1,
            "profile": "belga_text",
            "pubstatus": "usable",
            "format": "HTML",
            "template": ObjectId("5c94ead2fe985e1c5776ddca"),
            "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
            "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "firstpublished": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "state": "published",
            "source": "Belga",
            "priority": 6,
            "urgency": 4,
            "language": "nl",
            "headline": "New Skoda Scala 1",
            "keywords": ["europe", "Prague", "CZ", "Skoda"],
            "slugline": "skoda scala",
            "byline": "BELGA",
            "rewritten_by": "update-2",
            "rewrite_of": "original",
            "rewrite_sequence": 1,
            "translations": ["update-1-fr"],
        },
        {
            "_id": "update-1-fr",
            "guid": "update-1-fr",
            "type": "text",
            "version": 1,
            "profile": "belga_text",
            "pubstatus": "usable",
            "format": "HTML",
            "template": ObjectId("5c94ead2fe985e1c5776ddca"),
            "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
            "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "firstpublished": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "state": "in_progress",
            "source": "Belga",
            "priority": 6,
            "urgency": 4,
            "language": "fr",
            "headline": "Old my beer",
            "keywords": ["europe", "Prague", "CZ", "Skoda"],
            "slugline": "skoda scala",
            "byline": "BELGA",
            "translation_id": "update-1",
            "translated_from": "update-1",
            "associations": {},
        },
        {
            "_id": "update-2",
            "guid": "update-2",
            "type": "text",
            "version": 1,
            "profile": "belga_text",
            "pubstatus": "usable",
            "format": "HTML",
            "template": ObjectId("5c94ead2fe985e1c5776ddca"),
            "_updated": datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
            "_created": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "firstpublished": datetime.datetime(
                2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC
            ),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "state": "published",
            "source": "Belga",
            "priority": 6,
            "urgency": 4,
            "language": "nl",
            "headline": "New Skoda Scala 2",
            "keywords": ["europe", "Prague", "CZ", "Skoda"],
            "slugline": "skoda scala",
            "byline": "BELGA",
            "rewrite_of": "update-1",
            "rewrite_sequence": 2,
        },
    )

    @mock.patch(
        "superdesk.publish.subscribers.SubscribersService.generate_sequence_number",
        lambda s, sub: 1,
    )
    def setUp(self):
        init_app(self.app)
        self.app.data.insert("users", self.users)
        self.app.data.insert("archive", self.archive)
        self.app.data.insert("roles", self.roles)
        self.app.data.insert("vocabularies", self.vocabularies)

        self.article["state"] = "published"
        self.formatter = BelgaNewsML12Formatter()
        seq, doc = self.formatter.format(self.article, self.subscriber)[0]
        self.newsml = etree.XML(
            bytes(bytearray(doc, encoding=BelgaNewsML12Formatter.ENCODING))
        )

    def test_newsitemid(self):
        # NewsML -> NewsItem -> Identification
        self.assertEqual(
            self.newsml.xpath("NewsItem/Identification/NewsIdentifier/NewsItemId")[
                0
            ].text,
            "original",
        )

    def test_1_level_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent
        newscomponent_1_level = self.newsml.xpath("NewsItem/NewsComponent")[0]
        self.assertDictEqual(
            dict(newscomponent_1_level.attrib),
            {"Duid": "original", "{http://www.w3.org/XML/1998/namespace}lang": "nl"},
        )

    def test_belga_text_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        expected = (("original-fr", "fr"), ("update-1", "nl"), ("update-2", "nl"))
        for i, newscomponent_2_level in enumerate(
            self.newsml.xpath("NewsItem/NewsComponent/NewsComponent")
        ):
            self.assertDictEqual(
                dict(newscomponent_2_level.attrib),
                {
                    "Duid": expected[i][0],
                    "{http://www.w3.org/XML/1998/namespace}lang": expected[i][1],
                },
            )


belga_514_fixture = fixtures_path / "belga-newsml-1.2-SDBELGA-514.json"
with belga_514_fixture.open() as f:
    belga_514_articles = json.load(f)


class BelgaNewsML12Formatter_ItemsChainImageTest(TestCase):
    article = belga_514_articles[0]
    archive = belga_514_articles

    users = (
        {
            "_id": "5ddfdba06dd032cb672d4780",
            "username": "adm",
            "password": "blabla",
            "email": "admin@example.com",
            "user_type": "administrator",
            "is_active": True,
            "needs_activation": False,
            "is_author": True,
            "is_enabled": True,
            "display_name": "John Smith",
            "sign_off": "ADM",
            "first_name": "John",
            "last_name": "Smith",
            "role": ObjectId("5d542206c04280bc6d6157f9"),
        },
    )

    roles = (
        {
            "_id": ObjectId("5d542206c04280bc6d6157f9"),
            "author_role": "AUTHOR",
            "editor_role": "AUTHOR",
        },
    )

    vocabularies = (
        {
            "_id": "belga-coverage-new",
            "field_type": "custom",
            "items": [],
            "type": "manageable",
            "schema": {"name": {}, "qcode": {}, "parent": {}},
            "service": {"all": 1},
            "custom_field_type": "belga.coverage",
            "display_name": "belga coverage new",
            "unique_field": "qcode",
        },
    )

    subscriber = {
        "_id": "some_id",
        "name": "Dev Subscriber",
    }

    @mock.patch(
        "superdesk.publish.subscribers.SubscribersService.generate_sequence_number",
        lambda s, sub: 1,
    )
    def setUp(self):
        init_app(self.app)
        self.app.data.insert("users", self.users)
        self.app.data.insert("archive", self.archive)
        self.app.data.insert("roles", self.roles)
        self.app.data.insert("vocabularies", self.vocabularies)

        self.formatter = BelgaNewsML12Formatter()
        seq, doc = self.formatter.format(self.article, self.subscriber)[0]
        self.newsml = etree.XML(
            bytes(bytearray(doc, encoding=BelgaNewsML12Formatter.ENCODING))
        )

    def test_picture_with_same_language_not_exported_multiple_times(self):
        """SDBELGA-514 and SDBELGA-597 regression test"""
        image_roles = self.newsml.xpath('//Role[@FormalName="Image"]')
        # modification in SDBELGA-514 for SDBELGA-597
        self.assertEqual(len(image_roles), 2)
