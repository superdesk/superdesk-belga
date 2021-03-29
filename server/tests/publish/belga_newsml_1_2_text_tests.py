# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from io import BytesIO
import pytz
import datetime
from lxml import etree
from unittest import mock
from bson.objectid import ObjectId

from superdesk.publish import init_app
from belga.publish.belga_newsml_1_2 import BelgaNewsML12Formatter
from .. import TestCase

belga_apiget_response = {
    'galleryId': 6666666,
    'active': True,
    'type': 'C',
    'name': 'JUDO   JPN   WORLD',
    'description': "Noel Van T End of Netherlands (L) celebrates after winning the gold medal.",
    'createDate': '2019-08-30T14:33:10Z',
    'deadlineDate': None,
    'author': 'auto',
    'credit': 'AFP',
    'category': None,
    'tagAuthor': None,
    'iconImageId': 777777777,
    'iconThumbnailUrl': 'https://2.t.cdn.belga.be/belgaimage:154669691:800x800:w?v=6666666&m=aaaaaaaa',
    'nrImages': 364,
    'themes': ['all', 'news', 'sports']
}


class BelgaNewsML12FormatterTextTest(TestCase):
    article = {
        '_id': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
        'guid': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
        'family_id': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
        'event_id': 'tag:localhost:5000:2019:f564b064-d0f9-45b2-b4a8-20a10dcfc761',
        'type': 'text',
        'version': 1,
        'flags': {
            'marked_for_not_publication': False,
            'marked_for_legal': False,
            'marked_archived_only': False,
            'marked_for_sms': False
        },
        'profile': 'belga_text',
        'pubstatus': 'usable',
        'format': 'HTML',
        'template': ObjectId('5c94ead2fe985e1c5776ddca'),
        'task': {
            'desk': ObjectId('5c94ed09fe985e1b69d7cb64'),
            'stage': ObjectId('5c94ed09fe985e1b69d7cb62'),
            'user': ObjectId('5d385f31fe985ec67a0ca583')
        },
        '_updated': datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
        '_created': datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
        '_current_version': 2,
        'firstcreated': datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
        'versioncreated': datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
        'firstpublished': datetime.datetime(2019, 4, 3, 12, 45, 14, tzinfo=pytz.UTC),
        'original_creator': '5d385f31fe985ec67a0ca583',
        'unique_id': 43,
        'unique_name': '#43',
        'state': 'in_progress',
        'source': 'Belga',
        'priority': 6,
        'urgency': 4,
        'genre': [{'qcode': 'Article', 'name': 'Article (news)'}],
        'place': [],
        'sign_off': 'ADM',
        'language': 'fr',
        'operation': 'update',
        'version_creator': '5d385f31fe985ec67a0ca583',
        'expiry': None,
        'schedule_settings': {'utc_embargo': None, 'time_zone': None},
        '_etag': '61c350853dc1513064f9e566f6d3c161cd387a0f',
        'lock_action': 'edit',
        'lock_session': ObjectId('5ca1cb4afe985e54931ee112'),
        'lock_time': datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
        'lock_user': ObjectId('5d385f31fe985ec67a0ca583'),
        'annotations': [],
        "associations": {
            "editor_0": {
                "type": "picture",
                "renditions": {
                    "original": {
                        "href": "http://localhost:5000/api/upload-raw/pic_1.jpg",
                        "media": "pic_1",
                        "mimetype": "image/jpeg",
                        "width": 3000,
                        "height": 2000
                    },
                    "baseImage": {
                        "href": "http://localhost:5000/api/upload-raw/pic_1.jpg",
                        "media": "pic_1",
                        "mimetype": "image/jpeg",
                        "width": 3000,
                        "height": 2000
                    },
                    "thumbnail": {
                        "href": "http://localhost:5000/api/upload-raw/pic_1.jpg",
                        "media": "pic_1",
                        "mimetype": "image/jpeg",
                        "width": 3000,
                        "height": 2000
                    },
                    "viewImage": {
                        "href": "http://localhost:5000/api/upload-raw/pic_1.jpg",
                        "media": "pic_1",
                        "mimetype": "image/jpeg",
                        "width": 3000,
                        "height": 2000
                    }
                },
                "extra": {
                    "belga-keywords": "japan, tokyo, mazda",
                    "city": "Tokio",
                    "country": "Japan"
                },
                "_id": "urn:newsml:localhost:5000:2019-08-19T15:15:01.015742:0976acf1-6956-4e03-beb1-e1c84833df45",
                "guid": "tag:localhost:5000:2019:7999396b-23a7-4642-94f4-55a09624d7ec",
                "media": "pic_1",
                "pubstatus": "usable",
                "format": "HTML",
                "firstcreated": "2019-08-19T13:15:01+0000",
                "versioncreated": "2019-08-19T13:15:01+0000",
                "original_creator": "5d385f31fe985ec67a0ca583",
                "state": "in_progress",
                "source": "Superdesk",
                "priority": 6,
                "urgency": 3,
                "genre": [
                    {
                        "qcode": "Article",
                        "name": "Article (news)"
                    }
                ],
                "place": [],
                "sign_off": "ADM",
                "language": "nl",
                "version_creator": "5d385f31fe985ec67a0ca583",
                "mimetype": "image/jpeg",
                "filemeta_json": "{\"length\": 883005}",
                "alt_text": "",
                "archive_description": "",
                "byline": "",
                "copyrightholder": "Belga",
                "copyrightnotice": "",
                "description_text": "Mazda MX5 retro 1990",
                "expiry": "2047-01-03T13:15:01+0000",
                "headline": "Mazda MX5 retro",
                "usageterms": "",
                "version": 2,
                "subject": [
                    {
                        "name": "Belga On The Spot",
                        "qcode": "Belga_on_the_spot",
                        "scheme": "media-source"
                    },
                    {
                        "name": "Czechia",
                        "qcode": "cze",
                        "translations": {
                            "name": {
                                "nl": "Tsjechië",
                                "fr": "Tchéquie"
                            }
                        },
                        "scheme": "countries"
                    }
                ]
            },
            "editor_1": {
                "renditions": {
                    "original": {
                        "width": 5472,
                        "height": 3648,
                        "href": "https://3.t.cdn.belga.be/belgaimage:154620545:1800x650:w?v=5d5aaa94&m=njopcomo"
                    },
                    "thumbnail": {
                        "href": "http://p.cdn.belga.be/belgaimage:154620545:600x140?v=5d5aaa94&m=kmjjblom"
                    },
                    "viewImage": {
                        "href": "https://3.t.cdn.belga.be/belgaimage:154620545:800x800:w?v=5d5aaa94&m=hdccpkpj"
                    },
                    "baseImage": {
                        "href": "https://3.t.cdn.belga.be/belgaimage:154620545:1800x650:w?v=5d5aaa94&m=njopcomo"
                    }
                },
                "type": "picture",
                "pubstatus": "usable",
                "_id": "urn:belga.be:image:154620545",
                "guid": "urn:belga.be:image:154620545",
                "headline": "20190827_zap_d99_014.jpg",
                "description_text": "August 27, 2019: Gaza, Palestine. 27 August 2019.The Al-Azza team defeats the Qala"
                                    "t Al-Janoub team 3-0 in the opening match of the amputees football league. The mat"
                                    "ch has been organized by the Palestine Amputee Football Association under the ausp"
                                    "ices of the International Committee of the Red Cross (ICRC) and was held at the P"
                                    "alestine stadium in Gaza City. Although some of the players were either born disab"
                                    "le or lost their limbs in the three recent Israeli offensives on Gaza, many others"
                                    " have lost their limbs in recent months after being shot by Israeli forces while t"
                                    "aking part in the Great March of Return rallies along the Gaza-Israeli border. The"
                                    " ICRC in Gaza believes in the importance of supporting people with disabilities ca"
                                    "used by military conflicts and in reintegrating them into society through both ps"
                                    "ychological and physical rehabilitation.",
                "versioncreated": "2019-08-28T09:22:17+0000",
                "firstcreated": "2019-08-28T09:22:17+0000",
                "byline": "NBWBNX",
                "creditline": "ZUMAPRESS",
                "source": "ZUMAPRESS",
            },
            "editor_2": {
                "_id": "urn:newsml:localhost:5000:2019-08-22T19:21:03.822095:354d20b8-1e3f-479a-ab80-eea6d72d5324",
                "media": "audio_1",
                "type": "audio",
                "pubstatus": "usable",
                "format": "HTML",
                "firstcreated": "2019-08-22T17:21:03+0000",
                "versioncreated": "2019-08-22T17:21:04+0000",
                "original_creator": "5d385f31fe985ec67a0ca583",
                "guid": "tag:localhost:5000:2019:a0b22047-4620-435a-8042-8f9ee24c282f",
                "unique_id": 28,
                "unique_name": "#28",
                "state": "in_progress",
                "source": "Superdesk",
                "priority": 6,
                "urgency": 3,
                "genre": [
                    {
                        "qcode": "Article",
                        "name": "Article (news)"
                    }
                ],
                "place": [],
                "sign_off": "ADM",
                "language": "nl",
                "operation": "update",
                "version_creator": "5d385f31fe985ec67a0ca583",
                "renditions": {
                    "original": {
                        "href": "http://localhost:5000/api/upload-raw/audio_1.mp3",
                        "media": "audio_1",
                        "mimetype": "audio/mp3"
                    }
                },
                "mimetype": "audio/mp3",
                "filemeta_json": "{\"title\": \"Impact Moderato\", \"author\": \"Kevin MacLeod\", \"album\": \"YouTube "
                                 "Audio Library\", \"duration\": \"0:00:27.193425\", \"music_genre\": \"Cinematic\", \""
                                 "nb_channel\": \"2\", \"sample_rate\": \"44100\", \"bits_per_sample\": \"16\", \"compr"
                                 "_rate\": \"4.41\", \"bit_rate\": \"320000\", \"format_version\": \"MPEG version 1 lay"
                                 "er III\", \"mime_type\": \"audio/mpeg\", \"endian\": \"Big endian\", \"length\": 1087"
                                 "849}",
                "description_text": "Some desc is here",
                "expiry": "2047-01-06T17:21:04+0000",
                "extra": {
                    "belga-keywords": "audio, music",
                    "city": "Pragua"
                },
                "headline": "audio head",
            },
            "editor_3": {
                "_id": "urn:newsml:localhost:5000:2019-08-14T16:51:06.604540:734d4292-db4f-4358-8b2f-c2273a4925d5",
                "media": "video_1",
                "type": "video",
                "pubstatus": "usable",
                "format": "HTML",
                "firstcreated": "2019-08-14T14:51:06+0000",
                "versioncreated": "2019-08-14T14:51:06+0000",
                "original_creator": "5d385f31fe985ec67a0ca583",
                "guid": "tag:localhost:5000:2019:3fe341ab-45d8-4f72-9308-adde548daef8",
                "unique_id": 13,
                "unique_name": "#13",
                "family_id": "urn:newsml:localhost:5000:2019-08-14T16:51:06."
                             "604540:734d4292-db4f-4358-8b2f-c2273a4925d5",
                "event_id": "tag:localhost:5000:2019:d8846c42-d18a-447d-96e2-c3173c3adfdd",
                "state": "in_progress",
                "source": "Superdesk",
                "priority": 6,
                "urgency": 3,
                "genre": [
                    {
                        "qcode": "Article",
                        "name": "Article (news)"
                    }
                ],
                "place": [],
                "sign_off": "ADM",
                "language": "nl",
                "operation": "update",
                "version_creator": "5d385f31fe985ec67a0ca583",
                "renditions": {
                    "original": {
                        "href": "http://localhost:5000/api/upload-raw/video_1.mp4",
                        "media": "video_1",
                        "mimetype": "video/mp4"
                    }
                },
                "mimetype": "video/mp4",
                "filemeta_json": "{\"duration\": \"0:00:09.482000\", \"width\": \"640\", \"height\": \"360\", \"creatio"
                                 "n_date\": \"2019-06-16T17:32:12+00:00\", \"last_modification\": \"2019-06-16T17:32:12"
                                 "+00:00\", \"comment\": \"User volume: 100.0%\", \"mime_type\": \"video/mp4\", \"endia"
                                 "n\": \"Big endian\", \"length\": 1022462}",
                "description_text": "water",
                "expiry": "2046-12-29T14:51:06+0000",
                "headline": "water",
            },
            "belga_related_images--1": {
                "_id": "urn:newsml:localhost:5000:2019-08-15T13:04:19.702285:d201d16e-1011-4d4c-a262-fed9942a64db",
                "type": "picture"
            },
            "belga_related_images--2": {
                "renditions": {
                    "original": {
                        "width": 4288,
                        "height": 3012,
                        "href": "https://0.t.cdn.belga.be/belgaimage:154670415:1800x650:w?v=5d5aaa94&m=ablplddf"
                    },
                    "thumbnail": {
                        "href": "http://p.cdn.belga.be/belgaimage:154670415:600x140?v=5d5aaa94&m=fcgloioh"
                    },
                    "viewImage": {
                        "href": "https://2.t.cdn.belga.be/belgaimage:154670415:800x800:w?v=5d5aaa94&m=ebedljnc"
                    },
                    "baseImage": {
                        "href": "https://0.t.cdn.belga.be/belgaimage:154670415:1800x650:w?v=5d5aaa94&m=ablplddf"
                    }
                },
                "_links": {
                    "self": {
                        "title": "Search_providers_proxy",
                        "href": "search_providers_proxy/urn:belga.be:image:154670415"
                    }
                },
                "type": "picture",
                "pubstatus": "usable",
                "_id": "urn:belga.be:image:154670415",
                "guid": "urn:belga.be:image:154670415",
                "headline": "urn:newsml:dpa.com:20090101:190829-99-659387",
                "description_text": "29 August 2019, Hanover: Cycling: UCI Europaserie, Germany Tour, 1st stage from Ha"
                                    "nnover to Halberstadt (167,00 km). The German Pascal Ackermann from Team Bora-Hans"
                                    "grohe before the start of the race. Photo: Bernd Thissen/dpa",
                "versioncreated": "2019-08-29T13:22:02+0000",
                "firstcreated": "2019-08-29T13:22:02+0000",
                "byline": "NBYXIU",
                "creditline": "DPA",
                "source": "DPA",
                "_type": "externalsource",
                "fetch_endpoint": "search_providers_proxy"
            },
            "belga_related_gallery--1": {
                "renditions": {
                    "original": {
                        "href": "http://localhost:5000/api/upload-raw/pic_3.jpg",
                        "media": "pic_3",
                        "mimetype": "image/jpeg",
                        "width": 3000,
                        "height": 2000
                    },
                    "baseImage": {
                        "href": "http://localhost:5000/api/upload-raw/pic_3.jpg",
                        "media": "pic_3",
                        "mimetype": "image/jpeg",
                        "width": 3000,
                        "height": 2000
                    },
                    "thumbnail": {
                        "href": "http://localhost:5000/api/upload-raw/pic_3.jpg",
                        "media": "pic_3",
                        "mimetype": "image/jpeg",
                        "width": 3000,
                        "height": 2000
                    },
                    "viewImage": {
                        "href": "http://localhost:5000/api/upload-raw/pic_3.jpg",
                        "media": "pic_3",
                        "mimetype": "image/jpeg",
                        "width": 3000,
                        "height": 2000
                    }
                },
                "extra": {
                    "belga-keywords": "japan, tokyo, mazda",
                    "city": "Tokio",
                    "country": "Japan"
                },
                "_id": "urn:newsml:localhost:5000:2019-08-19T15:16:08.719058:f5628876-33e5-4dd1-89f0-1d9e792eebaa",
                "guid": "tag:localhost:5000:2019:c9d059aa-4056-4009-9e26-06cf718badaa",
                "media": "pic_3",
                "type": "picture",
                "pubstatus": "usable",
                "format": "HTML",
                "firstcreated": "2019-08-19T13:15:01+0000",
                "versioncreated": "2019-08-19T13:15:01+0000",
                "original_creator": "5d385f31fe985ec67a0ca583",
                "state": "in_progress",
                "source": "Superdesk",
                "priority": 6,
                "urgency": 3,
                "genre": [
                    {
                        "qcode": "Article",
                        "name": "Article (news)"
                    }
                ],
                "place": [],
                "sign_off": "ADM",
                "language": "nl",
                "version_creator": "5d385f31fe985ec67a0ca583",
                "mimetype": "image/jpeg",
                "filemeta_json": "{\"length\": 883005}",
                "alt_text": "",
                "archive_description": "",
                "byline": "",
                "copyrightholder": "Belga",
                "copyrightnotice": "",
                "description_text": "Mazda MX5 new 2017",
                "expiry": "2047-01-03T13:15:01+0000",
                "headline": "Mazda MX5 new",
                "subject": [],
                "usageterms": "",
                "version": 2
            },
            "belga_related_gallery--2": {
                "renditions": {
                    "original": {
                        "width": 4000,
                        "height": 2580,
                        "href": "https://2.t.cdn.belga.be/belgaimage:147832075:1800x650:w?v=5d5aaa94&m=lhkkcgbb"
                    },
                    "thumbnail": {
                        "href": "http://p.cdn.belga.be/belgaimage:147832075:600x140?v=5d5aaa94&m=pmahjglh"
                    },
                    "viewImage": {
                        "href": "https://0.t.cdn.belga.be/belgaimage:147832075:800x800:w?v=5d5aaa94&m=lgmbdgan"
                    },
                    "baseImage": {
                        "href": "https://2.t.cdn.belga.be/belgaimage:147832075:1800x650:w?v=5d5aaa94&m=lhkkcgbb"
                    }
                },
                "_links": {
                    "self": {
                        "title": "Search_providers_proxy",
                        "href": "search_providers_proxy/urn:belga.be:image:147832075"
                    }
                },
                "type": "picture",
                "pubstatus": "usable",
                "_id": "urn:belga.be:image:147832075",
                "guid": "urn:belga.be:image:147832075",
                "headline": "JAPAN-AUTOMOBILE-MAZDA",
                "description_text": "April 5, 2019, Chiba, Japan - Japanese automaker Mazda Motor designer Masashi Naka"
                                    "yama displays Mazda MX-5 or Roadster 30th anniversary edition at the Automobile Co"
                                    "uncil in Chiba, suburban Tokyo on Friday, April 5, 2019. Mazda started to accept o"
                                    "rders of 3,000 limited units worldwide including softtop and retractable hardtop f"
                                    "or the world's best selling roadster's 30th anniversary model.   (Photo by Yoshio "
                                    "Tsunoda/AFLO)\nNO THIRD PARTY SALES.",
                "versioncreated": "2019-04-07T22:03:56+0000",
                "firstcreated": "2019-04-07T22:03:56+0000",
                "byline": "MMZTTC",
                "creditline": "AFLO",
                "source": "AFLO",
                "fetch_endpoint": "search_providers_proxy",
                "ingest_provider": "5d542028c04280bc6d6157f4",
                "_etag": "abb9ce931da3840290650facfcc7961f0dd476b7"
            },
            "belga-coverages--1": {
                "renditions": {
                    "original": {
                        "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                    },
                    "thumbnail": {
                        "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                    },
                    "viewImage": {
                        "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                    },
                    "baseImage": {
                        "href": "https://1.t.cdn.belga.be/belgaimage:154670498:800x800:w?v=5d5aaa94&m=dnikoiil"
                    }
                },
                "extra": {
                    "bcoverage": "urn:belga.be:coverage:6690595"
                },
                "_links": {
                    "self": {
                        "title": "Search_providers_proxy",
                        "href": "search_providers_proxy/urn:belga.be:coverage:6690595"
                    }
                },
                "type": "graphic",
                "mimetype": "application/vnd.belga.coverage",
                "pubstatus": "usable",
                "_id": "urn:belga.be:coverage:6690595",
                "guid": "urn:belga.be:coverage:6690595",
                "headline": "RUSSIAN PARAGLIDING CHAMPIONSHIP IN STAVROPOL TERRITORY",
                "description_text": "STAVROPOL TERRITORY, RUSSIA - AUGUST 28, 2019: Contestants during the 2019 Russian"
                                    " Paragliding Championship on Mount Yutsa. Anton Podgaiko/TASS 0",
                "versioncreated": "2019-08-29T15:46:39+0000",
                "firstcreated": "2019-08-29T15:46:39+0000",
                "byline": "",
                "creditline": "ITARTASS",
                "source": "ITARTASS",
                "_type": "externalsource",
            },
            "belga-related-audio--1": {
                "_id": "urn:newsml:localhost:5000:2019-08-22T19:21:03.822095:354d20b8-1e3f-479a-ab80-eea6d72d5324",
                "type": "audio"
            },
            "belga-related-video--1": {
                "_id": "urn:newsml:localhost:5000:2019-08-14T16:51:06.604540:734d4292-db4f-4358-8b2f-c2273a4925d5",
                "type": "video"
            },
            "belga_related_articles--1": {
                "_id": "urn:newsml:localhost:5000:2019-09-16T16:15:29.975832:2cbd7b49-9d7b-48c5-b1a0-fc802f3f4413",
                "type": "text"
            },
            "belga_related_articles--2": {
                "extra": {
                    "bcoverage": "urn:belga.be:360archive:77777777"
                },
                "type": "text",
                "mimetype": "application/vnd.belga.360archive",
                "pubstatus": "usable",
                "_id": "urn:belga.be:360archive:77777777",
                "guid": "urn:belga.be:360archive:77777777",
                "headline": "Vasil Kiryienka (38) doet ondanks hartproblemen verder bij INEOS",
                "name": "",
                "description_text": "",
                "versioncreated": "2019-10-23T09:30:14+0000",
                "firstcreated": "2019-10-23T09:30:14+0000",
                "creditline": "BELGA",
                "source": "BELGA",
                "language": "nl",
                "abstract": "Vasil Kiryienka zal ook in 2020 deel uitmaken van het peloton.",
                "body_html": "Kiryienka werd dit jaar opgeschrikt door een hartprobleem.",
                "_type": "externalsource",
                "fetch_endpoint": "search_providers_proxy",
                "ingest_provider": "5da8572a9e7cb98d13ce1d7b",
                "selected": False
            }
        },
        'authors': [
            {
                '_id': ['5d385f31fe985ec67a0ca583', 'AUTHOR'],
                'role': 'AUTHOR',
                'name': 'AUTHOR',
                'parent': '5d385f31fe985ec67a0ca583',
                'sub_label': 'John Smith',
                'scheme': None
            },
            {
                'role': 'EDITOR',
                'name': 'OLEG',
            }
        ],
        'body_html': '<p>Curabitur non nulla sit amet nisl <b>tempus</b> convallis quis ac lectus. Donec sollicitudin <'
                     'b>molestie</b> malesuada. Vivamus suscipit tortor eget felis porttitor volutpat.</p>\n<p>Donec ru'
                     'trum congue leo eget malesuada. Sed porttitor lectus nibh. Pellentesque in ipsum id orci porta da'
                     'pibus. Praesent sapien massa, convallis a pellentesque nec, egestas non nisi.</p>\n<h2>books</h2>'
                     '\n<p>Praesent sapien massa, convallis a pellentesque nec, egestas non nisi. Curabitur aliquet qua'
                     'm id dui posuere blandit. Vivamus suscipit tortor eget felis porttitor volutpat. Praesent sapien '
                     'massa, convallis a pellentesque nec, egestas non nisi. Vestibulum ante ipsum primis in faucibus o'
                     'rci luctus et ultrices posuere cubilia Curae.</p>',
        'ednote': 'Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui.',
        'extra': {
            'belga-url': [
                {
                    'url': 'http://example.com/',
                    'description': 'Example com',
                    'guid': 'bf744ced-ecca-4a2f-bf6d-bdd52092e31e'
                },
                {
                    'url': 'https://github.com/superdesk',
                    'description': 'Superdesk',
                    'guid': '262f0e63-b4d9-4269-8a45-8938b0c9e556'
                }
            ],
            "city": "Prague",
            "belga-coverage-new": "urn:belga.be:coverage:6666666"
        },
        'fields_meta': {
            'extracountry': {'draftjsState': [{'blocks': [
                {'key': 'cuo9h', 'text': 'Czech Republic', 'type': 'unstyled', 'depth': 0, 'inlineStyleRanges': [],
                 'entityRanges': [], 'data': {'MULTIPLE_HIGHLIGHTS': {}}}], 'entityMap': {}}]
            },
            'extracity': {
                'draftjsState': [{'blocks': [
                    {'key': 'c49mk', 'text': 'Prague', 'type': 'unstyled', 'depth': 0, 'inlineStyleRanges': [],
                     'entityRanges': [], 'data': {'MULTIPLE_HIGHLIGHTS': {}}}], 'entityMap': {}}]
            },
            'headline': {
                'draftjsState': [{'blocks': [
                    {'key': '72fbn', 'text': 'New Skoda Scala', 'type': 'unstyled', 'depth': 0, 'inlineStyleRanges': [],
                     'entityRanges': [], 'data': {'MULTIPLE_HIGHLIGHTS': {}}}], 'entityMap': {}}]
            },
            'body_html': {
                'draftjsState': [{'blocks': [{'key': 'fgaq4',
                                              'text': 'Praesent sapien massa, convallis a pellentesque nec, egestas '
                                                      'non nisi. Curabitur aliquet quam id dui posuere blandit. '
                                                      'Curabitur non nulla sit amet nisl tempus convallis quis ac '
                                                      'lectus.',
                                              'type': 'unstyled', 'depth': 0, 'inlineStyleRanges': [],
                                              'entityRanges': [], 'data': {'MULTIPLE_HIGHLIGHTS': {}}}],
                                  'entityMap': {}}]
            }
        },
        'headline': 'New Skoda Scala',
        'keywords': ['europe', 'Prague', 'CZ', 'Skoda'],
        'slugline': 'skoda scala',
        'subject': [
            {'name': 'bilingual', 'qcode': 'bilingual', 'scheme': 'distribution'},
            {'name': 'ANALYSIS', 'qcode': 'ANALYSIS', 'scheme': 'genre'},
            {'name': 'CURRENT', 'qcode': 'CURRENT', 'scheme': 'genre'},
            {'name': 'FORECAST', 'qcode': 'FORECAST', 'scheme': 'genre'},
            {'name': 'A1', 'qcode': 'A1', 'scheme': 'label'},
            {'name': 'A2', 'qcode': 'A2', 'scheme': 'label'},
            {'name': 'R1', 'qcode': 'R1', 'scheme': 'label'},
            {
                'name': 'Aruba',
                'qcode': 'country_abw',
                'translations': {
                    'name': {
                        'nl': 'Aruba',
                        'fr': 'Aruba'
                    }
                },
                'scheme': 'country'
            },
            {'name': 'BIN/ALG', 'qcode': 'BIN/ALG', 'parent': 'BIN', 'scheme': 'services-products'},
            {'name': 'EXT/ECO', 'qcode': 'EXT/ECO', 'parent': 'EXT', 'scheme': 'services-products'},
            {'name': 'BIN', 'qcode': 'BIN', 'parent': None, 'scheme': 'services-products'},
            {'name': 'NEWS/ENTERTAINMENT', 'qcode': 'NEWS/ENTERTAINMENT', 'parent': 'NEWS',
             'scheme': 'services-products'},
            {'name': 'NEWS/SPORTS', 'qcode': 'NEWS/SPORTS', 'parent': 'NEWS', 'scheme': 'services-products'},
            {'name': 'DPA', 'qcode': 'DPA', 'scheme': 'sources'},
            {'name': 'ANP', 'qcode': 'ANP', 'scheme': 'sources'},
            {
                "name": "Belgium",
                "qcode": "bel",
                "translations": {
                    "name": {
                        "nl": "België",
                        "fr": "Belgique"
                    }
                },
                "scheme": "countries"
            }
        ],
        'word_count': 28,
        'byline': 'BELGA',
        'administrative': {
            'contributor': 'John',
            'validator': 'John the validator',
            'validation_date': '123123',
            'foreign_id': '4444444'
        },
        'line_type': '1',
        'line_text': 'line text is here',
        'attachments': [
            {
                'attachment': ObjectId('5d692b76c8f549e289b0270b')
            }
        ]
    }

    attachments = (
        {
            "_id": ObjectId("5d692b76c8f549e289b0270b"),
            "media": "pdf_1",
            "title": "booktype pdf",
            "description": "A pdf cover for a book",
            "user": ObjectId("5d385f31fe985ec67a0ca583"),
            "filename": "AIR_16-17_ar_frontcover_web.pdf",
            "mimetype": "application/pdf",
            "length": 40248,
        },
    )

    archive = (
        {
            "_id": "urn:newsml:localhost:5000:2019-08-15T13:04:19.702285:d201d16e-1011-4d4c-a262-fed9942a64db",
            "media": "pic_2",
            "type": "picture",
            "pubstatus": "usable",
            "format": "HTML",
            "_current_version": 4,
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "tag:localhost:5000:2019:bb1f22ac-d33a-4b31-8ed6-2c7889373c78",
            "state": "in_progress",
            "source": "Superdesk",
            "priority": 6,
            "urgency": 3,
            "genre": [
                {
                    "qcode": "Article",
                    "name": "Article (news)"
                }
            ],
            "place": [],
            "sign_off": "ADM",
            "language": "nl",
            "version_creator": "5d385f31fe985ec67a0ca583",
            "renditions": {
                "original": {
                    "href": "http://localhost:5000/api/upload-raw/5d553c333031e2855a2e5662.jpg",
                    "media": "pic_2",
                    "mimetype": "image/jpeg",
                    "width": 1920,
                    "height": 1280,
                    "poi": {
                        "x": 960,
                        "y": 640
                    }
                },
                "baseImage": {
                    "href": "http://localhost:5000/api/upload-raw/5d553c343031e2855a2e5664.jpg",
                    "media": "pic_2",
                    "mimetype": "image/jpeg",
                    "width": 1400,
                    "height": 933,
                    "poi": {
                        "x": 700,
                        "y": 466
                    }
                },
                "thumbnail": {
                    "href": "http://localhost:5000/api/upload-raw/5d553c343031e2855a2e5666.jpg",
                    "media": "pic_2",
                    "mimetype": "image/jpeg",
                    "width": 180,
                    "height": 120,
                    "poi": {
                        "x": 90,
                        "y": 60
                    }
                },
                "viewImage": {
                    "href": "http://localhost:5000/api/upload-raw/5d553c343031e2855a2e5668.jpg",
                    "media": "pic_2",
                    "mimetype": "image/jpeg",
                    "width": 640,
                    "height": 426,
                    "poi": {
                        "x": 320,
                        "y": 213
                    }
                }
            },
            "mimetype": "image/jpeg",
            "filemeta_json": "{\"length\": 170263}",
            "byline": "BIENVENIDO VELASCO",
            "description_text": "History of Mazda",
            "headline": "History",
            "extra": {
                "belga-keywords": "one, two, three",
                "city": "Prague"
            },
            "subject": [
                {
                    "name": "Belga",
                    "qcode": "Belga",
                    "scheme": "credit"
                },
                {
                    "name": "Belgium",
                    "qcode": "bel",
                    "translations": {
                        "name": {
                            "nl": "België",
                            "fr": "Belgique"
                        }
                    },
                    "scheme": "countries"
                }
            ]
        },
        {
            "_id": "urn:newsml:localhost:5000:2019-08-22T19:21:03.822095:354d20b8-1e3f-479a-ab80-eea6d72d5324",
            "media": "audio_1",
            "type": "audio",
            "pubstatus": "usable",
            "format": "HTML",
            "firstcreated": "2019-08-22T17:21:03+0000",
            "versioncreated": "2019-08-22T17:21:04+0000",
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "tag:localhost:5000:2019:a0b22047-4620-435a-8042-8f9ee24c282f",
            "unique_id": 28,
            "unique_name": "#28",
            "state": "in_progress",
            "source": "Superdesk",
            "priority": 6,
            "urgency": 3,
            "genre": [
                {
                    "qcode": "Article",
                    "name": "Article (news)"
                }
            ],
            "place": [],
            "sign_off": "ADM",
            "language": "nl",
            "operation": "update",
            "version_creator": "5d385f31fe985ec67a0ca583",
            "renditions": {
                "original": {
                    "href": "http://localhost:5000/api/upload-raw/audio_1",
                    "media": "audio_1",
                    "mimetype": "audio/mp3"
                }
            },
            "mimetype": "audio/mp3",
            "filemeta_json": "{\"title\": \"Impact Moderato\", \"author\": \"Kevin MacLeod\", \"album\": \"YouTube Audi"
                             "o Library\", \"duration\": \"0:00:27.193425\", \"music_genre\": \"Cinematic\", \"nb_chann"
                             "el\": \"2\", \"sample_rate\": \"44100\", \"bits_per_sample\": \"16\", \"compr_rate\": \"4"
                             ".41\", \"bit_rate\": \"320000\", \"format_version\": \"MPEG version 1 layer III\", \"mime"
                             "_type\": \"audio/mpeg\", \"endian\": \"Big endian\", \"length\": 1087849}",
            "description_text": "Some desc is here",
            "expiry": "2047-01-06T17:21:04+0000",
            "extra": {
                "belga-keywords": "audio, music",
                "city": "Pragua"
            },
            "headline": "audio head",
        },
        {
            "_id": "urn:newsml:localhost:5000:2019-09-16T16:15:29.975832:2cbd7b49-9d7b-48c5-b1a0-fc802f3f4413",
            "family_id": "urn:newsml:localhost:5000:2019-09-10T16:16:39.458119:923d24ac-7075-413b-a164-701a4e9b2e06",
            "event_id": "tag:localhost:5000:2019:2bd05833-e4d7-482f-bf78-5afde4b980c5",
            "language": "nl",
            "source": "Belga",
            "authors": [
                {
                    "_id": [
                        "5d385f31fe985ec67a0ca583",
                        "AUTHOR"
                    ],
                    "role": "AUTHOR",
                    "name": "AUTHOR",
                    "parent": "5d385f31fe985ec67a0ca583",
                    "sub_label": "John Smith"
                }
            ],
            "headline": "100 let",
            "sign_off": "ADM",
            "slugline": "Citroen 100 let",
            "urgency": 2,
            "ednote": "100 let of citroen",
            "profile": "belga_text",
            "rewrite_of": "urn:newsml:localhost:5000:2019-09-10T16:16:39.458119:923d24ac-7075-413b-a164-701a4e9b2e06",
            "rewrite_sequence": 1,
            "task": {
                "desk": ObjectId("5d76113ab3af37dea3a2eb9e"),
                "stage": ObjectId("5d76113ab3af37dea3a2eb9c"),
                "user": ObjectId("5d385f31fe985ec67a0ca583")
            },
            "expiry": None,
            "body_html": "100 let of citroen in body",
            "state": "in_progress",
            "anpa_take_key": "update",
            "_current_version": 1,
            "type": "text",
            "pubstatus": "usable",
            "format": "HTML",
            "firstcreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "versioncreated": datetime.datetime(2019, 4, 3, 12, 41, 53, tzinfo=pytz.UTC),
            "original_creator": "5d385f31fe985ec67a0ca583",
            "guid": "urn:newsml:localhost:5000:2019-09-16T16:15:29.975832:2cbd7b49-9d7b-48c5-b1a0-fc802f3f4413",
            "unique_id": 71,
            "unique_name": "#71",
            "priority": 6,
            "genre": [
                {
                    "qcode": "Article",
                    "name": "Article (news)"
                }
            ],
            "place": [],
            "operation": "create",
            "version_creator": "5d385f31fe985ec67a0ca583"
        }
    )

    users = ({
        "_id": ObjectId("5d385f31fe985ec67a0ca583"),
        "username": "adm",
        "password": "blabla",
        "email": "admin@example.com",
        "user_type": "administrator",
        "is_active": True,
        "needs_activation": False,
        "is_author": True,
        "is_enabled": True,
        "display_name": "John Smith",
        "sign_off": "ADM",
        "first_name": "John",
        "last_name": "Smith",
        "role": ObjectId("5d542206c04280bc6d6157f9"),
    },)

    roles = ({
        "_id": ObjectId("5d542206c04280bc6d6157f9"),
        "author_role": "AUTHOR",
        "editor_role": "AUTHOR"
    },)

    vocabularies = (
        {
            "_id": "belga-coverage-new",
            "field_type": "custom",
            "items": [],
            "type": "manageable",
            "schema": {
                "name": {},
                "qcode": {},
                "parent": {}
            },
            "service": {
                "all": 1
            },
            "custom_field_type": "belga.coverage",
            "display_name": "belga coverage new",
            "unique_field": "qcode",
        },
    )

    subscriber = {
        '_id': 'some_id',
        'name': 'Dev Subscriber',
    }

    @mock.patch('superdesk.publish.subscribers.SubscribersService.generate_sequence_number', lambda s, sub: 1)
    @mock.patch('belga.search_providers.BelgaCoverageSearchProvider.api_get', lambda self,
                endpoint, params: belga_apiget_response)
    def setUp(self):
        init_app(self.app)
        self.app.data.insert('users', self.users)
        self.app.data.insert('archive', self.archive)
        self.app.data.insert('attachments', self.attachments)
        self.app.data.insert('roles', self.roles)
        self.app.data.insert('vocabularies', self.vocabularies)
        # insert pictures
        media_items = (
            {
                '_id': 'pic_1',
                'content': BytesIO(b'pic_one_content'),
                'content_type': 'image/jpeg',
                'metadata': {
                    'length': 10
                }
            },
            {
                '_id': 'pic_2',
                'content': BytesIO(b'pic_two_content'),
                'content_type': 'image/jpeg'
            },
            {
                '_id': 'pic_3',
                'content': BytesIO(b'pic_three_content'),
                'content_type': 'image/jpeg',
                'metadata': {
                    'length': 12
                }
            },
            {
                '_id': 'audio_1',
                'content': BytesIO(b'the man who sold the world'),
                'content_type': 'audio/mp3',
                'metadata': {
                    'length': 12
                }
            },
            {
                '_id': 'video_1',
                'content': BytesIO(b'czech rap xD'),
                'content_type': 'video/mp4',
                'metadata': {
                    'length': 12
                }
            },
            {
                '_id': 'pdf_1',
                'content': BytesIO(b'it is a pdf'),
                'content_type': 'application/pdf',
                'metadata': {
                    'length': 40248
                }
            },
        )
        for media_item in media_items:
            # base rendition
            self.app.media.put(**media_item)

        self.article['state'] = 'published'
        self.formatter = BelgaNewsML12Formatter()
        seq, doc = self.formatter.format(self.article, self.subscriber)[0]
        self.newsml = etree.XML(bytes(bytearray(doc, encoding=BelgaNewsML12Formatter.ENCODING)))

    def test_catalog(self):
        # NewsML -> Catalog
        catalog = self.newsml.xpath('Catalog')[0]
        self.assertEqual(
            catalog.get('Href'),
            'http://www.belga.be/dtd/BelgaCatalog.xml'
        )

    def test_newsenvelope(self):
        # NewsML -> NewsEnvelope
        self.assertEqual(
            self.newsml.xpath('NewsEnvelope/DateAndTime')[0].text,
            self.formatter._string_now
        )
        self.assertIsNone(
            self.newsml.xpath('NewsEnvelope/NewsService')[0].text,
        )
        self.assertIsNone(
            self.newsml.xpath('NewsEnvelope/NewsProduct')[0].text,
        )

    def test_identification(self):
        # NewsML -> NewsItem -> Identification
        with self.app.app_context():
            self.assertEqual(
                self.newsml.xpath('NewsItem/Identification/NewsIdentifier/ProviderId')[0].text,
                self.app.config['NEWSML_PROVIDER_ID']
            )
        self.assertEqual(
            self.newsml.xpath('NewsItem/Identification/NewsIdentifier/DateId')[0].text,
            '20190403T144153'
        )
        self.assertEqual(
            self.newsml.xpath('NewsItem/Identification/NewsIdentifier/NewsItemId')[0].text,
            self.formatter._duid
        )
        revisionid = self.newsml.xpath('NewsItem/Identification/NewsIdentifier/RevisionId')[0]
        self.assertEqual(revisionid.text, '2')
        self.assertDictEqual(dict(revisionid.attrib), {'Update': 'N', 'PreviousRevision': '0'})
        self.assertEqual(
            self.newsml.xpath('NewsItem/Identification/NewsIdentifier/PublicIdentifier')[0].text,
            'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5:2N'
        )

    def test_newsmanagement(self):
        # NewsML -> NewsItem -> NewsManagement
        newsitemtype = self.newsml.xpath('NewsItem/NewsManagement/NewsItemType')[0]
        self.assertDictEqual(
            dict(newsitemtype.attrib),
            {'FormalName': 'NEWS'}
        )
        self.assertIsNone(newsitemtype.text)
        self.assertEqual(
            self.newsml.xpath('NewsItem/NewsManagement/FirstCreated')[0].text,
            '20190403T144153'
        )
        self.assertEqual(
            self.newsml.xpath('NewsItem/NewsManagement/ThisRevisionCreated')[0].text,
            '20190403T144514'
        )
        status = self.newsml.xpath('NewsItem/NewsManagement/Status')[0]
        self.assertDictEqual(
            dict(status.attrib),
            {'FormalName': 'USABLE'}
        )
        self.assertIsNone(status.text)

    def test_1_level_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent
        newscomponent_1_level = self.newsml.xpath('NewsItem/NewsComponent')[0]
        self.assertDictEqual(
            dict(newscomponent_1_level.attrib),
            {
                'Duid': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
                '{http://www.w3.org/XML/1998/namespace}lang': 'fr'
            }
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            self.newsml.xpath('NewsItem/NewsComponent/NewsLines/HeadLine')[0].text,
            'New Skoda Scala'
        )
        # NewsML -> NewsItem -> NewsComponent -> AdministrativeMetadata
        self.assertIsNone(
            self.newsml.xpath('NewsItem/NewsComponent/AdministrativeMetadata')[0].text
        )
        # NewsML -> NewsItem -> NewsComponent -> DescriptiveMetadata -> Genre
        self.assertDictEqual(
            dict(self.newsml.xpath('NewsItem/NewsComponent/DescriptiveMetadata/Genre')[0].attrib),
            {'FormalName': 'ANALYSIS'}
        )

    def test_belga_text_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath('NewsItem/NewsComponent/NewsComponent')[0]
        self.assertDictEqual(
            dict(newscomponent_2_level.attrib),
            {
                'Duid': 'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5',
                '{http://www.w3.org/XML/1998/namespace}lang': 'fr'
            }
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> Role
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('Role')[0].attrib),
            {'FormalName': 'Belga text'}
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines
        self.assertIsNone(
            newscomponent_2_level.xpath('NewsLines/DateLine')[0].text
        )
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'New Skoda Scala'
        )
        self.assertIsNone(
            newscomponent_2_level.xpath('NewsLines/CopyrightLine')[0].text
        )
        self.assertListEqual(
            [kw.text for kw in newscomponent_2_level.xpath('NewsLines/KeywordLine')],
            ['Aruba', 'europe', 'Prague', 'CZ', 'Skoda']
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('NewsLines/NewsLine/NewsLineType')[0].attrib),
            {'FormalName': '1'}
        )
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/NewsLine/NewsLineText')[0].text,
            'line text is here'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> AdministrativeMetadata
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Provider/Party')[0].attrib),
            {'FormalName': '1'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Creator/Party')[0].attrib),
            {'FormalName': 'adm', 'Topic': 'AUTHOR'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Creator/Party')[1].attrib),
            {'FormalName': 'OLEG', 'Topic': 'EDITOR'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Contributor/Party')[0].attrib),
            {'FormalName': 'John'}
        )
        expected_attribs = (
            {'FormalName': 'Validator', 'Value': 'adm'},
            {'FormalName': 'ValidationDate', 'Value': '20190403T144514'},
            {'FormalName': 'ForeignId', 'Value': '4444444'},
            {'FormalName': 'Priority', 'Value': '4'},
            {'FormalName': 'Topic', 'Value': 'skoda scala'},
            {'FormalName': 'NewsObjectId', 'Value':
                'urn:newsml:localhost:5000:2019-04-03T15:41:53.479892:1628c9b4-6261-42c8-ad43-77c132bc0ba5'},
            {'FormalName': 'EditorialInfo', 'Value': 'Vestibulum ac diam sit amet quam vehicula elementum '
                                                     'sed sit amet dui.'},
            {'FormalName': 'Distribution', 'Value': 'B'},
            {'FormalName': 'Label', 'Value': 'A1'},
            {'FormalName': 'Label', 'Value': 'A2'},
            {'FormalName': 'Label', 'Value': 'R1'},
            {'FormalName': 'NewsPackage'},
            {'FormalName': 'NewsPackage'},
            {'FormalName': 'NewsPackage'},
            {'FormalName': 'NewsPackage'},
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in newscomponent_2_level.xpath('AdministrativeMetadata/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )

        expected_attribs = (
            {'FormalName': 'NewsService', 'Value': 'BIN'},
            {'FormalName': 'NewsProduct', 'Value': 'ALG'},
            {'FormalName': 'NewsService', 'Value': 'EXT'},
            {'FormalName': 'NewsProduct', 'Value': 'ECO'},
            {'FormalName': 'NewsService', 'Value': 'NEWS'},
            {'FormalName': 'NewsProduct', 'Value': 'ENTERTAINMENT'},
            {'FormalName': 'NewsService', 'Value': 'NEWS'},
            {'FormalName': 'NewsProduct', 'Value': 'SPORTS'}
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in newscomponent_2_level.xpath('AdministrativeMetadata/Property/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Source/Party')[0].attrib),
            {'FormalName': 'DPA/ANP'}
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> DescriptiveMetadata
        descriptivemetadata = newscomponent_2_level.xpath('DescriptiveMetadata')[0]
        self.assertDictEqual(
            dict(descriptivemetadata.attrib),
            {'DateAndTime': '20190403T144153'}
        )
        self.assertIsNone(
            descriptivemetadata.xpath('SubjectCode')[0].text
        )
        expected_attribs = (
            {'FormalName': 'City', 'Value': 'Prague'},
            {'FormalName': 'Country', 'Value': 'Belgique'},
            {'FormalName': 'CountryArea'},
            {'FormalName': 'WorldRegion'}
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in descriptivemetadata.xpath('Location/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        newscomponent_3_level = newscomponent_2_level.xpath('NewsComponent')[0]
        self.assertDictEqual(
            dict(newscomponent_3_level.attrib),
            {
                '{http://www.w3.org/XML/1998/namespace}lang': 'fr'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('Role')[0].attrib),
            {
                'FormalName': 'Body',
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('DescriptiveMetadata/Property')[0].attrib),
            {
                'FormalName': 'ComponentClass',
                'Value': 'Text'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('ContentItem/Format')[0].attrib),
            {
                'FormalName': 'Text'
            }
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/DataContent')[0].text,
            """Donec rutrum congue leo eget malesuada. Sed porttitor lectus nibh. Pellentesque in ipsum id orci porta dapibus. Praesent sapien massa, convallis a pellentesque nec, egestas non nisi.
     books
     Praesent sapien massa, convallis a pellentesque nec, egestas non nisi. Curabitur aliquet quam id dui posuere blandit. Vivamus suscipit tortor eget felis porttitor volutpat. Praesent sapien massa, convallis a pellentesque nec, egestas non nisi. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae.""" # noqa
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/Characteristics/SizeInBytes')[0].text,
            '530'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        newscomponent_3_level = newscomponent_2_level.xpath('NewsComponent')[1]
        self.assertDictEqual(
            dict(newscomponent_3_level.attrib),
            {
                '{http://www.w3.org/XML/1998/namespace}lang': 'fr'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('Role')[0].attrib),
            {
                'FormalName': 'Title',
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('DescriptiveMetadata/Property')[0].attrib),
            {
                'FormalName': 'ComponentClass',
                'Value': 'Text'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('ContentItem/Format')[0].attrib),
            {
                'FormalName': 'Text'
            }
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/DataContent')[0].text,
            'New Skoda Scala'
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/Characteristics/SizeInBytes')[0].text,
            '15'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        newscomponent_3_level = newscomponent_2_level.xpath('NewsComponent')[2]
        self.assertDictEqual(
            dict(newscomponent_3_level.attrib),
            {
                '{http://www.w3.org/XML/1998/namespace}lang': 'fr'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('Role')[0].attrib),
            {
                'FormalName': 'Lead',
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('DescriptiveMetadata/Property')[0].attrib),
            {
                'FormalName': 'ComponentClass',
                'Value': 'Text'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('ContentItem/Format')[0].attrib),
            {
                'FormalName': 'Text'
            }
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/DataContent')[0].text,
            'Curabitur non nulla sit amet nisl tempus convallis quis ac lectus. Donec sollicitudin molestie malesuada. Vivamus suscipit tortor eget felis porttitor volutpat.'# noqa
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/Characteristics/SizeInBytes')[0].text,
            '160'
        )

    def test_url_newscomponent(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        self.assertEqual(
            self.newsml.xpath('count(NewsItem/NewsComponent/NewsComponent/Role[@FormalName="URL"])'),
            2
        )
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent/Role[@FormalName="URL"]'
        )[0].getparent()
        self.assertDictEqual(
            dict(newscomponent_2_level.attrib),
            {
                'Duid': 'bf744ced-ecca-4a2f-bf6d-bdd52092e31e',
                '{http://www.w3.org/XML/1998/namespace}lang': 'fr'
            }
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> Role
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('Role')[0].attrib),
            {'FormalName': 'URL'}
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines
        self.assertIsNone(
            newscomponent_2_level.xpath('NewsLines/DateLine')[0].text
        )
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'Example com'
        )
        self.assertIsNone(
            newscomponent_2_level.xpath('NewsLines/CopyrightLine')[0].text
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> AdministrativeMetadata
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Provider/Party')[0].attrib),
            {'FormalName': '1'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Creator/Party')[0].attrib),
            {'FormalName': 'adm', 'Topic': 'AUTHOR'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Creator/Party')[1].attrib),
            {'FormalName': 'OLEG', 'Topic': 'EDITOR'}
        )
        self.assertDictEqual(
            dict(newscomponent_2_level.xpath('AdministrativeMetadata/Contributor/Party')[0].attrib),
            {'FormalName': 'John'}
        )
        expected_attribs = (
            {'FormalName': 'Validator', 'Value': 'adm'},
            {'FormalName': 'ValidationDate', 'Value': '20190403T144514'},
            {'FormalName': 'ForeignId', 'Value': '4444444'},
            {'FormalName': 'Topic', 'Value': 'skoda scala'},
            {'FormalName': 'NewsObjectId', 'Value': 'bf744ced-ecca-4a2f-bf6d-bdd52092e31e'},
            {'FormalName': 'NewsPackage'},
            {'FormalName': 'NewsPackage'},
            {'FormalName': 'NewsPackage'},
            {'FormalName': 'NewsPackage'},
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in newscomponent_2_level.xpath('AdministrativeMetadata/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )

        expected_attribs = (
            {'FormalName': 'NewsService', 'Value': 'BIN'},
            {'FormalName': 'NewsProduct', 'Value': 'ALG'},
            {'FormalName': 'NewsService', 'Value': 'EXT'},
            {'FormalName': 'NewsProduct', 'Value': 'ECO'},
            {'FormalName': 'NewsService', 'Value': 'NEWS'},
            {'FormalName': 'NewsProduct', 'Value': 'ENTERTAINMENT'},
            {'FormalName': 'NewsService', 'Value': 'NEWS'},
            {'FormalName': 'NewsProduct', 'Value': 'SPORTS'}
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in newscomponent_2_level.xpath('AdministrativeMetadata/Property/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> DescriptiveMetadata
        descriptivemetadata = newscomponent_2_level.xpath('DescriptiveMetadata')[0]
        self.assertDictEqual(
            dict(descriptivemetadata.attrib),
            {'DateAndTime': '20190403T144153'}
        )
        self.assertIsNone(
            descriptivemetadata.xpath('SubjectCode')[0].text
        )
        expected_attribs = (
            {'FormalName': 'City', 'Value': 'Prague'},
            {'FormalName': 'CountryArea'},
            {'FormalName': 'WorldRegion'}
        )
        for idx, attribs in enumerate(
                [dict(p.attrib) for p in descriptivemetadata.xpath('Location/Property')]):
            self.assertDictEqual(
                attribs,
                expected_attribs[idx]
            )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        newscomponent_3_level = newscomponent_2_level.xpath('NewsComponent')[0]
        self.assertDictEqual(
            dict(newscomponent_3_level.attrib),
            {
                '{http://www.w3.org/XML/1998/namespace}lang': 'fr'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('Role')[0].attrib),
            {
                'FormalName': 'Title',
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('DescriptiveMetadata/Property')[0].attrib),
            {
                'FormalName': 'ComponentClass',
                'Value': 'Text'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('ContentItem/Format')[0].attrib),
            {
                'FormalName': 'Text'
            }
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/DataContent')[0].text,
            'Example com'
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/Characteristics/SizeInBytes')[0].text,
            '11'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        newscomponent_3_level = newscomponent_2_level.xpath('NewsComponent')[1]
        self.assertDictEqual(
            dict(newscomponent_3_level.attrib),
            {
                '{http://www.w3.org/XML/1998/namespace}lang': 'fr'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('Role')[0].attrib),
            {
                'FormalName': 'Locator',
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('DescriptiveMetadata/Property')[0].attrib),
            {
                'FormalName': 'ComponentClass',
                'Value': 'Text'
            }
        )
        self.assertDictEqual(
            dict(newscomponent_3_level.xpath('ContentItem/Format')[0].attrib),
            {
                'FormalName': 'Text'
            }
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/DataContent')[0].text,
            'http://example.com/'
        )
        self.assertEqual(
            newscomponent_3_level.xpath('ContentItem/Characteristics/SizeInBytes')[0].text,
            '19'
        )

    def test_pictures_count(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> Role
        roles = self.newsml.xpath('NewsItem/NewsComponent/NewsComponent/Role[@FormalName="Picture"]')
        # count
        self.assertEqual(len(roles), 6)

    def test_gallery_count(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> Role
        roles = self.newsml.xpath('NewsItem/NewsComponent/NewsComponent/Role[@FormalName="Gallery"]')
        # count
        self.assertEqual(len(roles), 2)

    def test_audio_count(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> Role
        roles = self.newsml.xpath('NewsItem/NewsComponent/NewsComponent/Role[@FormalName="Audio"]')
        # count
        self.assertEqual(len(roles), 1)

    def test_video_count(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> Role
        roles = self.newsml.xpath('NewsItem/NewsComponent/NewsComponent/Role[@FormalName="Video"]')
        # count
        self.assertEqual(len(roles), 1)

    def test_related_document_count(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> Role
        roles = self.newsml.xpath('NewsItem/NewsComponent/NewsComponent/Role[@FormalName="RelatedDocument"]')
        # count
        self.assertEqual(len(roles), 1)

    def test_related_article_count(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> Role
        roles = self.newsml.xpath('NewsItem/NewsComponent/NewsComponent/Role[@FormalName="RelatedArticle"]')
        # count
        self.assertEqual(len(roles), 2)

    def test_uploaded_picture_in_editor(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="tag:localhost:5000:2019:7999396b-23a7-4642-94f4-55a09624d7ec"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CreditLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'Mazda MX5 retro'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CopyrightLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CopyrightLine')[0].text,
            'Belga'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> KeywordLine
        keywords = ('japan', 'tokyo', 'mazda')
        for i, keywordline in enumerate(newscomponent_2_level.xpath('NewsLines/KeywordLine')):
            self.assertEqual(
                keywordline.text,
                keywords[i]
            )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> AdministrativeMetadata -> Creator
        party = newscomponent_2_level.xpath('AdministrativeMetadata/Creator/Party')
        self.assertDictEqual(
            dict(party[0].attrib),
            {'FormalName': 'adm', 'Topic': 'AUTHOR'}
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> AdministrativeMetadata -> Property[Priority]
        priority = newscomponent_2_level.xpath('AdministrativeMetadata/Property[@FormalName="Priority"]')[0]
        self.assertEqual(
            priority.attrib['Value'],
            '3'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> AdministrativeMetadata -> Property[NewsObjectId]
        newsobjectid = newscomponent_2_level.xpath(
            'AdministrativeMetadata/Property[@FormalName="NewsObjectId"]'
        )[0]
        self.assertEqual(
            newsobjectid.attrib['Value'],
            'tag:localhost:5000:2019:7999396b-23a7-4642-94f4-55a09624d7ec'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> AdministrativeMetadata -> Source
        source = newscomponent_2_level.xpath('AdministrativeMetadata/Source/Party')[0]
        self.assertEqual(
            source.attrib['FormalName'],
            'Belga_on_the_spot'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> DescriptiveMetadata[DateAndTime]
        descriptivemetadata = newscomponent_2_level.xpath('DescriptiveMetadata')[0]
        self.assertEqual(
            descriptivemetadata.attrib['DateAndTime'],
            '20190819T151501'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> DescriptiveMetadata -> Location
        property = newscomponent_2_level.xpath('DescriptiveMetadata/Location/Property[@FormalName="City"]')[0]
        self.assertEqual(
            property.attrib['Value'],
            'Tokio'
        )
        property = newscomponent_2_level.xpath('DescriptiveMetadata/Location/Property[@FormalName="Country"]')[0]
        self.assertEqual(
            property.attrib['Value'],
            'Tchéquie' # language is inherited from parent item
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(title) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'Mazda MX5 retro'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '15'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(caption) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent/ContentItem/DataContent'
        )
        self.assertEqual(
            datacontent[0].text,
            'Mazda MX5 retro 1990'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '20'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Image) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:pic_1'
        )
        _format = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent/ContentItem/Format'
        )[0]
        self.assertEqual(
            _format.attrib['FormalName'],
            'Jpeg'
        )
        mimetype = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent/ContentItem/MimeType'
        )[0]
        self.assertEqual(
            mimetype.attrib['FormalName'],
            'image/jpeg'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )[0]
        self.assertEqual(
            sizeinbytes.text,
            '15'
        )
        property = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/Property[@FormalName="Width"]'
        )[0]
        self.assertEqual(
            property.attrib['Value'],
            '3000'
        )
        property = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/Property[@FormalName="Height"]'
        )[0]
        self.assertEqual(
            property.attrib['Value'],
            '2000'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Thumbnail) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Thumbnail"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:pic_1'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Preview) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Preview"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:pic_1'
        )

    def test_belga_picture_in_editor(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="urn:belga.be:image:154620545"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CreditLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            '20190827_zap_d99_014.jpg'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CopyrightLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CopyrightLine')[0].text,
            None
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> KeywordLine
        self.assertEqual(
            newscomponent_2_level.xpath('count(NewsLines/KeywordLine)'),
            0
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> AdministrativeMetadata -> Property[NewsObjectId]
        newsobjectid = newscomponent_2_level.xpath(
            'AdministrativeMetadata/Property[@FormalName="NewsObjectId"]'
        )[0]
        self.assertEqual(
            newsobjectid.attrib['Value'],
            'urn:belga.be:image:154620545'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> AdministrativeMetadata -> Source
        source = newscomponent_2_level.xpath('AdministrativeMetadata/Source/Party')[0]
        self.assertEqual(
            source.attrib['FormalName'],
            'ZUMAPRESS'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> DescriptiveMetadata[DateAndTime]
        descriptivemetadata = newscomponent_2_level.xpath('DescriptiveMetadata')[0]
        self.assertEqual(
            descriptivemetadata.attrib['DateAndTime'],
            '20190828T112217'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(title) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            '20190827_zap_d99_014.jpg'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '24'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(caption) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent/ContentItem/DataContent'
        )
        self.assertEqual(
            datacontent[0].text,
            'August 27, 2019: Gaza, Palestine. 27 August 2019.The Al-Azza team defeats the Qalat Al-Janoub team 3-0 in '
            'the opening match of the amputees football league. The match has been organized by the Palestine Amputee F'
            'ootball Association under the auspices of the International Committee of the Red Cross (ICRC) and was held'
            ' at the Palestine stadium in Gaza City. Although some of the players were either born disable or lost thei'
            'r limbs in the three recent Israeli offensives on Gaza, many others have lost their limbs in recent months'
            ' after being shot by Israeli forces while taking part in the Great March of Return rallies along the Gaza-'
            'Israeli border. The ICRC in Gaza believes in the importance of supporting people with disabilities caused '
            'by military conflicts and in reintegrating them into society through both psychological and physical rehab'
            'ilitation.'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '858'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Image) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:picturestore:154620545:full:true'
        )
        _format = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent/ContentItem/Format'
        )[0]
        self.assertEqual(
            _format.attrib['FormalName'],
            'Jpeg'
        )
        property = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/Property[@FormalName="Width"]'
        )[0]
        self.assertEqual(
            property.attrib['Value'],
            '5472'
        )
        property = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/Property[@FormalName="Height"]'
        )[0]
        self.assertEqual(
            property.attrib['Value'],
            '3648'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Thumbnail) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Thumbnail"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:picturestore:154620545:thumbnail:true'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Preview) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Preview"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:picturestore:154620545:preview:true'
        )

    def test_uploaded_picture_related_images(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="tag:localhost:5000:2019:bb1f22ac-d33a-4b31-8ed6-2c7889373c78"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CreditLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'History'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CopyrightLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CopyrightLine')[0].text,
            None
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> KeywordLine
        keywords = ('one', 'two', 'three')
        for i, keywordline in enumerate(newscomponent_2_level.xpath('NewsLines/KeywordLine')):
            self.assertEqual(
                keywordline.text,
                keywords[i]
            )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Image) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:pic_2'
        )
        _format = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent/ContentItem/Format'
        )[0]
        self.assertEqual(
            _format.attrib['FormalName'],
            'Jpeg'
        )
        property = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/Property[@FormalName="Width"]'
        )[0]
        self.assertEqual(
            property.attrib['Value'],
            '1920'
        )
        property = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/Property[@FormalName="Height"]'
        )[0]
        self.assertEqual(
            property.attrib['Value'],
            '1280'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Thumbnail) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Thumbnail"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:pic_2'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Preview) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Preview"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:pic_2'
        )

    def test_belga_picture_related_images(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="urn:belga.be:image:154670415"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Image) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:picturestore:154670415:full:true'
        )
        property = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/Property[@FormalName="Width"]'
        )[0]
        self.assertEqual(
            property.attrib['Value'],
            '4288'
        )
        property = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/Property[@FormalName="Height"]'
        )[0]
        self.assertEqual(
            property.attrib['Value'],
            '3012'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Thumbnail) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Thumbnail"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:picturestore:154670415:thumbnail:true'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Preview) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Preview"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:picturestore:154670415:preview:true'
        )

    def test_uploaded_picture_related_gallery(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="tag:localhost:5000:2019:c9d059aa-4056-4009-9e26-06cf718badaa"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Image) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:pic_3'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Thumbnail) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Thumbnail"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:pic_3'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Preview) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Preview"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:pic_3'
        )

    def test_belga_picture_related_gallery(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="urn:belga.be:image:147832075"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Image) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Image"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:picturestore:147832075:full:true'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Thumbnail) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Thumbnail"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:picturestore:147832075:thumbnail:true'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Preview) -> ContentItem
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Preview"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:picturestore:147832075:preview:true'
        )

    def test_belga_coverages(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="urn:belga.be:coverage:6690595"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CreditLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'RUSSIAN PARAGLIDING CHAMPIONSHIP IN STAVROPOL TERRITORY'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(title) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'RUSSIAN PARAGLIDING CHAMPIONSHIP IN STAVROPOL TERRITORY'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '55'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(caption) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent/ContentItem/DataContent'
        )
        self.assertEqual(
            datacontent[0].text,
            'STAVROPOL TERRITORY, RUSSIA - AUGUST 28, 2019: Contestants during the 2019 Russian Paragliding Championshi'
            'p on Mount Yutsa. Anton Podgaiko/TASS 0'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '145'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Component"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:belgagallery:6690595'
        )
        _format = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Component"]/ancestor::NewsComponent/ContentItem/Format'
        )[0]
        self.assertEqual(
            _format.attrib['FormalName'],
            'Jpeg',
        )

    def test_belga_coverage_custom_field(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="urn:belga.be:coverage:6666666"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CreditLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'JUDO   JPN   WORLD'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(title) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'JUDO   JPN   WORLD'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '18'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(caption) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent/ContentItem/DataContent'
        )
        self.assertEqual(
            datacontent[0].text,
            'Noel Van T End of Netherlands (L) celebrates after winning the gold medal.'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Caption"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '74'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Component"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:belgagallery:6666666'
        )
        _format = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Component"]/ancestor::NewsComponent/ContentItem/Format'
        )[0]
        self.assertEqual(
            _format.attrib['FormalName'],
            'Jpeg',
        )

    def test_audio_in_editor_and_related(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="tag:localhost:5000:2019:a0b22047-4620-435a-8042-8f9ee24c282f"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CreditLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'audio head'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(title) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'audio head'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '10'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Body) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'Some desc is here'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )[0]
        self.assertEqual(
            sizeinbytes.text,
            '17'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Sound"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:audio_1'
        )
        _format = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Sound"]/ancestor::NewsComponent/ContentItem/Format'
        )[0]
        self.assertEqual(
            _format.attrib['FormalName'],
            'Mp3'
        )
        mimetype = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Sound"]/ancestor::NewsComponent/ContentItem/MimeType'
        )[0]
        self.assertEqual(
            mimetype.attrib['FormalName'],
            'audio/mp3'
        )

    def test_video_in_editor_and_related(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="tag:localhost:5000:2019:3fe341ab-45d8-4f72-9308-adde548daef8"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CreditLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'water'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(title) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'water'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '5'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Body) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'water'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )[0]
        self.assertEqual(
            sizeinbytes.text,
            '5'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Clip"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:video_1'
        )
        _format = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Clip"]/ancestor::NewsComponent/ContentItem/Format'
        )[0]
        self.assertEqual(
            _format.attrib['FormalName'],
            'Mpeg4'
        )
        mimetype = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Clip"]/ancestor::NewsComponent/ContentItem/MimeType'
        )[0]
        self.assertEqual(
            mimetype.attrib['FormalName'],
            'video/mp4'
        )

    def test_attachment(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="5d692b76c8f549e289b0270b"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CreditLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'booktype pdf'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(title) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'booktype pdf'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '12'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Body) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'A pdf cover for a book'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )[0]
        self.assertEqual(
            sizeinbytes.text,
            '22'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        contentitem = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Component"]/ancestor::NewsComponent/ContentItem'
        )[0]
        self.assertEqual(
            contentitem.attrib['Href'],
            'urn:www.belga.be:superdesk:tst:pdf_1'
        )
        _format = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Component"]/ancestor::NewsComponent/ContentItem/Format'
        )[0]
        self.assertEqual(
            _format.attrib['FormalName'],
            'Pdf'
        )
        mimetype = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Component"]/ancestor::NewsComponent/ContentItem/MimeType'
        )[0]
        self.assertEqual(
            mimetype.attrib['FormalName'],
            'application/pdf'
        )

    def test_related_article_internal(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="urn:newsml:localhost:5000:2019-09-16T16:15:29.975832:2cbd7b49-9d7b-48c5-b1a0-fc802f3f4413"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CreditLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            '100 let'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(title) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            '100 let'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '7'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Body) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            '100 let of citroen in body'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )[0]
        self.assertEqual(
            sizeinbytes.text,
            '26'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        _format = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/Format'
        )[0]
        self.assertEqual(
            _format.attrib['FormalName'],
            'Text'
        )

    def test_related_article_belga_archive_text(self):
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent
        newscomponent_2_level = self.newsml.xpath(
            'NewsItem/NewsComponent/NewsComponent'
            '[@Duid="urn:belga.be:360archive:77777777"]'
        )[0]

        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> CreditLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/CreditLine')[0].text,
            'BELGA'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsLines -> HeadLine
        self.assertEqual(
            newscomponent_2_level.xpath('NewsLines/HeadLine')[0].text,
            'Vasil Kiryienka (38) doet ondanks hartproblemen verder bij INEOS'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(title) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'Vasil Kiryienka (38) doet ondanks hartproblemen verder bij INEOS'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )
        self.assertEqual(
            sizeinbytes[0].text,
            '64'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent(Body) -> ContentItem
        datacontent = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent/ContentItem/DataContent'
        )[0]
        self.assertEqual(
            datacontent.text,
            'Kiryienka werd dit jaar opgeschrikt door een hartprobleem.'
        )
        sizeinbytes = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Body"]/ancestor::NewsComponent'
            '/ContentItem/Characteristics/SizeInBytes'
        )[0]
        self.assertEqual(
            sizeinbytes.text,
            '58'
        )
        # NewsML -> NewsItem -> NewsComponent -> NewsComponent -> NewsComponent
        _format = newscomponent_2_level.xpath(
            'NewsComponent/Role[@FormalName="Title"]/ancestor::NewsComponent/ContentItem/Format'
        )[0]
        self.assertEqual(
            _format.attrib['FormalName'],
            'Text'
        )
