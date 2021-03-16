import os
from lxml import etree

from belga.io.feed_parsers.belga_kyodo_newsml_1_2 import BelgaKyodoNewsMLOneFeedParser
from tests import TestCase


class BelgaKyodoNewsMLTestCase(TestCase):
    filename = 'kyodo_newsml_1_2_belga.xml'

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'test'}
        with open(fixture, 'rb') as f:
            parser = BelgaKyodoNewsMLOneFeedParser()
            self.xml_root = etree.parse(f).getroot()
            self.item = parser.parse(self.xml_root, provider)

    def test_content(self):
        item = self.item[0]

        self.assertEqual(item['headline'], 'Ex-Chinese Premier Li Peng dies aged 90: Xinhua')
        self.assertEqual(item["slugline"], None)
        self.assertEqual(item["keywords"], [])
        self.assertEqual(item['date_id'], '20190723')
        self.assertEqual(item['format'], 'Nitf_v3.0')
        self.assertEqual(item['guid'], 'urn:newsml:kyodonews.jp:20190723:20161021KW___0003800010:1')
        self.assertEqual(item['item_id'], '20161021KW___0003800010')
        self.assertEqual(item['priority'], 9)
        self.assertEqual(item['provider_id'], 'kyodonews.jp')
        self.assertEqual(item['type'], 'text')
        self.assertEqual(item['firstcreated'].isoformat(), '2019-07-23T20:21:19+09:00')
        self.assertEqual(item['versioncreated'].isoformat(), '2019-07-23T20:21:19+09:00')
        self.assertEqual(item['subject'], [
            {'name': 'France', 'qcode': 'country_fra', 'scheme': 'country',
             'translations': {'name': {'fr': 'France', 'nl': 'Frankrijk'}}},
            {'name': 'NEWS/GENERAL', 'parent': 'NEWS', 'qcode': 'NEWS/GENERAL', 'scheme': 'services-products'},
            {'name': 'default', 'qcode': 'default', 'scheme': 'distribution'},
            {'name': 'no', 'qcode': 'no', 'scheme': 'essential'},
            {'name': 'no', 'qcode': 'no', 'scheme': 'equivalents_list'},
        ])
        body_html = (
            "<p>     Former Chinese Premier Li Peng, who led a military crackdown on the pro-democracy movement at"
            " Beijing's Tiananmen Square in 1989, died Monday of illness in the capital, the official Xinhua"
            " News Agency reported Tuesday. He was 90.</p>"
            "<p>     Li served as premier, from 1988 to 1998, and chairman of the Standing Committee of the"
            " National People's Congress, China's top legislative body, between 1998 and 2003.</p>"
            "<p>     A native of Shanghai, he was ranked second in the Communist Party of China behind then General"
            " Secretary Jiang Zemin for much of the 1990s.</p>"
            "<p>     As premier, Li was believed to have taken a hard-line stance on the Tiananmen Square"
            " pro-democracy protests in 1989, including declaring martial law and ordering a military crackdown"
            " against student demonstrators in June that year.</p>"
            "<p>     China has never released an official death toll from the crackdown on protesters in Tiananmen"
            " Square and elsewhere around the country, but estimates from human rights groups and witnesses range"
            " from several hundred to several thousand.</p>"
            "<p>     Li traveled to Japan in 1989 and 1997 while he was premier. He also visited the country in"
            " 2002, which marked the 30th anniversary of normalized relations between Beijing and Tokyo, and held"
            " talks with then Japanese Prime Minister Junichiro Koizumi.</p>"
            "<p>==Kyodo</p>")
        item['body_html'] = item['body_html'].replace('\n', '').replace('\t', '')
        self.assertEqual(item['body_html'], body_html)
