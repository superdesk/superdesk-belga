# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import os

import superdesk
from superdesk import get_resource_service
from superdesk.io.feed_parsers.rfc822 import EMailRFC822FeedParser
from superdesk.tests import setup
from superdesk.users.services import UsersService

from belga.io.feeding_services.email_belga import EmailBelgaFeedingService
from tests import TestCase


class EmailBelgaIngestServiceTest(TestCase):
    filename = "email_attachment_belga.txt"

    def setUp(self):
        setup(context=self)
        with self.app.app_context():
            # mock one user:
            user_service = UsersService("users", backend=superdesk.get_backend())
            self.user_id = user_service.create(
                [
                    {
                        "name": "user",
                        "user_type": "administrator",
                        "email": "asender@a.com.au",
                    }
                ]
            )[0]

            provider = {"name": "Test"}
            dirname = os.path.dirname(os.path.realpath(__file__))
            fixture = os.path.normpath(
                os.path.join(dirname, "../fixtures", self.filename)
            )
            with open(fixture, mode="rb") as f:
                data = [(1, f.read())]
            parser = EMailRFC822FeedParser()
            self.items = parser.parse(data, provider)
            instance = EmailBelgaFeedingService()

            instance.save_attachment(data, self.items)

    def test_attachment(self):
        self.maxDiff = None
        self.assertEqual(self.items[0]["ednote"], "The story has 1 attachment(s)")
        self.assertEqual(len(self.items[0]["attachments"]), 1)
        attachment_id = self.items[0]["attachments"][0].get("attachment")
        data = get_resource_service("attachments").find_one(req=None, _id=attachment_id)
        self.assertEqual(data["title"], "attachment")
        self.assertEqual(data["description"], "email's attachment")
        self.assertEqual(data["user"], None)
        self.assertEqual(data["filename"], "attachment.txt")
        self.assertEqual(data["mimetype"], "text/plain")
        self.assertEqual(data["length"], 5)
