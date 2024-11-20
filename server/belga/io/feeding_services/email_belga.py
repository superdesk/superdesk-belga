# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
import socket
import email
import imaplib
import io
import logging
from flask import current_app as app
from superdesk.media.media_operations import process_file_from_stream
from superdesk.io.feeding_services import EmailFeedingService
from superdesk.io.feed_parsers.rfc822 import EMailRFC822FeedParser
from superdesk.io.registry import (
    register_feeding_service,
    register_feeding_service_parser,
)
from superdesk.errors import IngestEmailError
from superdesk import get_resource_service

logger = logging.getLogger(__name__)


class EmailBelgaFeedingService(EmailFeedingService):
    NAME = "email-belga"
    label = "Email Belga"
    fields = [
        {
            "id": "attachment",
            "type": "boolean",
            "label": "Ingest email attachments",
            "required": True,
        },
        {
            "id": "server",
            "type": "text",
            "label": "Email Server",
            "placeholder": "Email Server",
            "required": True,
            "errors": {6003: "Server not found.", 6002: "Unexpected server response"},
        },
        {
            "id": "port",
            "type": "text",
            "label": "Email Server Port",
            "placeholder": "Email Server Port",
            "required": True,
            "default": "993",
        },
        {
            "id": "user",
            "type": "text",
            "label": "User",
            "placeholder": "User",
            "required": True,
        },
        {
            "id": "password",
            "type": "password",
            "label": "Password",
            "placeholder": "Password",
            "required": True,
            "errors": {6000: "Authentication error."},
        },
        {
            "id": "mailbox",
            "type": "text",
            "label": "Mailbox",
            "placeholder": "Mailbox",
            "required": True,
            "errors": {6004: "Authentication error."},
        },
        {
            "id": "formatted",
            "type": "boolean",
            "label": "Formatted Email Parser",
            "required": True,
        },
        {
            "id": "filter",
            "type": "text",
            "label": "Filter",
            "placeholder": "Filter",
            "required": True,
        },
    ]

    def _update(self, provider, update, test=False):
        config = provider.get("config", {})
        server = config.get("server", "")
        port = int(config.get("port", 993))
        new_items = []

        try:
            try:
                socket.setdefaulttimeout(app.config.get("EMAIL_TIMEOUT", 10))
                imap = imaplib.IMAP4_SSL(host=server, port=port)
            except (socket.gaierror, OSError) as e:
                raise IngestEmailError.emailHostError(exception=e, provider=provider)

            try:
                imap.login(config.get("user", None), config.get("password", None))
            except imaplib.IMAP4.error:
                raise IngestEmailError.emailLoginError(imaplib.IMAP4.error, provider)

            try:
                rv, data = imap.select(config.get("mailbox", None), readonly=False)
                if rv != "OK":
                    raise IngestEmailError.emailMailboxError()
                try:
                    rv, data = imap.search(None, config.get("filter", "(UNSEEN)"))
                    if rv != "OK":
                        raise IngestEmailError.emailFilterError()
                    for num in data[0].split():
                        rv, data = imap.fetch(num, "(RFC822)")
                        if rv == "OK" and not test:
                            try:
                                parser = self.get_feed_parser(provider, data)
                                item = parser.parse(data, provider)
                                if config.get("attachment"):
                                    self.save_attachment(data, item)
                                new_items.append(item)
                                rv, data = imap.store(num, "+FLAGS", "\\Seen")
                            except IngestEmailError:
                                continue
                finally:
                    imap.close()
            finally:
                imap.logout()
        except IngestEmailError:
            raise
        except Exception as ex:
            raise IngestEmailError.emailError(ex, provider)
        return new_items

    def save_attachment(self, data, items):
        """
        Given a data email for getting stream of attachment.

        """
        attachments = []
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    disposition = part.get("Content-Disposition")
                    if (
                        disposition is not None
                        and disposition.split(";")[0] == "attachment"
                    ):
                        fileName = part.get_filename()
                        if bool(fileName):
                            content = part.get_payload(decode=True)
                            content = io.BytesIO(content)
                            res = process_file_from_stream(
                                content, part.get_content_type()
                            )
                            file_name, content_type, metadata = res
                            content.seek(0)
                            media_id = app.media.put(
                                content,
                                filename=fileName,
                                content_type=content_type,
                                metadata=metadata,
                                resource="attachments",
                            )
                            try:
                                attachment_service = get_resource_service("attachments")
                                ids = attachment_service.post(
                                    [
                                        {
                                            "media": media_id,
                                            "filename": fileName,
                                            "title": "attachment",
                                            "description": "email's attachment",
                                        }
                                    ]
                                )
                                if ids:
                                    attachments.append(
                                        {"attachment": next(iter(ids), None)}
                                    )
                            except Exception as ex:
                                logger.error(
                                    "cannot add attachment for %s, %s"
                                    % (fileName, ex.args[0])
                                )
                                app.media.delete(media_id)

                if attachments:
                    for item in items:
                        if item["type"] == "text":
                            item["attachments"] = attachments
                            item["ednote"] = "The story has %s attachment(s)" % str(
                                len(attachments)
                            )


register_feeding_service(EmailBelgaFeedingService)
register_feeding_service_parser(
    EmailBelgaFeedingService.NAME, EMailRFC822FeedParser.NAME
)
