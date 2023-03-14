from superdesk.tests import TestCase
from belga.macros.set_default_metadata import set_default_metadata


class SetDefaultMetadataTestCase(TestCase):
    def test_set_default_metadata(self):
        self.app.data.insert(
            "desks",
            [
                {
                    "_id": "desk_1",
                    "name": "Politic Desk",
                    "default_content_profile": "belga_text",
                    "default_content_template": "content_template_1",
                    "desk_language": "fr",
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
                        "language": "en",
                        "keywords": ["some", "keyword"],
                        "body_html": "",
                    },
                    "template_type": "create",
                }
            ],
        )

        item = {
            "headline": "test headline",
            "slugine": "test slugline",
            "keywords": ["foo", "bar"],
            "state": "ingested",
        }

        set_default_metadata(item, dest_desk_id="desk_1")
        self.assertEqual(item.get("keywords"), ["some", "keyword"])
        self.assertEqual(item.get("language"), "en")
        # packages
        self.assertIn(
            {
                "name": "INT/GENERAL",
                "qcode": "INT/GENERAL",
                "parent": "INT",
                "scheme": "services-products",
            },
            item["subject"],
        )

        self.assertIn(
            {"name": "default", "qcode": "default", "scheme": "distribution"},
            item["subject"],
        )

        self.assertIn(
            {
                "name": "BRIEF",
                "qcode": "BRIEF",
                "translations": {"name": {"nl": "BRIEF", "fr": "BRIEF"}},
                "scheme": "belga-keywords",
            },
            item["subject"],
        )
