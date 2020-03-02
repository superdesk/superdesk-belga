# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.appendsourcefabric.org/superdesk/license

import hashlib
import logging
import os
from datetime import datetime
from ftplib import error_perm
from io import BytesIO
from tempfile import gettempdir
from xml.etree import ElementTree

from flask import current_app as app

from superdesk import get_resource_service
from superdesk.ftp import ftp_connect
from superdesk.io.feeding_services import FileFeedingService, FTPFeedingService
from superdesk.io.registry import register_feed_parser
from superdesk.media.media_operations import process_file_from_stream

from .belga_newsml_1_2 import BelgaNewsMLOneFeedParser, SkipItemException

logger = logging.getLogger(__name__)


class BelgaRemoteNewsMLOneFeedParser(BelgaNewsMLOneFeedParser):
    """Feed Parser for Belga specific AFP NewsML."""

    NAME = 'belga_remote_newsml12'

    label = 'Belga Remote News ML 1.2 Parser'

    SUPPORTED_ASSET_TYPES = ('ALERT', 'SHORT', 'TEXT', 'BRIEF', 'ORIGINAL')

    def __init__(self):
        super().__init__()
        self.provider = None

    def parse(self, xml, provider=None):
        self.provider = provider
        if self.provider is None:
            self.provider = {}
        return super().parse(xml, provider)

    def parser_newsitem(self, newsitem_el):
        """
        Parse Newsitem element.
        Example:
         <NewsItem xml:lang="fr">
            <Identification>
                ....
            </Identification>
            <NewsManagement>
                ....
            </NewsManagement>
            <NewsComponent>
                ....
            </NewsComponent>
          </NewsItem>
        :param newsitem_el:
        :return:
        """
        # Identification
        self._item_seed.update(
            self.parser_identification(newsitem_el.find('Identification'))
        )

        # NewsManagement
        self._item_seed.update(
            self.parser_newsmanagement(newsitem_el.find('NewsManagement'))
        )

        # NewsComponent
        news_component_1 = newsitem_el.find('NewsComponent')
        if news_component_1 is not None:
            # Genre from NewsComponent 1st level
            for element in news_component_1.findall('DescriptiveMetadata/Genre'):
                if element.get('FormalName'):
                    # genre CV
                    self._item_seed.setdefault('subject', []).append({
                        "name": element.get('FormalName'),
                        "qcode": element.get('FormalName'),
                        "scheme": "genre"
                    })

            # parse attachment
            self._item_seed.update(
                self.parse_attachments(news_component_1)
            )

            # NewsComponent 2nd level
            # NOTE: each NewsComponent of 2nd level is a separate item with unique GUID
            for news_component_2 in news_component_1.findall('NewsComponent'):
                # create an item
                salt = hashlib.md5(ElementTree.tostring(news_component_2)).hexdigest()
                item = {**self._item_seed, 'guid': salt}

                # NewsComponent
                try:
                    self.parser_newscomponent(item, news_component_2)
                    if item.get('abstract'):
                        abstract = '<p>' + item['abstract'] + '</p>'
                        item['body_html'] = abstract + item['body_html']
                except SkipItemException:
                    continue

                # type
                self.populate_fields(item)

                self._items.append(item)

    def parse_attachments(self, news_component_1):
        attachments = []
        for news_component_2 in news_component_1.findall('NewsComponent'):
            role_name = self._get_role(news_component_2)
            if role_name and role_name.upper() not in self.SUPPORTED_ASSET_TYPES:
                for newscomponent in news_component_2.findall('NewsComponent'):
                    component_role = self._get_role(newscomponent)
                    if component_role and component_role not in ('Caption', 'Title'):
                        attachment = self.parse_attachment(newscomponent)
                        if attachment:
                            attachments.append(attachment)
                            # remove element to avoid parsing it as news item
                            news_component_1.remove(news_component_2)

        if attachments:
            return {
                'attachments': attachments,
                'ednote': 'The story has {} attachment(s)'.format(len(attachments)),
            }
        return {}

    def parse_attachment(self, newscomponent_el):
        """
        Parse attachment component, save it to storage and return attachment id

        <NewsComponent Duid="0" xml:lang="nl">
            <Role FormalName="Image"/>
            <DescriptiveMetadata>
                <Property FormalName="ComponentClass" Value="Image"/>
            </DescriptiveMetadata>
            <ContentItem Href="IMG_0182.jpg">
                <Format FormalName="Jpeg"/>
                <Characteristics>
                    <SizeInBytes>2267043</SizeInBytes>
                    <Property FormalName="Width" Value="4032"/>
                    <Property FormalName="Height" Value="3024"/>
                </Characteristics>
            </ContentItem>
        </NewsComponent>
        """
        content_item = newscomponent_el.find('ContentItem')
        if content_item is None:
            return

        # avoid re-adding media after item is ingested
        guid = hashlib.md5(ElementTree.tostring(content_item)).hexdigest()
        attachment_service = get_resource_service('attachments')
        old_attachment = attachment_service.find_one(req=None, guid=guid)
        if old_attachment:
            return {'attachment': old_attachment['_id']}

        filename = content_item.attrib.get('Href')
        if filename is None:
            return

        format_name = ''
        format_el = content_item.find('Format')
        if format_el is not None:
            format_name = format_el.attrib.get('FormalName')

        content = self._get_file(filename)
        if not content:
            return
        _, content_type, metadata = process_file_from_stream(content, 'application/' + format_name)
        content.seek(0)
        media_id = app.media.put(content,
                                 filename=filename,
                                 content_type=content_type,
                                 metadata=metadata,
                                 resource='attachments')
        try:
            ids = attachment_service.post([{
                'media': media_id,
                'filename': filename,
                'title': filename,
                'description': 'belga remote attachment',
                'guid': guid,
            }])
            return {'attachment': next(iter(ids), None)}
        except Exception as ex:
            app.media.delete(media_id)

    def _get_role(self, newscomponent_el):
        role = newscomponent_el.find('Role')
        if role is not None:
            return role.attrib.get('FormalName')

    def _get_file(self, filename):
        config = self.provider.get('config', {})
        path = config.get('path', '')
        file_dir = os.path.join(path, 'attachments')
        file_path = os.path.join(file_dir, filename)
        try:
            if self.provider.get('feeding_service') == 'ftp':
                file_path = self._download_file(filename, file_path, config)
            with open(file_path, 'rb') as f:
                content = f.read()
                self._move_file(file_dir, filename, config)
                return BytesIO(content)
        except (FileNotFoundError, error_perm) as e:
            logger.warning('File %s not found', file_path)
        except Exception as e:
            logger.error(e)

    def _download_file(self, filename, file_path, config):
        tmp_dir = os.path.join(gettempdir(), filename)
        with ftp_connect(config) as ftp, open(tmp_dir, 'wb') as f:
            ftp.retrbinary('RETR ' + file_path, f.write)
            return tmp_dir

    def _move_file(self, file_dir, filename, config):
        if self.provider.get('feeding_service') == 'ftp':
            with ftp_connect(config) as ftp:
                if config.get('move', False):
                    ftp_service = FTPFeedingService()
                    move_path, _ = ftp_service._create_move_folders(config, ftp)
                    ftp_service._move(
                        ftp, os.path.join(file_dir, filename), os.path.join(move_path, filename),
                        datetime.now(), False
                    )
        else:
            file_service = FileFeedingService()
            # move processed attachments to the same folder with XML
            file_dir = os.path.dirname(file_dir)
            file_service.move_file(file_dir, '/attachments/' + filename, self.provider)


register_feed_parser(BelgaRemoteNewsMLOneFeedParser.NAME, BelgaRemoteNewsMLOneFeedParser())
