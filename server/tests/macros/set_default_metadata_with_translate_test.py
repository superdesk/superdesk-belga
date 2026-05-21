from bson import ObjectId
from unittest.mock import patch
from tests.mock import resources
from superdesk import get_resource_service

# from superdesk.tests import TestCase
from superdesk.tests import utils as test_utils
from superdesk.errors import StopDuplication
from belga.macros.set_default_metadata_with_translate import (
    set_default_metadata_with_translate,
)

from .. import TestCase


class SetDefaultMetadataWithTranslateTestCase(TestCase):
    async def test_no_destination_data(self):
        item = {
            "headline": "test headline",
            "slugine": "test slugline",
            "keywords": ["foo", "bar"],
        }
        self.app.data.insert("archive", [item])
        self.assertIsNone(await set_default_metadata_with_translate(item))

    async def test_no_template_language(self):
        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "name": "Politic Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_1",
                    "desk_language": "fr",
                    "source": "politic",
                }
            ],
        )
        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ObjectId("5d385f31fe985ec67a0ca583"),
                    "name": "Incoming Stage 2",
                    "default_incoming": True,
                    "desk_order": 2,
                    "content_expiry": None,
                    "working_stage": False,
                    "is_visible": True,
                    "desk": ObjectId("5d385f17fe985ec5e1a78b49"),
                }
            ],
        )
        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": "content_template_1",
                    "template_name": "belga text",
                    "is_public": True,
                    "data": {
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "headline": "",
                        "subject": [
                            {
                                "name": "INT/GENERAL",
                                "qcode": "INT/GENERAL",
                                "parent": "INT",
                                "scheme": "services-products",
                            },
                            {
                                "name": "default",
                                "qcode": "default",
                                "scheme": "distribution",
                            },
                        ],
                        "keywords": ["some", "keyword"],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )
        item = {
            "_id": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "guid": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "headline": "test headline",
            "slugine": "test slugline",
            "state": "published",
            "type": "text",
            "keywords": ["foo", "bar"],
        }
        self.app.data.insert("archive", [item])
        with self.assertRaises(StopDuplication):
            await set_default_metadata_with_translate(
                item,
                dest_desk_id=ObjectId("5d385f17fe985ec5e1a78b49"),
                dest_stage_id=ObjectId("5d385f31fe985ec67a0ca583"),
            )
        archive_service = get_resource_service("archive")
        new_item = archive_service.find_one(
            req=None,
            original_id="urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
        )
        self.assertNotIn("translated_from", new_item)

    async def test_duplicate(self):
        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "name": "Politic Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_1",
                    "desk_language": "fr",
                    "source": "politic",
                }
            ],
        )
        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ObjectId("5d385f31fe985ec67a0ca583"),
                    "name": "Incoming Stage 2",
                    "default_incoming": True,
                    "desk_order": 2,
                    "content_expiry": None,
                    "working_stage": False,
                    "is_visible": True,
                    "desk": ObjectId("5d385f17fe985ec5e1a78b49"),
                }
            ],
        )
        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": "content_template_1",
                    "template_name": "belga text",
                    "is_public": True,
                    "data": {
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "headline": "",
                        "subject": [
                            {
                                "name": "INT/GENERAL",
                                "qcode": "INT/GENERAL",
                                "parent": "INT",
                                "scheme": "services-products",
                            },
                            {
                                "name": "default",
                                "qcode": "default",
                                "scheme": "distribution",
                            },
                        ],
                        "language": "en",
                        "keywords": ["some", "keyword"],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )
        item = {
            "_id": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "guid": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "headline": "test headline",
            "slugine": "test slugline",
            "state": "published",
            "type": "text",
            "keywords": ["foo", "bar"],
            "language": "en",
        }
        self.app.data.insert("archive", [item])
        with self.assertRaises(StopDuplication):
            await set_default_metadata_with_translate(
                item,
                dest_desk_id=ObjectId("5d385f17fe985ec5e1a78b49"),
                dest_stage_id=ObjectId("5d385f31fe985ec67a0ca583"),
            )

        archive_service = get_resource_service("archive")
        new_item = archive_service.find_one(
            req=None,
            original_id="urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
        )
        self.assertNotIn("translated_from", new_item)

    async def test_translate(self):
        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "name": "Politic Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_1",
                    "desk_language": "fr",
                    "source": "politic",
                }
            ],
        )
        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ObjectId("5d385f31fe985ec67a0ca583"),
                    "name": "Incoming Stage 2",
                    "default_incoming": True,
                    "desk_order": 2,
                    "content_expiry": None,
                    "working_stage": False,
                    "is_visible": True,
                    "desk": ObjectId("5d385f17fe985ec5e1a78b49"),
                }
            ],
        )
        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": "content_template_1",
                    "template_name": "belga text",
                    "is_public": True,
                    "data": {
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "headline": "",
                        "subject": [
                            {
                                "name": "INT/GENERAL",
                                "qcode": "INT/GENERAL",
                                "parent": "INT",
                                "scheme": "services-products",
                            },
                            {
                                "name": "default",
                                "qcode": "default",
                                "scheme": "distribution",
                            },
                        ],
                        "language": "en",
                        "keywords": ["some", "keyword"],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )
        item = {
            "_id": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "guid": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "headline": "test headline",
            "slugine": "test slugline",
            "state": "published",
            "type": "text",
            "keywords": ["foo", "bar"],
            "language": "fr",
        }
        self.app.data.insert("archive", [item])
        with self.assertRaises(StopDuplication):
            await set_default_metadata_with_translate(
                item,
                dest_desk_id=ObjectId("5d385f17fe985ec5e1a78b49"),
                dest_stage_id=ObjectId("5d385f31fe985ec67a0ca583"),
            )
        archive_service = get_resource_service("archive")
        new_item = archive_service.find_one(
            req=None,
            original_id="urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
        )
        self.assertEqual(new_item["translated_from"], item["guid"])

    async def test_keywords_not_to_overwrite(self):
        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "name": "Politic Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_1",
                    "desk_language": "fr",
                    "source": "politic",
                }
            ],
        )
        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ObjectId("5d385f31fe985ec67a0ca583"),
                    "name": "Incoming Stage 2",
                    "default_incoming": True,
                    "desk_order": 2,
                    "content_expiry": None,
                    "working_stage": False,
                    "is_visible": True,
                    "desk": ObjectId("5d385f17fe985ec5e1a78b49"),
                }
            ],
        )
        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": "content_template_1",
                    "template_name": "belga text",
                    "is_public": True,
                    "data": {
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "headline": "",
                        "language": "en",
                        "keywords": ["some", "keyword"],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )
        item = {
            "_id": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "guid": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "headline": "test headline",
            "slugine": "test slugline",
            "state": "published",
            "type": "text",
            "keywords": ["foo", "bar"],
            "language": "fr",
        }
        self.app.data.insert("archive", [item])
        with self.assertRaises(StopDuplication):
            await set_default_metadata_with_translate(
                item,
                dest_desk_id=ObjectId("5d385f17fe985ec5e1a78b49"),
                dest_stage_id=ObjectId("5d385f31fe985ec67a0ca583"),
                overwrite_keywords=False,
            )
        archive_service = get_resource_service("archive")
        new_item = archive_service.find_one(
            req=None,
            original_id="urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
        )
        self.assertEqual(new_item["translated_from"], item["guid"])

        self.assertEqual(["foo", "bar"], new_item["keywords"])

    async def test_keywords_to_overwrite(self):
        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "name": "Politic Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_1",
                    "desk_language": "fr",
                    "source": "politic",
                }
            ],
        )
        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ObjectId("5d385f31fe985ec67a0ca583"),
                    "name": "Incoming Stage 2",
                    "default_incoming": True,
                    "desk_order": 2,
                    "content_expiry": None,
                    "working_stage": False,
                    "is_visible": True,
                    "desk": ObjectId("5d385f17fe985ec5e1a78b49"),
                }
            ],
        )
        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": "content_template_1",
                    "template_name": "belga text",
                    "is_public": True,
                    "data": {
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "headline": "",
                        "language": "en",
                        "keywords": ["some", "keyword"],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )
        item = {
            "_id": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "guid": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "headline": "test headline",
            "slugine": "test slugline",
            "state": "published",
            "type": "text",
            "keywords": ["foo", "bar"],
            "language": "fr",
        }
        self.app.data.insert("archive", [item])
        with self.assertRaises(StopDuplication):
            await set_default_metadata_with_translate(
                item,
                dest_desk_id=ObjectId("5d385f17fe985ec5e1a78b49"),
                dest_stage_id=ObjectId("5d385f31fe985ec67a0ca583"),
                overwrite_keywords=True,
            )
        archive_service = get_resource_service("archive")
        new_item = archive_service.find_one(
            req=None,
            original_id="urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
        )

        self.assertEqual(["some", "keyword"], new_item["keywords"])

    async def test_belga_keywords(self):
        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "name": "Politic Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_1",
                    "desk_language": "fr",
                    "source": "politic",
                }
            ],
        )
        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ObjectId("5d385f31fe985ec67a0ca583"),
                    "name": "Incoming Stage 2",
                    "default_incoming": True,
                    "desk_order": 2,
                    "content_expiry": None,
                    "working_stage": False,
                    "is_visible": True,
                    "desk": ObjectId("5d385f17fe985ec5e1a78b49"),
                }
            ],
        )
        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": "content_template_1",
                    "template_name": "belga text",
                    "is_public": True,
                    "data": {
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "headline": "",
                        "language": "en",
                        "keywords": ["some", "keyword"],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )
        item = {
            "_id": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "guid": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "headline": "test headline",
            "slugine": "test slugline",
            "state": "published",
            "type": "text",
            "subject": [
                {
                    "name": "BRIEF",
                    "qcode": "BRIEF",
                    "translations": {"name": {"nl": "BRIEF", "fr": "BRIEF"}},
                    "scheme": "belga-keywords",
                }
            ],
            "keywords": ["foo", "bar"],
            "language": "fr",
        }
        self.app.data.insert("archive", [item])
        with self.assertRaises(StopDuplication):
            await set_default_metadata_with_translate(
                item,
                dest_desk_id=ObjectId("5d385f17fe985ec5e1a78b49"),
                dest_stage_id=ObjectId("5d385f31fe985ec67a0ca583"),
            )
        archive_service = get_resource_service("archive")
        new_item = archive_service.find_one(
            req=None,
            original_id="urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
        )

        self.assertEqual(item["subject"], new_item["subject"])

    async def test_duplicate_item(self):
        # SDBELGA-538

        ids = dict(
            filter_conditions=[ObjectId(), ObjectId()],
            content_filters=[ObjectId(), ObjectId()],
            desks=[ObjectId(), ObjectId()],
            stages=[ObjectId(), ObjectId()],
            content_templates=[ObjectId(), ObjectId()],
            destination=[ObjectId(), ObjectId()],
        )

        await test_utils.post_items(
            "filter_conditions",
            [
                {
                    "_id": ids["filter_conditions"][0],
                    "operator": "in",
                    "field": "services-products",
                    "value": "BIN/ALG",
                    "name": "Bin/alg filter_c",
                },
                {
                    "_id": ids["filter_conditions"][1],
                    "operator": "in",
                    "field": "services-products",
                    "value": "BIN/ECO",
                    "name": "Bin/eco filter_c",
                },
            ],
        )
        content_filter = [
            {
                "_id": ids["content_filters"][0],
                "name": "Bin/ALG Filter",
                "content_filter": [
                    {"expression": {"fc": [ids["filter_conditions"][0]]}}
                ],
            },
            {
                "_id": ids["content_filters"][1],
                "name": "Bin/ECO Filter",
                "content_filter": [
                    {"expression": {"fc": [ids["filter_conditions"][1]]}}
                ],
            },
        ]
        await test_utils.post_items("content_filters", content_filter)

        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ids["desks"][0],
                    "name": "Politic Desk",
                    "default_content_profile": "belga_text-1",
                    "default_content_template": ids["content_templates"][0],
                    "desk_language": "fr",
                    "source": "politic",
                },
                {
                    "_id": ids["desks"][1],
                    "name": "Sports Desk",
                    "default_content_profile": "belga_text-2",
                    "default_content_template": ids["content_templates"][1],
                    "desk_language": "en",
                    "source": "sports",
                },
            ],
        )
        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ids["stages"][0],
                    "name": "Incoming Stage 2",
                    "default_incoming": True,
                    "desk_order": 1,
                    "content_expiry": None,
                    "working_stage": False,
                    "is_visible": True,
                    "desk": ids["desks"][0],
                },
                {
                    "_id": ids["stages"][1],
                    "name": "Incoming Stage 2",
                    "default_incoming": True,
                    "desk_order": 2,
                    "content_expiry": None,
                    "working_stage": False,
                    "is_visible": True,
                    "desk": ids["desks"][1],
                },
            ],
        )

        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": ids["content_templates"][0],
                    "template_name": "belga text one",
                    "is_public": True,
                    "data": {
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "headline": "",
                        "language": "en",
                        "keywords": ["some", "keyword"],
                        "body_html": "",
                    },
                    "template_type": "create",
                },
                {
                    "_id": ids["content_templates"][1],
                    "template_name": "belga text two",
                    "is_public": True,
                    "data": {
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "headline": "",
                        "language": "en",
                        "keywords": ["some", "keyword"],
                        "body_html": "",
                    },
                    "template_type": "create",
                },
            ],
        )

        destination = [
            {
                "_id": ids["destination"][0],
                "is_active": True,
                "name": "BIN/ALG",
                "filter": ids["content_filters"][0],
                "desk": "123",
                "stage": "213",
                "macro": "Set Default Metadata With Translate",
            },
            {
                "_id": ids["destination"][1],
                "is_active": True,
                "name": "BIN/ECO",
                "filter": ids["content_filters"][0],
                "desk": "456",
                "stage": "214",
                "macro": "Set Default Metadata With Translate",
            },
        ]
        self.app.data.insert("internal_destinations", destination)

        item = {
            "_id": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "guid": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "headline": "test headline",
            "slugine": "test slugline",
            "state": "published",
            "type": "text",
            "subject": [
                {
                    "name": "BIN/ALG",
                    "qcode": "BIN/ALG",
                    "parent": "BIN",
                    "scheme": "services-products",
                },
                {
                    "name": "BIN/ECO",
                    "qcode": "BIN/ECO",
                    "parent": "BIN",
                    "scheme": "services-products",
                },
            ],
            "keywords": ["foo", "bar"],
            "language": "fr",
        }

        self.app.data.insert("archive", [item])
        with self.assertRaises(StopDuplication):
            await set_default_metadata_with_translate(
                item,
                dest_desk_id=ids["desks"][0],
                dest_stage_id=ids["stages"][0],
                internal_destination=destination[0],
            )

    async def test_preserve_btl_to_ext_eco_package(self):
        # SDBELGA-720

        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "name": "Economics Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_eco",
                    "desk_language": "nl",
                    "source": "eco",
                }
            ],
        )
        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ObjectId("5d385f31fe985ec67a0ca583"),
                    "desk": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "default_incoming": True,
                    "desk_order": 1,
                    "is_visible": True,
                }
            ],
        )
        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": "content_template_eco",
                    "template_name": "eco template",
                    "is_public": True,
                    "data": {
                        "language": "fr",
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "subject": [],
                        "keywords": [],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )

        item = {
            "_id": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "guid": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "language": "nl",
            "state": "published",
            "type": "text",
            "subject": [
                {
                    "scheme": "services-products",
                    "qcode": "BTL/ECO",
                    "parent": "BTL",
                    "name": "BTL/ECO",
                }
            ],
        }
        self.app.data.insert("archive", [item])

        with patch.dict("superdesk.resources", resources):
            with self.assertRaises(StopDuplication):
                await set_default_metadata_with_translate(
                    item,
                    dest_desk_id=ObjectId("5d385f17fe985ec5e1a78b49"),
                    dest_stage_id=ObjectId("5d385f31fe985ec67a0ca583"),
                )

            new_item = get_resource_service("archive").find_one(
                req=None,
                original_id="urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            )
            services = [
                s for s in new_item["subject"] if s["scheme"] == "services-products"
            ]
            self.assertEqual(len(services), 1)
            self.assertEqual(services[0]["qcode"], "EXT/ECO")

    async def test_preserve_ext_to_btl_eco_package(self):

        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "name": "Economics Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_eco",
                    "desk_language": "fr",
                    "source": "eco",
                }
            ],
        )
        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ObjectId("5d385f31fe985ec67a0ca583"),
                    "desk": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "default_incoming": True,
                    "desk_order": 1,
                    "is_visible": True,
                }
            ],
        )
        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": "content_template_eco",
                    "template_name": "eco template",
                    "is_public": True,
                    "data": {
                        "language": "nl",
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "subject": [],
                        "keywords": [],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )

        item = {
            "_id": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "guid": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "language": "fr",
            "state": "published",
            "type": "text",
            "subject": [
                {
                    "scheme": "services-products",
                    "qcode": "EXT/ECO",
                    "parent": "EXT",
                    "name": "EXT/ECO",
                }
            ],
        }
        self.app.data.insert("archive", [item])

        with patch.dict("superdesk.resources", resources):
            with self.assertRaises(StopDuplication):
                await set_default_metadata_with_translate(
                    item,
                    dest_desk_id=ObjectId("5d385f17fe985ec5e1a78b49"),
                    dest_stage_id=ObjectId("5d385f31fe985ec67a0ca583"),
                )

            new_item = get_resource_service("archive").find_one(
                req=None,
                original_id="urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            )
            services = [
                s for s in new_item["subject"] if s["scheme"] == "services-products"
            ]
            self.assertEqual(len(services), 1)
            self.assertEqual(services[0]["qcode"], "BTL/ECO")

    async def test_removes_old_eco_and_adds_mapped(self):
        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "name": "Economics Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_eco_fr",
                    "desk_language": "nl",
                    "source": "eco",
                }
            ],
        )

        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ObjectId("5d385f31fe985ec67a0ca583"),
                    "desk": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "default_incoming": True,
                    "desk_order": 1,
                    "is_visible": True,
                }
            ],
        )

        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": "content_template_eco_fr",
                    "template_name": "eco fr template",
                    "is_public": True,
                    "data": {
                        "language": "fr",
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "subject": [
                            {"qcode": "INT/ECO", "scheme": "services-products"}
                        ],
                        "keywords": [],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )

        item = {
            "_id": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "guid": "urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            "language": "nl",
            "state": "published",
            "type": "text",
            "subject": [
                {
                    "scheme": "services-products",
                    "qcode": "BTL/ECO",
                    "parent": "BTL",
                    "name": "BTL/ECO",
                }
            ],
        }
        self.app.data.insert("archive", [item])

        with patch.dict("superdesk.resources", resources):
            with self.assertRaises(StopDuplication):
                await set_default_metadata_with_translate(
                    item,
                    dest_desk_id=ObjectId("5d385f17fe985ec5e1a78b49"),
                    dest_stage_id=ObjectId("5d385f31fe985ec67a0ca583"),
                )

            new_item = get_resource_service("archive").find_one(
                req=None,
                original_id="urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564",
            )

            eco_subjects = [
                s["qcode"]
                for s in new_item.get("subject", [])
                if s.get("scheme") == "services-products"
                and s.get("qcode", "").endswith("/ECO")
            ]

            self.assertEqual(
                len(eco_subjects),
                1,
                msg=f"Unexpected ECO subjects found: {eco_subjects}",
            )
            self.assertNotIn(
                "BTL/ECO", eco_subjects, msg="BTL/ECO should have been removed."
            )

    async def test_should_fallback_to_second_subject_if_first_does_not_match_filter(
        self,
    ):
        await test_utils.post_items(
            "filter_conditions",
            [
                {
                    "_id": ObjectId("7d385f17fe985ec5e1a78b49"),
                    "operator": "in",
                    "field": "subject",
                    "value": "EXT/ECO",
                    "name": "EXT/ECO filter",
                }
            ],
        )

        filter_id = ObjectId("7d385f17fe985ec5e1a78b50")

        await test_utils.post_items(
            "content_filters",
            [
                {
                    "_id": filter_id,
                    "name": "EXT/ECO Filter",
                    "content_filter": [
                        {"expression": {"fc": [ObjectId("7d385f17fe985ec5e1a78b49")]}}
                    ],
                }
            ],
        )

        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "name": "Economics Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_eco",
                    "desk_language": "en",
                    "source": "eco",
                }
            ],
        )
        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ObjectId("5d385f31fe985ec67a0ca583"),
                    "desk": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "default_incoming": True,
                    "desk_order": 1,
                    "is_visible": True,
                }
            ],
        )

        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": "content_template_eco",
                    "template_name": "eco template",
                    "is_public": True,
                    "data": {
                        "language": "en",
                        "profile": "belga_text",
                        "type": "text",
                        "pubstatus": "usable",
                        "format": "HTML",
                        "subject": [],
                        "keywords": [],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )

        # Internal destination points to content filter for EXT/ECO only
        internal_destination = {
            "_id": "dest_eco",
            "is_active": True,
            "name": "EXT/ECO",
            "filter": str(filter_id),
            "desk": "123",
            "stage": "213",
            "macro": "Set Default Metadata With Translate",
        }
        self.app.data.insert("internal_destinations", [internal_destination])

        # Item with two subjects: first one won't match, second one will
        item = {
            "_id": "urn:test:multi-subject-case",
            "guid": "urn:test:multi-subject-case",
            "language": "fr",
            "state": "published",
            "type": "text",
            "subject": [
                {
                    "scheme": "services-products",
                    "qcode": "EXT/POL",
                    "parent": "EXT",
                    "name": "EXT/POL",
                },
                {
                    "scheme": "services-products",
                    "qcode": "EXT/ECO",
                    "parent": "EXT",
                    "name": "EXT/ECO",
                },
            ],
        }

        self.app.data.insert("archive", [item])

        with patch.dict("superdesk.resources", resources):
            with self.assertRaises(StopDuplication):
                await set_default_metadata_with_translate(
                    item,
                    dest_desk_id=ObjectId("5d385f17fe985ec5e1a78b49"),
                    dest_stage_id=ObjectId("5d385f31fe985ec67a0ca583"),
                    internal_destination=internal_destination,
                )

            new_item = get_resource_service("archive").find_one(
                req=None,
                original_id="urn:test:multi-subject-case",
            )
            assert new_item is not None
            services = [
                s for s in new_item["subject"] if s["scheme"] == "services-products"
            ]
            self.assertEqual(len(services), 1)
            self.assertEqual(services[0]["qcode"], "BTL/ECO")
