# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
import os

from belga.command.contacts_import import import_contacts_via_json_file
from .. import TestCase


class BelgaContactImportTestCase(TestCase):
    filename = "contacts.json"

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, "./fixtures", self.filename))
        self.items = import_contacts_via_json_file(fixture)

    def test_import(self):
        self.assertEqual(len(self.items), 2)
        item = self.items[0]
        self.assertEqual(item["schema"], {"is_active": True, "public": True})
        self.assertEqual(item["organisation"], "Commune de Doische")
        self.assertEqual(item["first_name"], "André")
        self.assertEqual(item["last_name"], "Dricot")
        self.assertEqual(item["job_title"], "bourgmestre / burgemeester")
        self.assertEqual(
            item["contact_phone"],
            [
                {"number": "+32 82 21 47 20", "usage": "Business", "public": True},
                {"number": "+32 82 67 74 02", "usage": "Business", "public": True},
                {"number": "+32 82 67 74 02", "usage": "Confidential", "public": True},
            ],
        )
        self.assertEqual(item["fax"], "")
        self.assertEqual(
            item["contact_email"], ["André@gmail.com", "test@idsolutions.com.vn"]
        )
        self.assertEqual(item["website"], "http://www.doische.be")
        self.assertEqual(
            item["contact_address"],
            [
                "Rue M. Sandron 114\n\n5680 Doische",
                "rue des Tilleuls 84\n\n5680 Romer¿e",
            ],
        )
        self.assertEqual(item["keywords"], "POLITICS ")
        self.assertEqual(item["original_id"], "11223")
