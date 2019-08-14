from superdesk.tests import TestCase
import datetime

items = [{
    'source': 'twitter',
    'extra': {
        'tweet_url': 'https://twitter.com/thanhnguyenfs/status/1161474034728460290'
    },
    'headline': 'thanhnguyenfs: Hello, I am testing link for facebook\nhttps://t.co/KBxMrf1zGk',
    'type': 'text',
    'guid': 'tag:localhost:5000:2019:73fa4ad84a5fe6aed212563f03cb148d38ab1c6e',
    'versioncreated': datetime.datetime(2019, 8, 14, 3, 6, 3),
    'firstcreated': datetime.datetime(2019, 8, 14, 3, 6, 3),
    'body_html': 'Hello, I am testing link for facebook\nhttps://t.co/KBxMrf1zGk<p><a href="https://t.co/KBxMrf1zGk" '
                 'target="_blank">https://t.co/KBxMrf1zGk</a></p>'
}]


class RssBelgaIngestServiceTest(TestCase):
    """Base class for RSSFeedingService tests."""

    def setUpForChildren(self):
        super().setUpForChildren()
        try:
            from belga.io.feeding_services.twitter_belga import TwitterBelgaFeedingService
        except ImportError:
            # a missing class should result in a test failure, not in an error
            self.fail("Could not import class under test (RSSFeedingService).")
        else:
            provider = {
                "config": {
                    "iframely_key": "9b959025054a1629510c03",
                    "embed_tweet": True
                }
            }
            self.items = TwitterBelgaFeedingService().parse_twitter_belga(items, provider)[0]


class RSSBelgaTestCase(RssBelgaIngestServiceTest):
    """Tests for the _create_item() method."""

    def test_creates_item_from_given_data(self):
        self.maxDiff = None
        item = self.items[0]
        self.assertEqual(item["source"], "twitter")
        self.assertEqual(item["extra"], {'tweet_url': 'https://twitter.com/thanhnguyenfs/status/1161474034728460290'})
        self.assertEqual(item["headline"],
                         "thanhnguyenfs: Hello, I am testing link for facebook\nhttps://t.co/KBxMrf1zGk")
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["guid"], "tag:localhost:5000:2019:73fa4ad84a5fe6aed212563f03cb148d38ab1c6e")
        self.assertEqual(str(item["versioncreated"]), "2019-08-14 03:06:03")
        self.assertEqual(str(item["firstcreated"]), "2019-08-14 03:06:03")
        expected_body = \
            (
                'Hello, I am testing link for facebook\nhttps://t.co/KBxMrf1zGk<p><a href="https:/'
                '/t.co/KBxMrf1zGk" target="_blank">https://t.co/KBxMrf1zGk</a></p><!-- EMBED STAR'
                'T Twitter --><div class="iframely-embed" style="max-width: 640px;"><div class="i'
                'framely-responsive" style="padding-bottom: 75.0131%;"><a href="https://www.faceb'
                'ook.com/TomandJerry/photos/rpp.131583793581459/2759718637434615/?type=3&amp;thea'
                'ter" data-iframely-url="//cdn.iframe.ly/api/iframe?url=https%3A%2F%2Ft.co%2FKBxM'
                'rf1zGk&amp;key=7297b5377a04ff05f3378eb7d6e3cf0d"></a></div></div><script async s'
                'rc="//cdn.iframe.ly/embed.js" charset="utf-8"></script><!-- EMBED END Twitter --'
                '>'
            )
        self.assertEqual(item["body_html"], expected_body)
