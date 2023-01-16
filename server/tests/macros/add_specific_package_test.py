import unittest

from belga.macros.add_specific_package import update_package


class AddSpecificPackage(unittest.TestCase):
    def test_add_specific_package_macro(self):
        item = {
            "headline": "test1",
            "type": "text",
            "state": "fetched",
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
            "language": "de",
        }
        update_package(item)
        self.assertEqual(
            item.get("subject")[1],
            {
                "name": "BTL/ECO",
                "qcode": "BTL/ECO",
                "parent": "BTL",
                "scheme": "services-products",
            },
        )

        item["language"] = "fr"
        update_package(item)
        self.assertEqual(
            item.get("subject")[1],
            {
                "name": "EXT/ECO",
                "qcode": "EXT/ECO",
                "parent": "EXT",
                "scheme": "services-products",
            },
        )
