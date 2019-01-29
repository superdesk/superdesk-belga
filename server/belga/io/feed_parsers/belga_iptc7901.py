# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import re
import logging

from superdesk.errors import ParserError
from superdesk.io.registry import register_feed_parser
from superdesk.io.feed_parsers.dpa_iptc7901 import DPAIPTC7901FeedParser
from superdesk.metadata.utils import generate_guid
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, GUID_TAG
from superdesk.utc import utcnow

logger = logging.getLogger(__name__)


class BelgaIPTC7901FeedParser(DPAIPTC7901FeedParser):
    """
    Feed Parser which can parse if the feed is in IPTC 7901 format.
    """

    NAME = 'belgaiptc7901'

    label = 'Belga IPTC 7901 Parser'

    types = [
        ('dpa', b'([a-zA-Z]*)([0-9]*) (.) ([A-Z]{1,3}) ([0-9]*) ([a-zA-Z0-9 ]*)')
        ]
    txt_type = None

    def can_parse(self, file_path):
        try:
            BelgaIPTC7901FeedParser.txt_type = None
            with open(file_path, 'rb') as f:
                lines = [line for line in f]
                for item in self.types:
                    check_type = re.match(item[1], lines[0], flags=re.I)
                    if check_type:
                        BelgaIPTC7901FeedParser.txt_type = item[0]
                        return check_type

        except Exception as ex:
            return False

    def parse(self, file_path, provider=None):
        if BelgaIPTC7901FeedParser.txt_type == 'dpa':
            item = self.parse_content(file_path, provider)
            item = self.dpa_derive_dateline(item)
            self.dpa_parse_header(item)
            # Markup the text and set the content type
            item['body_html'] = '<p>' + item['body_html'].replace('\r\n', ' ').replace('\n', '</p><p>') + '</p>'
            item[ITEM_TYPE] = CONTENT_TYPE.TEXT

        return item

    def parse_content(self, file_path, provider=None):
        try:
            item = {ITEM_TYPE: CONTENT_TYPE.TEXT, 'guid': generate_guid(type=GUID_TAG),
                    'versioncreated': utcnow()}

            with open(file_path, 'rb') as f:
                lines = [line for line in f]
            # parse first header line
            m = re.match(b'([a-zA-Z]*)([0-9]*) (.) ([A-Z]{1,3}) ([0-9]*) ([a-zA-Z0-9 ]*)', lines[0], flags=re.I)
            if m:
                item['original_source'] = m.group(1).decode('latin-1', 'replace')
                item['ingest_provider_sequence'] = m.group(2).decode()
                item['priority'] = self.map_priority(m.group(3).decode())
                item['anpa_category'] = [{'qcode': self.map_category(m.group(4).decode())}]
                item['word_count'] = int(m.group(5).decode())

            inHeader = True
            inText = False
            inNote = False
            line_count = 0
            for line in lines[1:]:
                line_count += 1
                # STX starts the body of the story
                if line_count == 2:
                    # pick the rest of the line off as the headline
                    item['headline'] = line.decode('latin-1', 'replace').rstrip('\r\n')
                    item['body_html'] = ''
                    inText = True
                    inHeader = False
                    continue
                if inText:
                    if line.decode('latin-1', 'replace')\
                            .find('The following information is not for publication') != -1 \
                            or line.decode('latin-1', 'replace').find(
                                'The following information is not intended for publication') != -1:
                        inNote = True
                        inText = False
                        item['ednote'] = ''
                        continue
                    item['body_html'] += line.decode('latin-1', 'replace')
                if inNote:
                    item['ednote'] += line.decode('latin-1', 'replace')
                    continue
                if inHeader:
                    if 'slugline' not in item:
                        item['slugline'] = ''
                    item['slugline'] += line.decode('latin-1', 'replace').rstrip('/\r\n')
                    continue

            return item
        except Exception as ex:
            raise ParserError.IPTC7901ParserError(exception=ex, provider=provider)

    def dpa_parse_header(self, item):
        """
        Try to pickout the headline, byline and take key from what is seemingly a header
        :param item:
        :return:
        """
        headers, divider, the_rest = item.get('body_html', '').partition(' =\n \n')
        # If no divider then there was only one line and that is the headline so clean up the stray '='
        if not divider:
            item['headline'] = item.get('headline').replace(' =', '')
            return

        headerlines = headers.split('\n')

        item['headline'] = ''
        for line in headerlines:
            if line == str.upper(line):
                if 'anpa_take_key' in item:
                    item['anpa_take_key'] += " " + line
                else:
                    item['anpa_take_key'] = line
                continue
            if line.startswith('(') or line.endswith(')'):
                if 'anpa_header' in item:
                    item['anpa_header'] += " " + line
                else:
                    item['anpa_header'] = line
                continue
            if line == headerlines[-1]:
                if line.startswith('By '):
                    item['byline'] = line.replace('By ', '')
                continue
            item['headline'] += line
        item['body_html'] = the_rest

register_feed_parser(BelgaIPTC7901FeedParser.NAME, BelgaIPTC7901FeedParser())
