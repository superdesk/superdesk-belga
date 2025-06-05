from bson import ObjectId
from unittest.mock import patch
from tests.mock import resources
from superdesk import get_resource_service
from superdesk.tests import TestCase
from superdesk.errors import StopDuplication
from belga.macros.set_default_metadata_with_translate import (
    set_default_metadata_with_translate,
)


class SetDefaultMetadataWithTranslateTestCase(TestCase):
    def test_no_destination_data(self):
        item = {
            "headline": "test headline",
            "slugine": "test slugline",
            "keywords": ["foo", "bar"],
        }
        self.app.data.insert("archive", [item])
        self.assertIsNone(set_default_metadata_with_translate(item))

    def test_no_template_language(self):
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
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
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

    def test_duplicate(self):
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
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
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

    def test_translate(self):
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
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
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

    def test_keywords_not_to_overwrite(self):
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
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
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

    def test_keywords_to_overwrite(self):
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
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
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

    def test_belga_keywords(self):
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
            "vocabularies",
            [
                {
                    "_id": "belga-keywords",
                    "display_name": "Belga Keywords",
                    "type": "manageable",
                    "selection_type": "multi selection",
                    "unique_field": "qcode",
                    "schema": {"name": {}, "qcode": {}, "translations": {}},
                    "service": {"all": 1},
                    "items": [
                        {
                            "name": "BRIEF",
                            "qcode": "BRIEF",
                            "is_active": True,
                            "translations": {"name": {"nl": "BRIEF", "fr": "BRIEF"}},
                        },
                        {
                            "name": "PREVIEW",
                            "qcode": "PREVIEW",
                            "is_active": True,
                            "translations": {
                                "name": {"nl": "VOORBERICHT", "fr": "AVANT-PAPIER"}
                            },
                        },
                    ],
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
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
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

    def test_duplicate_item(self):
        # SDBELGA-538

        self.app.data.insert(
            "filter_conditions",
            [
                {
                    "_id": ObjectId("6d385f17fe985ec5e1a78b49"),
                    "operator": "in",
                    "field": "services-products",
                    "value": "BIN/ALG",
                    "name": "Bin/alg filter_c",
                },
                {
                    "_id": ObjectId("7d385f17fe985ec5e1a78b49"),
                    "operator": "in",
                    "field": "services-products",
                    "value": "BIN/ECO",
                    "name": "Bin/eco filter_c",
                },
            ],
        )
        content_filter = [
            {
                "_id": 1,
                "name": "Bin/ALG Filter",
                "content_filter": [
                    {"expression": {"fc": [ObjectId("6d385f17fe985ec5e1a78b49")]}}
                ],
            },
            {
                "_id": 2,
                "name": "Bin/ECO Filter",
                "content_filter": [
                    {"expression": {"fc": [ObjectId("7d385f17fe985ec5e1a78b49")]}}
                ],
            },
        ]
        self.app.data.insert("content_filters", content_filter)

        self.app.data.insert(
            "desks",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b49"),
                    "name": "Politic Desk",
                    "default_content_profile": "belga_text-1",
                    "default_content_template": "content_template_1",
                    "desk_language": "fr",
                    "source": "politic",
                },
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a78b40"),
                    "name": "Sports Desk",
                    "default_content_profile": "belga_text-2",
                    "default_content_template": "content_template_2",
                    "desk_language": "en",
                    "source": "sports",
                },
            ],
        )
        self.app.data.insert(
            "stages",
            [
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a88b49"),
                    "name": "Incoming Stage 2",
                    "default_incoming": True,
                    "desk_order": 1,
                    "content_expiry": None,
                    "working_stage": False,
                    "is_visible": True,
                    "desk": ObjectId("5d385f17fe985ec5e1a78b49"),
                },
                {
                    "_id": ObjectId("5d385f17fe985ec5e1a89b49"),
                    "name": "Incoming Stage 2",
                    "default_incoming": True,
                    "desk_order": 2,
                    "content_expiry": None,
                    "working_stage": False,
                    "is_visible": True,
                    "desk": ObjectId("5d385f17fe985ec5e1a78b40"),
                },
            ],
        )

        self.app.data.insert(
            "content_templates",
            [
                {
                    "_id": "content_template_1",
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
                    "_id": "content_template_2",
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
                "_id": "desti_1",
                "is_active": True,
                "name": "BIN/ALG",
                "filter": "1",
                "desk": "123",
                "stage": "213",
                "macro": "Set Default Metadata With Translate",
            },
            {
                "_id": "desti_2",
                "is_active": True,
                "name": "BIN/ECO",
                "filter": "2",
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
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
            item,
            dest_desk_id=ObjectId("5d385f17fe985ec5e1a78b49"),
            dest_stage_id=ObjectId("5d385f17fe985ec5e1a88b49"),
            internal_destination=destination[0],
        )

    def test_preserve_btl_to_ext_eco_package(self):
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
                set_default_metadata_with_translate(
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

    def test_preserve_ext_to_btl_eco_package(self):

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
                set_default_metadata_with_translate(
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

    def test_removes_old_eco_and_adds_mapped(self):
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
                set_default_metadata_with_translate(
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
