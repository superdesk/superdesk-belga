from superdesk.tests import TestCase
from belga.macros.add_specific_package import update_package


class AddSpecificPackage(TestCase):
    def test_add_specific_package_macro(self):
        self.app.data.insert(
            "desks",
            [
                {
                    "_id": "desk_1",
                    "name": "Politic Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_1",
                    "desk_language": "en",
                    "source": "politic",
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
                        "language": "nl",
                        "keywords": ["some", "keyword"],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )

        item = {
            "headline": "test1",
            "type": "text",
            "language": "nl",
            "state": "ingested",
            "subject": [
                {
                    "name": "EXT/GEN",
                    "parent": "EXT",
                    "qcode": "EXT/GEN",
                    "scheme": "services-products",
                },
                {
                    "qcode": "05005002",
                    "name": "middle schools",
                    "parent": "05005000",
                    "scheme": None,
                },
            ],
        }

        dest_desk = {
            "_id": "desk_2",
            "name": "Politic Desk",
            "default_content_profile": "belga_text",
            "default_content_template": "content_template_1",
            "desk_language": "fr",
            "source": "politic",
        }

        update_package(item, desk=dest_desk)
        self.assertIn(
            {
                "name": "EXT/ECO",
                "qcode": "EXT/ECO",
                "parent": "EXT",
                "scheme": "services-products",
            },
            item["subject"],
        )
        self.assertEqual(item.get("keywords"), ["some", "keyword"])
        self.assertEqual(item.get("language"), "nl")
