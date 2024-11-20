import datetime
import json

from httmock import HTTMock, urlmatch

from belga.io.feeding_services.twitter_belga import TwitterBelgaFeedingService
from tests import TestCase


items = [
    {
        "source": "twitter",
        "extra": {"tweet_url": "https://twitter.com/belga/status/1161474034728460290"},
        "headline": "belga: Hello, I am testing link for facebook\nhttps://t.co/KBxMrf1zGk",
        "type": "text",
        "guid": "tag:localhost:5000:2019:73fa4ad84a5fe6aed212563f03cb148d38ab1c6e",
        "versioncreated": datetime.datetime(2019, 8, 14, 3, 6, 3),
        "firstcreated": datetime.datetime(2019, 8, 14, 3, 6, 3),
        "body_html": 'Hello, I am testing link for facebook\nhttps://t.co/KBxMrf1zGk<p><a href="https://t.co/KBxMrf1zGk" '
        'target="_blank">https://t.co/KBxMrf1zGk</a></p>',
    }
]


@urlmatch(
    scheme="https",
    netloc="iframe.ly",
    path="/api/oembed",
    query="url=https://t.co/KBxMrf1zGk&api_key=abcdef",
)
def iframely_mock(url, request):
    body = (
        '<div class="iframely-embed" style="max-width: 640px;"><div class="i'
        'framely-responsive" style="padding-bottom: 75.0131%;"><a href="https://www.faceb'
        "ook.com/TomandJerry/photos/rpp.131583793581459/2759718637434615/?type=3&amp;thea"
        'ter" data-iframely-url="//cdn.iframe.ly/api/iframe?url=https%3A%2F%2Ft.co%2FKBxM'
        'rf1zGk&amp;key=7297b5377a04ff05f3378eb7d6e3cf0d"></a></div></div><script async s'
        'rc="//cdn.iframe.ly/embed.js" charset="utf-8"></script>'
    )
    return json.dumps({"html": body})


class TwitterBelgaServiceTestCase(TestCase):
    def setUp(self):
        provider = {"config": {"iframely_key": "abcdef", "embed_tweet": True}}
        with HTTMock(iframely_mock):
            self.items = TwitterBelgaFeedingService().parse_twitter_belga(
                items, provider
            )[0]

    def test_embed_content(self):
        item = self.items[0]
        self.assertEqual(item["source"], "twitter")
        self.assertEqual(
            item["extra"],
            {"tweet_url": "https://twitter.com/belga/status/1161474034728460290"},
        )
        self.assertEqual(
            item["headline"],
            "belga: Hello, I am testing link for facebook\nhttps://t.co/KBxMrf1zGk",
        )
        self.assertEqual(item["type"], "text")
        self.assertEqual(
            item["guid"],
            "tag:localhost:5000:2019:73fa4ad84a5fe6aed212563f03cb148d38ab1c6e",
        )
        self.assertEqual(str(item["versioncreated"]), "2019-08-14 03:06:03")
        self.assertEqual(str(item["firstcreated"]), "2019-08-14 03:06:03")
        expected_body = (
            'Hello, I am testing link for facebook\nhttps://t.co/KBxMrf1zGk<p><a href="https:/'
            '/t.co/KBxMrf1zGk" target="_blank">https://t.co/KBxMrf1zGk</a></p><!-- EMBED STAR'
            'T Twitter --><div class="iframely-embed" style="max-width: 640px;"><div class="i'
            'framely-responsive" style="padding-bottom: 75.0131%;"><a href="https://www.faceb'
            "ook.com/TomandJerry/photos/rpp.131583793581459/2759718637434615/?type=3&amp;thea"
            'ter" data-iframely-url="//cdn.iframe.ly/api/iframe?url=https%3A%2F%2Ft.co%2FKBxM'
            'rf1zGk&amp;key=7297b5377a04ff05f3378eb7d6e3cf0d"></a></div></div><script async s'
            'rc="//cdn.iframe.ly/embed.js" charset="utf-8"></script><!-- EMBED END Twitter --'
            ">"
        )
        self.assertEqual(item["body_html"], expected_body)
