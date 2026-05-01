from unittest import TestCase
import datetime
import json
from flask import render_template
from app import get_app
from bson import ObjectId
from belga.planning_exports.format_news_events_tommorow_bilingual import (
    format_event_for_tommorow_bilingual,
)
from belga.planning_exports.internal_bilingual_events_advisory_tomorrow import (
    format_event_for_tommorow_bilingual_internal,
)
from belga.planning_exports.internal_bilingual_planning_advisory_tomorrow import (
    format_planning_for_tomorrow_bilingual_internal,
)


class PlanningExportTests(TestCase):
    app = get_app()
    events_for_week = [
        {
            "type": "event",
            "calendars": [{"is_active": True, "name": "Sport", "qcode": "sport"}],
            "language": "en",
            "name": "First",
            "dates": {
                "start": datetime.datetime(
                    2024, 4, 22, 10, 30, tzinfo=datetime.timezone.utc
                ),
                "end": datetime.datetime(
                    2024, 4, 23, 15, 30, 59, tzinfo=datetime.timezone.utc
                ),
                "tz": "Asia/Calcutta",
            },
            "subject": [
                {
                    "name": "WC2028",
                    "scheme": "belga-keywords",
                    "qcode": "WC2028",
                    "translations": {"name": {"nl": "WC2028", "fr": "WC2028"}},
                },
                {
                    "name": "REDWOLVES",
                    "scheme": "belga-keywords",
                    "qcode": "REDWOLVES",
                    "translations": {"name": {"nl": "REDWOLVES", "fr": "REDWOLVES"}},
                },
            ],
            "location": [
                {
                    "name": "Rabat ⵔⴱⴰⵟ الرباط",
                    "qcode": "560fa29d-abc7-45f6-888f-b123ba044567",
                    "address": {
                        "line": [""],
                        "city": "Rabat",
                        "state": "Rabat-Salé-Kénitra",
                        "locality": "Rabat",
                        "area": "Rabat Prefecture",
                        "country": "Morocco",
                        "type": "administrative",
                    },
                    "location": {"lat": 34.02236, "lon": -6.8340222},
                }
            ],
            "links": ["www.google.xom/new"],
        },
        {
            "type": "event",
            "calendars": [{"is_active": True, "name": "Sport", "qcode": "sport"}],
            "name": "second",
            "language": "en",
            "dates": {
                "start": datetime.datetime(
                    2024, 4, 22, 10, 30, tzinfo=datetime.timezone.utc
                ),
                "end": datetime.datetime(
                    2024, 4, 23, 15, 30, 59, tzinfo=datetime.timezone.utc
                ),
                "tz": "Asia/Calcutta",
            },
            "subject": [
                {
                    "name": "WC2028",
                    "scheme": "belga-keywords",
                    "qcode": "WC2028",
                    "translations": {"name": {"nl": "WC2028", "fr": "WC2028"}},
                }
            ],
            "links": ["www.google.xom/new"],
        },
        {
            "type": "event",
            "occur_status": {
                "qcode": "eocstat:eos5",
                "name": "Planned, occurs certainly",
                "label": "Planned, occurs certainly",
            },
            "calendars": [{"is_active": True, "name": "Sport", "qcode": "sport"}],
            "language": "en",
            "languages": ["en"],
            "description_text": "Description of event",
            "slugline": "SLugline of the event",
            "name": "NExxxxt Sunday 21.04.2024",
            "dates": {
                "start": datetime.datetime(
                    2024, 4, 21, 10, 30, tzinfo=datetime.timezone.utc
                ),
                "end": datetime.datetime(
                    2024, 4, 22, 15, 30, 59, tzinfo=datetime.timezone.utc
                ),
                "tz": "Asia/Calcutta",
            },
            "subject": [
                {
                    "name": "REDWOLVES",
                    "scheme": "belga-keywords",
                    "qcode": "REDWOLVES",
                    "translations": {"name": {"nl": "REDWOLVES", "fr": "REDWOLVES"}},
                }
            ],
            "location": [
                {
                    "address": {
                        "country": "United States",
                        "city": "New York",
                        "line": [""],
                        "locality": "New York",
                        "state": "New York",
                        "type": "administrative",
                    },
                    "name": "City of New York",
                    "qcode": "5cad7a33-55ea-479d-8b17-eb638fdaedf6",
                    "location": {"lon": -74.0060152, "lat": 40.7127281},
                    "formatted_address": "New York New York United States",
                }
            ],
            "links": ["www.google.xom/new"],
            "translations": [
                {
                    "field": "name",
                    "language": "nl",
                    "value": "NExxxxt Sunday 21.04.2024 NL",
                },
                {
                    "field": "name",
                    "language": "fr",
                    "value": "NExxxxt Sunday 21.04.2024 FR",
                },
                {
                    "field": "description_text",
                    "language": "nl",
                    "value": "Description of event NL",
                },
                {
                    "field": "description_text",
                    "language": "fr",
                    "value": "Description of event FR",
                },
            ],
        },
        {
            "type": "event",
            "occur_status": {
                "qcode": "eocstat:eos5",
                "name": "Planned, occurs certainly",
                "label": "Planned, occurs certainly",
            },
            "calendars": [{"is_active": True, "name": "Sport", "qcode": "sport"}],
            "language": "en",
            "languages": ["en"],
            "description_text": "Description of event",
            "slugline": "SLugline of the event",
            "name": "NExxxxt Monday 22.04.2024",
            "dates": {
                "start": datetime.datetime(
                    2024, 4, 22, 10, 30, tzinfo=datetime.timezone.utc
                ),
                "end": datetime.datetime(
                    2024, 4, 23, 15, 30, 59, tzinfo=datetime.timezone.utc
                ),
                "tz": "Asia/Calcutta",
            },
            "subject": [
                {
                    "name": "SPORTS",
                    "scheme": "belga-keywords",
                    "qcode": "SPORTS",
                    "translations": {"name": {"nl": "SPORTS", "fr": "SPORTS"}},
                }
            ],
            "location": [
                {
                    "name": "street",
                    "qcode": "9baf5379-908e-44b0-804b-3cce32e76d44",
                    "address": {
                        "line": [""],
                        "city": "Kubang Putiah",
                        "state": "West-Sumatra",
                        "locality": "West-Sumatra",
                        "area": "Kubang Putiah",
                        "postal_code": "26132",
                        "country": "Indonesien",
                        "boundingbox": [
                            "-0.3262313",
                            "-0.3228646",
                            "100.3965010",
                            "100.3977960",
                        ],
                        "type": "stream",
                    },
                    "location": {"lat": -0.3246836, "lon": 100.3975641},
                    "formatted_address": "Kubang Putiah West-Sumatra 26132 Indonesien",
                }
            ],
            "links": ["www.google.xom/new"],
        },
    ]
    events_for_tommorow = [
        {
            "calendars": [
                {"is_active": True, "name": "(7) Sports", "qcode": "Sports"},
            ],
            "description_text": "Description of event",
            "name": "NExxxxt Sunday 21.04.2024",
            "dates": {
                "start": datetime.datetime(
                    2024, 4, 21, 10, 30, tzinfo=datetime.timezone.utc
                ),
                "end": datetime.datetime(
                    2024, 4, 22, 15, 30, 59, tzinfo=datetime.timezone.utc
                ),
                "tz": "Asia/Calcutta",
            },
            "location": [
                {
                    "address": {
                        "country": "United States",
                        "city": "New York",
                        "line": [""],
                        "locality": "New York",
                        "state": "New York",
                        "type": "administrative",
                    },
                    "name": "City of New York",
                    "qcode": "5cad7a33-55ea-479d-8b17-eb638fdaedf6",
                    "location": {"lon": -74.0060152, "lat": 40.7127281},
                    "formatted_address": "New York New York United States",
                }
            ],
            "links": ["www.google.xom/new"],
            "event_contact_info": [
                "5ab491271d41c88e98ad9336",
                "6618415a1704a42950a4eb62",
            ],
            "planning_ids": [ObjectId("6618415a1704a42950a4eb64")],
        },
        {
            "calendars": [{"is_active": True, "name": "(7) Sports", "qcode": "sports"}],
            "description_text": "Description of event",
            "name": "NExxxxt Monday 22.04.2024",
            "dates": {
                "start": datetime.datetime(
                    2024, 4, 24, 22, 00, 00, tzinfo=datetime.timezone.utc
                ),
                "end": datetime.datetime(
                    2024, 4, 25, 21, 59, 59, tzinfo=datetime.timezone.utc
                ),
                "tz": "Europe/Prague",
            },
            "links": ["www.google.xom/new"],
            "event_contact_info": [
                "5ab491271d41c88e98ad9336",
                "6618415a1704a42950a4eb62",
            ],
            "location": [
                {
                    "name": "Oud Gerechtshof",
                    "address": {
                        "line": ["10 Havermarkt"],
                        "city": "Hasselt",
                        "state": "Limburg",
                        "locality": "Limburg",
                        "area": "Hasselt",
                        "postal_code": "3500",
                        "country": "Belgium",
                    },
                    "qcode": "460fa29d-abc7-45f6-888f-b123ba044567",
                    "location": {"lon": -74.0060152, "lat": 40.7127281},
                }
            ],
            "planning_ids": [ObjectId("6618415a1704a42950a4eb64")],
        },
        {
            "calendars": [
                {"is_active": True, "name": "(1) General", "qcode": "general"}
            ],
            "description_text": "Description of event",
            "name": "another one",
            "dates": {
                "start": datetime.datetime(
                    2024, 4, 24, 22, 00, 00, tzinfo=datetime.timezone.utc
                ),
                "end": datetime.datetime(
                    2024, 4, 25, 21, 59, 59, tzinfo=datetime.timezone.utc
                ),
                "tz": "Europe/Prague",
            },
            "links": ["www.google.xom/new"],
            "event_contact_info": [
                "5ab491271d41c88e98ad9336",
                "6618415a1704a42950a4eb62",
            ],
            "location": [
                {
                    "name": "Москва",
                    "address": {
                        "line": ["Москва"],
                        "city": "Moscow",
                        "state": "Moscow",
                        "locality": "Moscow",
                        "country": "Russia",
                    },
                    "qcode": "d0b15bb0-0254-4f89-9855-e74afb531d69",
                    "location": {"lon": -74.0060152, "lat": 40.7127281},
                }
            ],
            "planning_ids": [ObjectId("6618415a1704a42950a4eb64")],
        },
        {
            "calendars": [
                {"is_active": True, "name": "(3) Economy", "qcode": "Economy"}
            ],
            "description_text": "Description of event",
            "name": "another two",
            "dates": {
                "start": datetime.datetime(
                    2024, 4, 24, 22, 00, 00, tzinfo=datetime.timezone.utc
                ),
                "end": datetime.datetime(
                    2024, 4, 25, 21, 59, 59, tzinfo=datetime.timezone.utc
                ),
                "tz": "Europe/Prague",
            },
            "links": ["www.google.xom/new"],
            "event_contact_info": [
                "5ab491271d41c88e98ad9336",
                "6618415a1704a42950a4eb62",
            ],
            "planning_ids": [ObjectId("6618415a1704a42950a4eb64")],
        },
    ]

    def setUp(self) -> None:
        super().setUp()
        with self.app.app_context():
            contact = [
                {
                    "_id": ObjectId("5ab491271d41c88e98ad9336"),
                    "contact_email": ["jdoe@fubar.com"],
                    "is_active": True,
                    "website": "fubar.com",
                    "public": False,
                    "last_name": "Doe",
                    "mobile": [
                        {"public": False, "number": "999", "usage": "Private Mobile"},
                        {"public": True, "number": "666", "usage": "Office Mobile"},
                    ],
                    "organisation": "FUBAR",
                    "first_name": "John",
                    "country": {"name": "Australia", "qcode": "aus"},
                    "city": "Sydney",
                    "job_title": "Media Contact",
                    "honorific": "Mr",
                    "contact_phone": [
                        {"usage": "Business", "public": True, "number": "99999999"}
                    ],
                },
                {
                    "_id": ObjectId("6618415a1704a42950a4eb62"),
                    "contact_email": ["funkbio@fubar.com"],
                    "is_active": True,
                    "website": "funkbar.com",
                    "public": True,
                    "contact_state": {"name": "New South Wales", "qcode": "NSW"},
                    "last_name": "Doe",
                    "mobile": [
                        {"public": False, "number": "999", "usage": "Private Mobile"},
                        {"public": True, "number": "666", "usage": "Office Mobile"},
                    ],
                    "organisation": "FUBAR",
                    "first_name": "Billiam",
                    "job_title": "Associate Consultant",
                    "honorific": "Mr",
                    "contact_phone": [
                        {"usage": "Business", "public": True, "number": "99999999"}
                    ],
                },
            ]
            self.app.data.insert("contacts", contact)
            planning_item = [
                {
                    "_id": ObjectId("6618415a1704a42950a4eb64"),
                    "type": "planning",
                    "coverages": [
                        {
                            "coverage_id": "cov1",
                            "planning": {
                                "g2_content_type": "text",
                                "slugline": "coverage slugline FR",
                                "ednote": "test coverage, I want 250 words",
                                "scheduled": "2029-10-12T14:00:00+0000",
                                "language": "fr",
                            },
                            "news_coverage_status": {
                                "qcode": "ncostat:notdec",
                                "name": "coverage not decided yet",
                                "label": "On merit",
                            },
                            "assigned_to": {
                                "user": "59f7f0881d41c88cab3f2a99",
                                "desk": "desk1",
                                "state": "in_progress",
                            },
                        },
                        {
                            "coverage_id": "cov2",
                            "planning": {
                                "g2_content_type": "picture",
                                "slugline": "coverage slugline NL",
                                "ednote": "test coverage, I want 250 words",
                                "scheduled": "2029-10-12T14:00:00+0000",
                                "language": "nl",
                            },
                            "news_coverage_status": {
                                "qcode": "ncostat:int",
                                "name": "coverage intended",
                                "label": "Planned",
                            },
                            "assigned_to": {
                                "user": "59f7f0881d41c88cab3f2a99",
                                "desk": "desk1",
                                "state": "in_progress",
                            },
                        },
                    ],
                }
            ]
            self.app.data.insert("planning", planning_item)
            location = [
                {
                    "_id": ObjectId("6694ed90bc490974d1ad3454"),
                    "unique_name": "Rabat, Hassan حسان, باشوية الرباط, Rabat Prefecture, Rabat-Salé-Kénitra, Morocco",
                    "is_active": True,
                    "name": "Rabat ⵔⴱⴰⵟ الرباط",
                    "address": {
                        "line": [""],
                        "city": "Rabat",
                        "state": "Rabat-Salé-Kénitra",
                        "locality": "Rabat",
                        "area": "Rabat Prefecture",
                        "country": "Morocco",
                    },
                    "translations": {
                        "name": {
                            "name": "Rabat ⵔⴱⴰⵟ الرباط",
                            "name:ar": "الرباط",
                            "name:be": "Рабат",
                            "name:bn": "রাবাত",
                            "name:en": "Rabat-en",
                            "name:fr": "Rabat",
                        }
                    },
                    "guid": "560fa29d-abc7-45f6-888f-b123ba044567",
                },
                {
                    "_id": ObjectId("6794ed90bc490974d1ad3454"),
                    "unique_name": "Oud Gerechtshof, 10, Havermarkt, Limburg, Vlaanderen, 3500, België",
                    "is_active": True,
                    "address": {
                        "line": ["10 Havermarkt"],
                        "city": "Hasselt",
                        "state": "Limburg",
                        "locality": "Limburg",
                        "area": "Hasselt",
                        "postal_code": "3500",
                        "country": "Belgium",
                    },
                    "name": "Oud Gerechtshof",
                    "translations": {"name": {"name": "Oud Gerechtshof"}},
                    "guid": "460fa29d-abc7-45f6-888f-b123ba044567",
                },
                {
                    "_id": ObjectId("7794ed90bc490974d1ad3454"),
                    "unique_name": "Moscow, Central Federal District, Russia",
                    "is_active": True,
                    "address": {
                        "line": [""],
                        "city": "Moscow",
                        "state": "Moscow",
                        "locality": "Moscow",
                        "country": "Russia",
                    },
                    "name": "Москва",
                    "translations": {
                        "name": {
                            "name": "Москва",
                            "name:ab": "Москва",
                            "name:af": "Moskou",
                            "name:en": "Moscow",
                        }
                    },
                    "guid": "d0b15bb0-0254-4f89-9855-e74afb531d69",
                    "formatted_address": "Moscow Moscow Russia",
                },
            ]
            self.app.data.insert("locations", location)

    def tearDown(self):
        # Clean up all documents in the contacts collection after each test
        with self.app.app_context():
            self.app.data.remove("contacts", {})
            self.app.data.remove("planning", {})
            self.app.data.remove("locations", {})

    def test_export_week(self):
        with self.app.app_context():
            events = self.events_for_week
            dutch_template_data = render_template(
                "dutch_news_events_list_export_body.html", items=events, app=self.app
            )

            self.assertIn(
                (
                    "<p>De belangrijkste sportevenementen op de Belgische en "
                    "internationale sportkalender van zondag 21 tot maandag 22 april:</p>"
                ),
                dutch_template_data,
            )
            self.assertIn("<h3>Zondag 21 april</h3>", dutch_template_data)
            self.assertIn("<h4>REDWOLVES</h4>", dutch_template_data)
            self.assertIn("<p>New York, United States</p>", dutch_template_data)

            self.assertIn("<p>16:00</p>", dutch_template_data)
            self.assertIn("<p>NExxxxt Sunday 21.04.2024 NL</p>", dutch_template_data)
            self.assertIn("<p>Description of event NL</p>", dutch_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a></p>',
                dutch_template_data,
            )
            self.assertIn("<h3>Maandag 22 april</h3>", dutch_template_data)
            self.assertIn("<h4>SPORTS</h4>", dutch_template_data)
            self.assertIn("<p>16:00</p>", dutch_template_data)
            self.assertIn("<p>NExxxxt Monday 22.04.2024</p>", dutch_template_data)
            self.assertIn("<p>Description of event</p>", dutch_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a></p>',
                dutch_template_data,
            )

            french_template_data = render_template(
                "french_news_events_list_export_body.html", items=events, app=self.app
            )
            self.assertIn(
                (
                    "<p>Principaux événements inscrits au calendrier sportif "
                    "international du dimanche 21 au lundi 22 avril :</p>"
                ),
                french_template_data,
            )
            self.assertIn("<h3>Dimanche 21 avril</h3>", french_template_data)
            self.assertIn("<h4>REDWOLVES</h4>", french_template_data)
            self.assertIn("<p>New York, United States</p>", french_template_data)

            self.assertIn("<p>16:00</p>", french_template_data)
            self.assertIn("<p>NExxxxt Sunday 21.04.2024 FR</p>", french_template_data)
            self.assertIn("<p>Description of event FR</p>", french_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a></p>',
                french_template_data,
            )
            self.assertIn("<h3>Lundi 22 avril</h3>", french_template_data)

            self.assertIn("<h4>SPORTS</h4>", french_template_data)
            self.assertIn("<p>Kubang Putiah, Indonesien</p>", french_template_data)
            self.assertIn("<p>16:00</p>", french_template_data)
            self.assertIn("<p>NExxxxt Monday 22.04.2024</p>", french_template_data)
            self.assertIn("<p>Description of event</p>", french_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a></p>',
                french_template_data,
            )

            self.assertIn("<h4>WC2028</h4>", french_template_data)
            self.assertIn("<p>16:00</p>", french_template_data)
            self.assertIn("<p>First</p>", french_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a></p>',
                french_template_data,
            )
            self.assertIn("<p>Rabat, Morocco</p>", french_template_data)
            self.assertIn("<p>second</p>", french_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a></p>',
                french_template_data,
            )

            new_events = [
                {
                    "dates": {
                        "start": datetime.datetime(
                            2024, 4, 24, 22, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                        "end": datetime.datetime(
                            2024, 4, 25, 21, 59, 59, tzinfo=datetime.timezone.utc
                        ),
                        "tz": "Europe/Prague",
                    },
                    "name": "one event",
                },
                {
                    "dates": {
                        "start": datetime.datetime(
                            2024, 4, 24, 22, 59, 0, tzinfo=datetime.timezone.utc
                        ),
                        "end": datetime.datetime(
                            2024, 4, 25, 21, 59, 59, tzinfo=datetime.timezone.utc
                        ),
                        "tz": "Europe/Prague",
                    },
                    "name": "Two event",
                },
            ]
            template_data = render_template(
                "dutch_news_events_list_export_body.html",
                items=new_events,
                app=self.app,
            )
            self.assertIn("<h3>Donderdag 25 april</h3>", template_data)
            self.assertNotIn("<p>00:00</p>", template_data)
            self.assertIn("<p>one event</p>", template_data)

            self.assertIn("<p>00:59</p>", template_data)
            self.assertIn("<p>Two event</p>", template_data)

            template_data = render_template(
                "french_news_events_list_export_body.html",
                items=new_events,
                app=self.app,
            )
            self.assertIn("<h3>Jeudi 25 avril</h3>", template_data)
            self.assertNotIn("<p>00:00</p>", template_data)
            self.assertIn("<p>one event</p>", template_data)
            self.assertIn("<p>00:59</p>", template_data)
            self.assertIn("<p>Two event</p>", template_data)

            french_template_headline_data = render_template(
                "french_news_events_list_export_headline.html",
                items=events,
                app=self.app,
            )
            self.assertIn(
                "<h4>Calendrier sportif international du dimanche 21 au lundi 22 avril</h4>",
                french_template_headline_data,
            )

            dutch_template_headline_data = render_template(
                "dutch_news_events_list_export_headline.html",
                items=events,
                app=self.app,
            )
            self.assertIn(
                "<h4>Internationale sportkalender van zondag 21 tot maandag 22 april</h4>",
                dutch_template_headline_data,
            )

    def test_export_tommorow(self):
        with self.app.app_context():
            events = self.events_for_tommorow
            french_data = render_template(
                "french_news_events_tommorrow.html", items=events, app=self.app
            )
            dutch_data = render_template(
                "dutch_news_events_tommorrow.html", items=events, app=self.app
            )
            self.assertIn(
                (
                    "<h2>Voici l’agenda Belga des événements belges et internationaux qui bénéficieront "
                    "d’une couverture de notre part. Les mentions TEXT, PICTURE, VIDEO, AUDIO, INFOGRAPHICS, "
                    "LIVE VIDEO et LIVE BLOG vous précisent si nous couvrons le sujet. La mention ON MERIT "
                    "vous signale que Belga suit le sujet mais ne peut pas encore assurer qu’il donnera lieu "
                    "à une couverture spécifique. La rédaction vous souhaite une bonne journée de travail</h2>"
                ),
                french_data,
            )
            self.assertIn(
                (
                    "<h2>Dit is de Belga-agenda van de Belgische en internationale gebeurtenissen, "
                    "met de vermelding of wij dit in TEXT, PICTURE, VIDEO, AUDIO, INFOGRAPHICS, LIVE "
                    "VIDEO en LIVE BLOG coveren. De vermelding ON MERIT betekent dat Belga dit onderwerp "
                    "opvolgt, maar dat voorlopig niet gegarandeerd kan worden dat er ook een specifieke "
                    "coverage zal volgen. De redactie van Belga wenst u een prettige werkdag.</h2>"
                ),
                dutch_data,
            )
            self.assertIn("<h3>General</h3>", dutch_data)
            self.assertIn("<p>00:00 - 23:59</p>", dutch_data)
            self.assertIn("<p>another one</p>", dutch_data)
            self.assertIn("<p>Description of event</p>", dutch_data)
            self.assertIn(
                "<p><a href='www.google.xom/new'>www.google.xom/new</a></p>",
                dutch_data,
            )
            self.assertIn(
                "<p>FUBAR - John Doe - Media Contact - jdoe@fubar.com - 99999999 - 666 - fubar.com</p>",
                dutch_data,
            )
            self.assertIn(
                (
                    "<p>FUBAR - Billiam Doe - Associate Consultant - "
                    "funkbio@fubar.com - 99999999 - 666 - funkbar.com</p>"
                ),
                dutch_data,
            )
            self.assertIn("<p>PICTURE (PLANNED)</p>", dutch_data)

            self.assertIn("<h3>Economy</h3>", dutch_data)
            self.assertIn("<p>16:00 - 21:00</p>", dutch_data)
            self.assertIn(
                "<p>City of New York, New York, United States</p>",
                dutch_data,
            )
            self.assertIn("another two</p>", dutch_data)
            self.assertIn("<p>Description of event</p>", dutch_data)
            self.assertIn(
                "<p><a href='www.google.xom/new'>www.google.xom/new</a></p>",
                dutch_data,
            )
            self.assertIn(
                "<p>FUBAR - John Doe - Media Contact - jdoe@fubar.com - 99999999 - 666 - fubar.com</p>",
                dutch_data,
            )
            self.assertIn(
                (
                    "<p>FUBAR - Billiam Doe - Associate Consultant "
                    "- funkbio@fubar.com - 99999999 - 666 - funkbar.com</p>"
                ),
                dutch_data,
            )
            self.assertIn("<p>PICTURE (PLANNED)</p>", dutch_data)

            self.assertIn("<h3>Sports</h3>", dutch_data)
            self.assertIn("<p>00:00 - 23:59</p>", dutch_data)
            self.assertIn("<p>NExxxxt Sunday 21.04.2024</p>", dutch_data)
            self.assertIn("<p>Description of event</p>", dutch_data)
            self.assertIn(
                "<p><a href='www.google.xom/new'>www.google.xom/new</a></p>",
                dutch_data,
            )
            self.assertIn(
                "<p>FUBAR - John Doe - Media Contact - jdoe@fubar.com - 99999999 - 666 - fubar.com</p>",
                dutch_data,
            )
            self.assertIn(
                (
                    "<p>FUBAR - Billiam Doe - Associate Consultant - "
                    "funkbio@fubar.com - 99999999 - 666 - funkbar.com</p>"
                ),
                dutch_data,
            )
            self.assertIn("<p>PICTURE (PLANNED)</p>", dutch_data)

            self.assertNotIn("<h3>Business</h3>", dutch_data)

            self.assertIn(
                "<p>Москва, Moscow, Russia</p>",
                dutch_data,
            )
            self.assertIn(
                "<p>Oud Gerechtshof, Havermarkt 10, 3500 Hasselt, Belgium</p>",
                dutch_data,
            )

    def test_planning_advisory_export_tomorrow(self):
        with self.app.app_context():
            self.app.data.insert("events", self.events_for_tommorow)

            # Insert plannings linked to those events
            planning_items = []
            for ev in self.events_for_tommorow:
                planning_items.append(
                    {
                        "_id": ObjectId(),
                        "type": "planning",
                        "slugline": f"planning for {ev['name']}",
                        "description_text": "planning desc",
                        "dates": ev["dates"],
                        "location": ev.get(
                            "location", {"name": "Unknown", "country": ""}
                        ),
                        "links": ev.get("links", []),
                        "coverages": [
                            {
                                "planning": {"g2_content_type": "picture"},
                                "news_coverage_status": {"label": "Planned"},
                            }
                        ],
                        "event_item": ev.get("_id") or str(ObjectId()),
                        "event_contact_info": ev.get("event_contact_info", []),
                        "language": "en",
                    }
                )
            self.app.data.insert("planning", planning_items)

            dutch_data = render_template(
                "archived/dutch_planning_advisory_tomorrow.html",
                items=planning_items,
                app=self.app,
            )
            french_data = render_template(
                "archived/french_planning_advisory_tomorrow.html",
                items=planning_items,
                app=self.app,
            )

            self.assertIn(
                (
                    "<h2>Voici l’agenda Belga des événements belges et internationaux qui bénéficieront "
                    "d’une couverture de notre part. Les mentions TEXT, PICTURE, VIDEO, AUDIO, INFOGRAPHICS, "
                    "LIVE VIDEO et LIVE BLOG vous précisent si nous couvrons le sujet. La mention ON MERIT "
                    "vous signale que Belga suit le sujet mais ne peut pas encore assurer qu’il donnera lieu "
                    "à une couverture spécifique. La rédaction vous souhaite une bonne journée de travail</h2>"
                ),
                french_data,
            )
            self.assertIn(
                (
                    "<h2>Dit is de Belga-agenda van de Belgische en internationale gebeurtenissen, "
                    "met de vermelding of wij dit in TEXT, PICTURE, VIDEO, AUDIO, INFOGRAPHICS, LIVE "
                    "VIDEO en LIVE BLOG coveren. De vermelding ON MERIT betekent dat Belga dit onderwerp "
                    "opvolgt, maar dat voorlopig niet gegarandeerd kan worden dat er ook een specifieke "
                    "coverage zal volgen. De redactie van Belga wenst u een prettige werkdag.</h2>"
                ),
                dutch_data,
            )

            self.assertIn("<h3>General</h3>", dutch_data)
            self.assertIn("<h3>Sports</h3>", dutch_data)
            self.assertIn("<h3>Economy</h3>", dutch_data)
            self.assertIn("<h3>General</h3>", french_data)
            self.assertIn("<h3>Sports</h3>", french_data)
            self.assertIn("<h3>Economy</h3>", french_data)

            general_section = dutch_data[dutch_data.index("<h3>General</h3>") :]
            self.assertIn("<p>another one</p>", general_section)
            self.assertIn("Moscow", general_section)

            sports_section = dutch_data[dutch_data.index("<h3>Sports</h3>") :]
            self.assertIn("<p>NExxxxt Sunday 21.04.2024</p>", sports_section)
            self.assertIn("New York", sports_section)

            economy_section = dutch_data[dutch_data.index("<h3>Economy</h3>") :]
            self.assertIn("<p>another two</p>", economy_section)
            self.assertIn("Belgium", economy_section)

            self.assertIn(
                "FUBAR - Billiam Doe - Associate Consultant - "
                "funkbio@fubar.com - 99999999 - 666 - funkbar.com",
                dutch_data,
            )

    def test_bilingual_planning_advisory_export_tomorrow(self):
        """Test the bilingual planning advisory template using only planning data"""
        with self.app.app_context():
            test_contact_id = ObjectId()
            test_contact = {
                "_id": test_contact_id,
                "first_name": "John",
                "last_name": "Doe",
                "organisation": "Test Org",
                "job_title": "Media Contact",
                "contact_email": ["jdoe@test.org"],
                "contact_phone": [{"number": "123456789", "public": True}],
                "mobile": [{"number": "987654321", "public": True}],
                "website": "test.org",
            }
            self.app.data.insert("contacts", [test_contact])
            desk_nl = ObjectId()
            desk_fr = ObjectId()

            test_desks = [
                {"_id": desk_nl, "desk_language": "nl", "name": "Test Desk NL"},
                {"_id": desk_fr, "desk_language": "fr", "name": "Test Desk FR"},
            ]
            self.app.data.remove(
                "desks", {"name": {"$in": ["Test Desk NL", "Test Desk FR"]}}
            )
            self.app.data.insert("desks", test_desks)

            # Planning items
            planning_1_id = ObjectId()
            planning_2_id = ObjectId()
            planning_3_id = ObjectId()

            planning_items = [
                {
                    "_id": planning_1_id,
                    "type": "planning",
                    "slugline": "planning-dutch-text",
                    "name": "Test Event NL",
                    "description_text": "Dutch description of the event",
                    "coverages": [
                        {
                            "coverage_id": "cov1",
                            "planning": {"g2_content_type": "text", "desk": desk_nl},
                            "news_coverage_status": {"label": "Planned"},
                        }
                    ],
                    "event_item": None,
                },
                {
                    "_id": planning_2_id,
                    "type": "planning",
                    "slugline": "planning-french-text",
                    "name": "Test Event FR",
                    "description_text": "French description of the event",
                    "coverages": [
                        {
                            "coverage_id": "cov1",
                            "planning": {"g2_content_type": "text", "desk": desk_fr},
                            "news_coverage_status": {"label": "On Merit"},
                        }
                    ],
                    "event_item": None,
                },
                {
                    "_id": planning_3_id,
                    "type": "planning",
                    "slugline": "planning-picture",
                    "name": "Picture Event",
                    "description_text": "Picture coverage description",
                    "coverages": [
                        {
                            "coverage_id": "cov2",
                            "planning": {"g2_content_type": "picture"},
                            "news_coverage_status": {"label": "Planned"},
                        }
                    ],
                    "event_item": None,
                },
            ]

            self.app.data.insert("planning", planning_items)

            bilingual_data = render_template(
                "bilingual_planning_advisory_tomorrow.html",
                items=planning_items,
                app=self.app,
            )

            self.assertIn(
                "<p>Test Event NL</p>", bilingual_data, "Dutch title should be present"
            )
            self.assertIn(
                "<p>Test Event FR</p>", bilingual_data, "French title should be present"
            )
            self.assertIn(
                "<p>Dutch description of the event</p>",
                bilingual_data,
                "Dutch description should be present",
            )
            self.assertIn(
                "<p>French description of the event</p>",
                bilingual_data,
                "French description should be present",
            )
            self.assertIn(
                "<p>BELGA TEXT N (PLANNED)</p>",
                bilingual_data,
                "Dutch text coverage should be tagged as TEXT N",
            )
            self.assertIn(
                "<p>BELGA TEXT F (ON MERIT)</p>",
                bilingual_data,
                "French text coverage should be tagged as TEXT F",
            )
            self.assertIn(
                "<p>BELGA PICTURE (PLANNED)</p>",
                bilingual_data,
                "Picture coverage should not have language tag",
            )

            self.assertIn(
                "<p>BELGA TEXT N (PLANNED)</p>",
                bilingual_data,
                "Dutch text coverage should be tagged as TEXT N",
            )
            self.assertIn(
                "<p>BELGA TEXT F (ON MERIT)</p>",
                bilingual_data,
                "French text coverage should be tagged as TEXT F",
            )
            self.assertIn(
                "<p>BELGA PICTURE (PLANNED)</p>",
                bilingual_data,
                "Picture coverage should not have language tag",
            )

    def test_bilingual_events_advisory_export_tomorrow(self):
        """Test the bilingual events advisory template with various scenarios"""
        with self.app.app_context():
            test_contact_id = ObjectId()
            test_contact = {
                "_id": test_contact_id,
                "first_name": "John",
                "last_name": "Doe",
                "organisation": "Test Org",
                "job_title": "Media Contact",
                "contact_email": ["jdoe@test.org"],
                "contact_phone": [{"number": "123456789", "public": True}],
                "mobile": [{"number": "987654321", "public": True}],
                "website": "test.org",
            }
            self.app.data.insert("contacts", [test_contact])
            desk_nl = ObjectId()
            desk_fr = ObjectId()
            test_desks = [
                {"_id": desk_nl, "desk_language": "nl", "name": "Test Desk NL"},
                {"_id": desk_fr, "desk_language": "fr", "name": "Test Desk FR"},
            ]
            self.app.data.remove(
                "desks", {"name": {"$in": ["Test Desk NL", "Test Desk FR"]}}
            )
            self.app.data.insert("desks", test_desks)

            event_1_id = ObjectId()
            event_2_id = ObjectId()
            event_3_id = ObjectId()

            bilingual_events = [
                {
                    "_id": event_1_id,
                    "name": "Test Event NL",
                    "slugline": "test-event-nl",
                    "definition_long": "Dutch description of the event",
                    "dates": {
                        "start": datetime.datetime(
                            2024, 4, 22, 9, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                        "end": datetime.datetime(
                            2024, 4, 22, 17, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                        "tz": "Europe/Brussels",
                    },
                    "calendars": [{"qcode": "general", "name": "General"}],
                    "location": [
                        {
                            "name": "Brussels",
                            "address": {"city": "Brussels", "country": "Belgium"},
                        }
                    ],
                    "links": ["http://test-event.com"],
                    "event_contact_info": [str(test_contact_id)],
                    "translations": [
                        {"field": "name", "language": "fr", "value": "Test Event FR"},
                        {
                            "field": "definition_long",
                            "language": "fr",
                            "value": "French description of the event",
                        },
                    ],
                },
                {
                    "_id": event_2_id,
                    "name": "All Day Event NL",
                    "slugline": "all-day-event",
                    "definition_long": "This is an all-day event in Dutch",
                    "dates": {
                        "start": datetime.datetime(
                            2024, 4, 22, 0, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                        "end": datetime.datetime(
                            2024, 4, 22, 23, 59, 59, tzinfo=datetime.timezone.utc
                        ),
                        "tz": "Europe/Brussels",
                    },
                    "calendars": [{"qcode": "politics", "name": "Politics"}],
                    "location": [
                        {
                            "name": "Brussels",
                            "address": {"city": "Brussels", "country": "Belgium"},
                        }
                    ],
                    "links": ["http://allday-event.com"],
                    "event_contact_info": [str(test_contact_id)],
                    "translations": [
                        {
                            "field": "name",
                            "language": "fr",
                            "value": "All Day Event FR",
                        },
                        {
                            "field": "definition_long",
                            "language": "fr",
                            "value": "This is an all-day event in French",
                        },
                    ],
                },
                {
                    "_id": event_3_id,
                    "name": "Single Language Event",
                    "slugline": "single-language",
                    "definition_long": "Event with only one language",
                    "dates": {
                        "start": datetime.datetime(
                            2024, 4, 22, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                        "end": datetime.datetime(
                            2024, 4, 22, 16, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                        "tz": "Europe/Brussels",
                    },
                    "calendars": [{"qcode": "economy", "name": "Economy"}],
                    "location": [
                        {
                            "name": "Antwerp",
                            "address": {"city": "Antwerp", "country": "Belgium"},
                        }
                    ],
                    "links": ["http://single-event.com"],
                    "event_contact_info": [str(test_contact_id)],
                    # No translations - should fall back to default language
                },
            ]

            self.app.data.insert("events", bilingual_events)

            planning_1_id = ObjectId()
            planning_2_id = ObjectId()
            planning_3_id = ObjectId()
            planning_4_id = ObjectId()
            planning_5_id = ObjectId()

            planning_items = [
                {
                    "_id": planning_1_id,
                    "type": "planning",
                    "slugline": "planning-dutch-text",
                    "description_text": "Planning for Dutch text coverage",
                    "dates": bilingual_events[0]["dates"],
                    "coverages": [
                        {
                            "coverage_id": "cov1",
                            "planning": {
                                "g2_content_type": "text",
                                "desk": desk_nl,
                            },
                            "news_coverage_status": {"label": "Planned"},
                        }
                    ],
                    "event_item": event_1_id,
                },
                {
                    "_id": planning_2_id,
                    "type": "planning",
                    "slugline": "planning-french-text",
                    "description_text": "Planning for French text coverage",
                    "dates": bilingual_events[0]["dates"],
                    "coverages": [
                        {
                            "coverage_id": "cov2",
                            "planning": {
                                "g2_content_type": "text",
                                "desk": desk_fr,
                            },
                            "news_coverage_status": {"label": "On Merit"},
                        }
                    ],
                    "event_item": event_1_id,
                },
                {
                    "_id": planning_3_id,
                    "type": "planning",
                    "slugline": "planning-picture",
                    "description_text": "Planning for picture coverage",
                    "dates": bilingual_events[0]["dates"],
                    "coverages": [
                        {
                            "coverage_id": "cov3",
                            "planning": {"g2_content_type": "picture"},
                            "news_coverage_status": {"label": "Planned"},
                        }
                    ],
                    "event_item": event_1_id,
                },
                {
                    "_id": planning_4_id,
                    "type": "planning",
                    "slugline": "planning-all-day-text",
                    "description_text": "Planning for all-day event",
                    "dates": bilingual_events[1]["dates"],
                    "coverages": [
                        {
                            "coverage_id": "cov4",
                            "planning": {
                                "g2_content_type": "text",
                                "desk": desk_nl,
                            },
                            "news_coverage_status": {"label": "Planned"},
                        }
                    ],
                    "event_item": event_2_id,
                },
                {
                    "_id": planning_5_id,
                    "type": "planning",
                    "slugline": "planning-single-event",
                    "description_text": "Planning for single language event",
                    "dates": bilingual_events[2]["dates"],
                    "coverages": [
                        {
                            "coverage_id": "cov5",
                            "planning": {
                                "g2_content_type": "text",
                                "desk": desk_nl,
                            },
                            "news_coverage_status": {"label": "Planned"},
                        },
                        {
                            "coverage_id": "cov6",
                            "planning": {"g2_content_type": "video"},
                            "news_coverage_status": {"label": "On Merit"},
                        },
                    ],
                    "event_item": event_3_id,
                },
            ]

            self.app.data.insert("planning", planning_items)

            self.app.data.update(
                "events",
                event_1_id,
                {"planning_ids": [planning_1_id, planning_2_id, planning_3_id]},
                bilingual_events[0],
            )

            self.app.data.update(
                "events",
                event_2_id,
                {"planning_ids": [planning_4_id]},
                bilingual_events[1],
            )

            self.app.data.update(
                "events",
                event_3_id,
                {"planning_ids": [planning_5_id]},
                bilingual_events[2],
            )

            bilingual_data = render_template(
                "bilingual_news_events_tommorrow.html",
                items=bilingual_events,
                app=self.app,
            )

            self.assertIn(
                "<h2>Dit is de Belga-agenda van de Belgische en internationale gebeurtenissen",
                bilingual_data,
                "Dutch introduction should be present",
            )
            self.assertIn(
                "<h2>Voici l'agenda Belga des événements belges et internationaux",
                bilingual_data,
                "French introduction should be present",
            )

            self.assertIn(
                "<h3>General</h3>",
                bilingual_data,
                "General calendar section should be present",
            )
            self.assertIn(
                "<h3>Politics</h3>",
                bilingual_data,
                "Politics calendar section should be present",
            )
            self.assertIn(
                "<h3>Economy</h3>",
                bilingual_data,
                "Economy calendar section should be present",
            )

            self.assertIn(
                "<p>Test Event NL</p>", bilingual_data, "Dutch title should be present"
            )
            self.assertIn(
                "<p>Test Event FR</p>", bilingual_data, "French title should be present"
            )
            self.assertIn(
                "<p>Dutch description of the event</p>",
                bilingual_data,
                "Dutch description should be present",
            )
            self.assertIn(
                "<p>French description of the event</p>",
                bilingual_data,
                "French description should be present",
            )

            self.assertIn(
                "<p>All Day Event NL</p>",
                bilingual_data,
                "All-day Dutch title should be present",
            )
            self.assertIn(
                "<p>All Day Event FR</p>",
                bilingual_data,
                "All-day French title should be present",
            )
            self.assertNotIn(
                "00:00 - 23:59",
                bilingual_data,
                "All-day events should not show 00:00-23:59 time",
            )

            self.assertIn(
                "11:00 - 19:00",
                bilingual_data,
                "Regular events should show specific time range",
            )
            self.assertIn(
                "16:00 - 18:00",
                bilingual_data,
                "Afternoon events should show correct time range",
            )

            self.assertIn(
                "Test Org - John Doe - Media Contact - jdoe@test.org - 123456789 - 987654321 - test.org",
                bilingual_data,
                "Contact information should be present",
            )

            self.assertIn(
                "Brussels, Belgium",
                bilingual_data,
                "Location information should be present",
            )
            self.assertIn(
                "Antwerp, Belgium",
                bilingual_data,
                "Second location should be present",
            )

            self.assertIn(
                'href="http://test-event.com"',
                bilingual_data,
                "Event links should be present",
            )
            self.assertIn(
                'href="http://allday-event.com"',
                bilingual_data,
                "All-day event links should be present",
            )

            general_index = bilingual_data.find("<h3>General</h3>")
            politics_index = bilingual_data.find("<h3>Politics</h3>")
            economy_index = bilingual_data.find("<h3>Economy</h3>")

            self.assertLess(
                general_index, politics_index, "General should come before Politics"
            )
            self.assertLess(
                politics_index, economy_index, "Politics should come before Economy"
            )

            politics_section = bilingual_data.split("<h3>Politics</h3>")[1].split(
                "<h3>"
            )[0]
            self.assertNotIn(
                "00:00 - 23:59",
                politics_section,
                "All-day event should not show time",
            )

    def test_internal_bilingual_events_advisory_export_tomorrow(self):
        """Test the internal bilingual events advisory template with usernames and full desk names"""
        with self.app.app_context():
            user_nl_id = ObjectId()
            user_fr_id = ObjectId()
            user_picture_id = ObjectId()

            timestamp = str(int(datetime.datetime.now().timestamp()))[-6:]
            test_users = [
                {
                    "_id": user_nl_id,
                    "username": f"reporternl_{timestamp}",
                    "sign_off": "RNL",
                    "display_name": "Reporter NL",
                    "email": f"reporter.nl_{timestamp}@test.com",
                },
                {
                    "_id": user_fr_id,
                    "username": f"reporterfr_{timestamp}",
                    "sign_off": "RFR",
                    "display_name": "Reporter FR",
                    "email": f"reporter.fr_{timestamp}@test.com",
                },
                {
                    "_id": user_picture_id,
                    "username": f"photographer_{timestamp}",
                    "sign_off": "PHOTO",
                    "display_name": "Photographer",
                    "email": f"photo_{timestamp}@test.com",
                },
            ]

            self.app.data.insert("users", test_users)

            desk_nl = ObjectId()
            desk_fr = ObjectId()
            desk_picture = ObjectId()

            test_desks = [
                {
                    "_id": desk_nl,
                    "desk_language": "nl",
                    "name": f"Test Desk NL {timestamp}",
                    "members": [{"user": user_nl_id}],
                },
                {
                    "_id": desk_fr,
                    "desk_language": "fr",
                    "name": f"Test Desk FR {timestamp}",
                    "members": [{"user": user_fr_id}],
                },
                {
                    "_id": desk_picture,
                    "desk_language": "nl",
                    "name": f"Picture Desk {timestamp}",
                    "members": [{"user": user_picture_id}],
                },
            ]
            self.app.data.remove(
                "desks",
                {
                    "name": {
                        "$in": [
                            f"Test Desk NL {timestamp}",
                            f"Test Desk FR {timestamp}",
                            f"Picture Desk {timestamp}",
                        ]
                    }
                },
            )
            self.app.data.insert("desks", test_desks)

            event_1_id = ObjectId()
            event_2_id = ObjectId()

            bilingual_events = [
                {
                    "_id": event_1_id,
                    "name": "Test Event with User Assignment",
                    "slugline": "test-event-users",
                    "definition_long": "Event with user assignments",
                    "dates": {
                        "start": datetime.datetime(
                            2024, 4, 22, 9, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                        "end": datetime.datetime(
                            2024, 4, 22, 17, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                        "tz": "Europe/Brussels",
                    },
                    "calendars": [{"qcode": "general", "name": "General"}],
                    "location": [
                        {
                            "name": "Brussels",
                            "address": {"city": "Brussels", "country": "Belgium"},
                        }
                    ],
                    "translations": [
                        {
                            "field": "name",
                            "language": "fr",
                            "value": "Test Event FR avec utilisateurs",
                        },
                        {
                            "field": "definition_long",
                            "language": "fr",
                            "value": "Événement avec assignation d'utilisateurs",
                        },
                    ],
                },
                {
                    "_id": event_2_id,
                    "name": "Event with Direct User Assignment",
                    "slugline": "direct-user-event",
                    "definition_long": "Event with direct user assignment in coverage",
                    "dates": {
                        "start": datetime.datetime(
                            2024, 4, 22, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                        "end": datetime.datetime(
                            2024, 4, 22, 16, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                        "tz": "Europe/Brussels",
                    },
                    "calendars": [{"qcode": "politics", "name": "Politics"}],
                    "location": [
                        {
                            "name": "Brussels",
                            "address": {"city": "Brussels", "country": "Belgium"},
                        }
                    ],
                    "translations": [
                        {
                            "field": "name",
                            "language": "fr",
                            "value": "Événement avec assignation directe",
                        },
                    ],
                },
            ]

            self.app.data.insert("events", bilingual_events)

            planning_1_id = ObjectId()
            planning_2_id = ObjectId()
            planning_3_id = ObjectId()
            planning_4_id = ObjectId()

            planning_items = [
                {
                    "_id": planning_1_id,
                    "type": "planning",
                    "slugline": "planning-desk-nl",
                    "coverages": [
                        {
                            "coverage_id": "cov1",
                            "planning": {"g2_content_type": "text", "desk": desk_nl},
                            "news_coverage_status": {"label": "Planned"},
                        }
                    ],
                    "event_item": event_1_id,
                },
                {
                    "_id": planning_2_id,
                    "type": "planning",
                    "slugline": "planning-desk-fr",
                    "coverages": [
                        {
                            "coverage_id": "cov2",
                            "planning": {"g2_content_type": "text", "desk": desk_fr},
                            "news_coverage_status": {"label": "On Merit"},
                        }
                    ],
                    "event_item": event_1_id,
                },
                {
                    "_id": planning_3_id,
                    "type": "planning",
                    "slugline": "planning-picture-desk",
                    "coverages": [
                        {
                            "coverage_id": "cov3",
                            "planning": {
                                "g2_content_type": "picture",
                                "desk": desk_picture,
                            },
                            "news_coverage_status": {"label": "Planned"},
                        }
                    ],
                    "event_item": event_1_id,
                },
                {
                    "_id": planning_4_id,
                    "type": "planning",
                    "slugline": "planning-direct-user",
                    "coverages": [
                        {
                            "coverage_id": "cov4",
                            "planning": {"g2_content_type": "text", "desk": desk_nl},
                            "assigned_to": {"user": user_nl_id},
                            "news_coverage_status": {"label": "Planned"},
                        },
                        {
                            "coverage_id": "cov5",
                            "planning": {"g2_content_type": "video"},
                            "assigned_to": {"user": user_picture_id},
                            "news_coverage_status": {"label": "On Merit"},
                        },
                    ],
                    "event_item": event_2_id,
                },
            ]

            self.app.data.insert("planning", planning_items)

            bilingual_events[0]["planning_ids"] = [
                planning_1_id,
                planning_2_id,
                planning_3_id,
            ]
            bilingual_events[1]["planning_ids"] = [planning_4_id]

            internal_data = render_template(
                "internal_bilingual_news_events_tomorrow.html",
                items=bilingual_events,
                app=self.app,
            )

            self.assertIn(
                f"<p>BELGA TEXT N (PLANNED) BY TEST DESK NL {timestamp}</p>",
                internal_data,
                "Dutch text coverage should show full desk name in UPPERCASE when no direct user",
            )
            self.assertIn(
                f"<p>BELGA TEXT F (ON MERIT) BY TEST DESK FR {timestamp}</p>",
                internal_data,
                "French text coverage should show full desk name in UPPERCASE when no direct user",
            )
            self.assertIn(
                f"<p>BELGA PICTURE (PLANNED) BY PICTURE DESK {timestamp}</p>",
                internal_data,
                "Picture coverage should show full desk name in UPPERCASE when no direct user",
            )
            self.assertIn(
                "<p>BELGA TEXT N (PLANNED) BY RNL</p>",
                internal_data,
                "Direct user assignment should show username",
            )
            self.assertIn(
                "<p>BELGA VIDEO (ON MERIT) BY PHOTO</p>",
                internal_data,
                "Video coverage with direct user assignment should show username",
            )

            self.assertIn(
                "<h2>Dit is de Belga-agenda van de Belgische en internationale gebeurtenissen",
                internal_data,
                "Dutch introduction should be present",
            )
            self.assertIn(
                "<h2>Voici l'agenda Belga des événements belges et internationaux",
                internal_data,
                "French introduction should be present",
            )

    def test_internal_bilingual_planning_advisory_export_tomorrow(self):
        """Test the internal bilingual planning advisory template with usernames and desk names"""
        with self.app.app_context():
            user_nl_id = ObjectId()
            user_fr_id = ObjectId()
            user_video_id = ObjectId()

            timestamp = str(int(datetime.datetime.now().timestamp()))[-6:]
            test_users = [
                {
                    "_id": user_nl_id,
                    "username": f"plannernl_{timestamp}",
                    "sign_off": "PNL",
                    "display_name": "Planner NL",
                    "email": f"planner.nl_{timestamp}@test.com",
                },
                {
                    "_id": user_fr_id,
                    "username": f"plannerfr_{timestamp}",
                    "sign_off": "PFR",
                    "display_name": "Planner FR",
                    "email": f"planner.fr_{timestamp}@test.com",
                },
                {
                    "_id": user_video_id,
                    "username": f"videographer_{timestamp}",
                    "sign_off": "VIDEO",
                    "display_name": "Videographer",
                    "email": f"video_{timestamp}@test.com",
                },
            ]

            self.app.data.insert("users", test_users)

            desk_nl = ObjectId()
            desk_fr = ObjectId()
            desk_video = ObjectId()

            test_desks = [
                {
                    "_id": desk_nl,
                    "desk_language": "nl",
                    "name": f"Planning Desk NL {timestamp}",
                    "members": [{"user": user_nl_id}],
                },
                {
                    "_id": desk_fr,
                    "desk_language": "fr",
                    "name": f"Planning Desk FR {timestamp}",
                    "members": [{"user": user_fr_id}],
                },
                {
                    "_id": desk_video,
                    "desk_language": "nl",
                    "name": f"Video Desk {timestamp}",
                    "members": [{"user": user_video_id}],
                },
            ]
            self.app.data.remove(
                "desks",
                {
                    "name": {
                        "$in": [
                            f"Planning Desk NL {timestamp}",
                            f"Planning Desk FR {timestamp}",
                            f"Video Desk {timestamp}",
                        ]
                    }
                },
            )
            self.app.data.insert("desks", test_desks)

            planning_1_id = ObjectId()
            planning_2_id = ObjectId()
            planning_3_id = ObjectId()

            planning_items = [
                {
                    "_id": planning_1_id,
                    "type": "planning",
                    "slugline": "internal-planning-nl",
                    "name": "Internal Planning NL",
                    "description_text": "Dutch planning with user assignments",
                    "coverages": [
                        {
                            "coverage_id": "cov1",
                            "planning": {"g2_content_type": "text", "desk": desk_nl},
                            "news_coverage_status": {"label": "Planned"},
                        },
                        {
                            "coverage_id": "cov2",
                            "planning": {"g2_content_type": "text", "desk": desk_fr},
                            "news_coverage_status": {"label": "On Merit"},
                        },
                    ],
                    "event_item": None,
                },
                {
                    "_id": planning_2_id,
                    "type": "planning",
                    "slugline": "internal-planning-mixed",
                    "name": "Internal Planning Mixed",
                    "description_text": "Planning with mixed coverage types",
                    "coverages": [
                        {
                            "coverage_id": "cov3",
                            "planning": {"g2_content_type": "picture", "desk": desk_nl},
                            "news_coverage_status": {"label": "Planned"},
                        },
                        {
                            "coverage_id": "cov4",
                            "planning": {
                                "g2_content_type": "video",
                                "desk": desk_video,
                            },
                            "assigned_to": {"user": user_video_id},
                            "news_coverage_status": {"label": "Planned"},
                        },
                    ],
                    "event_item": None,
                },
                {
                    "_id": planning_3_id,
                    "type": "planning",
                    "slugline": "internal-planning-fr",
                    "name": "Internal Planning FR",
                    "description_text": "French planning with direct user assignment",
                    "coverages": [
                        {
                            "coverage_id": "cov5",
                            "planning": {"g2_content_type": "text", "desk": desk_fr},
                            "assigned_to": {"user": user_fr_id},
                            "news_coverage_status": {"label": "On Merit"},
                        }
                    ],
                    "event_item": None,
                },
            ]

            self.app.data.insert("planning", planning_items)

            internal_data = render_template(
                "internal_bilingual_planning_advisory_tomorrow.html",
                items=planning_items,
                app=self.app,
            )

            self.assertIn(
                f"<p>BELGA TEXT N (PLANNED) BY PLANNING DESK NL {timestamp}</p>",
                internal_data,
                "Dutch text coverage should show full desk name in UPPERCASE when no direct user",
            )
            self.assertIn(
                f"<p>BELGA TEXT F (ON MERIT) BY PLANNING DESK FR {timestamp}</p>",
                internal_data,
                "French text coverage should show full desk name in UPPERCASE when no direct user",
            )
            self.assertIn(
                f"<p>BELGA PICTURE (PLANNED) BY PLANNING DESK NL {timestamp}</p>",
                internal_data,
                "Picture coverage should show full desk name in UPPERCASE when no direct user",
            )
            self.assertIn(
                "<p>BELGA VIDEO (PLANNED) BY VIDEO</p>",
                internal_data,
                "Video coverage with direct user assignment should show username",
            )
            self.assertIn(
                "<p>BELGA TEXT F (ON MERIT) BY PFR</p>",
                internal_data,
                "French text with direct user assignment should show username",
            )

            self.assertIn(
                "<p>Internal Planning NL</p>",
                internal_data,
                "Dutch planning title should be present",
            )
            self.assertIn(
                "<p>Internal Planning FR</p>",
                internal_data,
                "French planning title should be present",
            )

    def test_bilingual_events_header_uses_earliest_date_no_leading_zero(self):
        """
        - Events-only advisory header must use the earliest local date
        - Day should be rendered without leading zero (e.g. 5, not 05)
        """
        with self.app.app_context():
            events = [
                {
                    "_id": ObjectId(),
                    "name": "Later event",
                    "dates": {
                        "start": datetime.datetime(
                            2025, 11, 6, 10, 0, tzinfo=datetime.timezone.utc
                        ),
                        "end": datetime.datetime(
                            2025, 11, 6, 11, 0, tzinfo=datetime.timezone.utc
                        ),
                        "tz": "Europe/Brussels",
                    },
                    "calendars": [{"qcode": "general", "name": "General"}],
                    "location": [],
                    "links": [],
                    "event_contact_info": [],
                },
                {
                    "_id": ObjectId(),
                    "name": "Earlier event",
                    "dates": {
                        "start": datetime.datetime(
                            2025, 11, 5, 9, 0, tzinfo=datetime.timezone.utc
                        ),
                        "end": datetime.datetime(
                            2025, 11, 5, 10, 0, tzinfo=datetime.timezone.utc
                        ),
                        "tz": "Europe/Brussels",
                    },
                    "calendars": [{"qcode": "general", "name": "General"}],
                    "location": [],
                    "links": [],
                    "event_contact_info": [],
                },
            ]

            formatted = format_event_for_tommorow_bilingual(events, locale="nl")

            self.assertEqual(
                "WEDNESDAY 5 NOVEMBER 2025",
                formatted["weekday_date"],
                "Header date should use earliest local event date without leading zero",
            )

    def test_internal_bilingual_events_header_uses_earliest_date_no_leading_zero(self):
        """
        - Internal events-only advisory header must also use earliest local date
        - Day should be rendered without leading zero
        """
        with self.app.app_context():
            events = [
                {
                    "_id": ObjectId(),
                    "name": "Later event (internal)",
                    "dates": {
                        "start": datetime.datetime(
                            2025, 11, 6, 10, 0, tzinfo=datetime.timezone.utc
                        ),
                        "end": datetime.datetime(
                            2025, 11, 6, 11, 0, tzinfo=datetime.timezone.utc
                        ),
                        "tz": "Europe/Brussels",
                    },
                    "calendars": [{"qcode": "general", "name": "General"}],
                    "location": [],
                    "links": [],
                    "event_contact_info": [],
                },
                {
                    "_id": ObjectId(),
                    "name": "Earlier event (internal)",
                    "dates": {
                        "start": datetime.datetime(
                            2025, 11, 5, 9, 0, tzinfo=datetime.timezone.utc
                        ),
                        "end": datetime.datetime(
                            2025, 11, 5, 10, 0, tzinfo=datetime.timezone.utc
                        ),
                        "tz": "Europe/Brussels",
                    },
                    "calendars": [{"qcode": "general", "name": "General"}],
                    "location": [],
                    "links": [],
                    "event_contact_info": [],
                },
            ]

            formatted = format_event_for_tommorow_bilingual_internal(
                events, locale="nl"
            )

            self.assertEqual(
                "WEDNESDAY 5 NOVEMBER 2025",
                formatted["weekday_date"],
                "Internal header date should use earliest local event date without leading zero",
            )

    def test_internal_bilingual_planning_uses_french_translation_and_header_date(self):
        """
        - Planning-only internal advisory should:
          * Use French translations for the title (so FR name is not missing)
          * Render header date without leading zero, based on scheduled date
        """
        with self.app.app_context():
            planning_id = ObjectId()
            scheduled = datetime.datetime(
                2025, 11, 5, 10, 0, tzinfo=datetime.timezone.utc
            )

            planning_item = {
                "_id": planning_id,
                "type": "planning",
                "name": "Base EN name",
                "description_text": "Base EN description",
                "translations": [
                    {"field": "name", "language": "nl", "value": "Naam NL"},
                    {"field": "name", "language": "fr", "value": "Nom FR"},
                    {
                        "field": "description_text",
                        "language": "nl",
                        "value": "Beschrijving NL",
                    },
                    {
                        "field": "description_text",
                        "language": "fr",
                        "value": "Description FR",
                    },
                ],
                "coverages": [
                    {
                        "coverage_id": "cov1",
                        "planning": {
                            "g2_content_type": "text",
                            "scheduled": scheduled,
                        },
                        "news_coverage_status": {"label": "Planned"},
                    }
                ],
                "event_item": None,
            }

            self.app.data.insert("planning", [planning_item])

            formatted = format_planning_for_tomorrow_bilingual_internal([planning_item])

            self.assertEqual(
                "WEDNESDAY 5 NOVEMBER 2025",
                formatted["weekday_date"],
                "Planning advisory header date should not have leading zero",
            )

            self.assertEqual(1, len(formatted["events"]))
            events_for_calendar = formatted["events"][0]["events"]
            self.assertEqual(1, len(events_for_calendar))

            item = events_for_calendar[0]

            self.assertEqual(
                "Nom FR",
                item["title_fr"],
                "French title should come from FR translation (not be missing)",
            )
            self.assertEqual(
                "Description FR",
                item["description_fr"],
                "French description should come from FR translation",
            )

            self.assertEqual(
                "Beschrijving NL",
                item["description_nl"],
                "Dutch description should come from NL translation",
            )

    def test_advisory_hides_all_day_no_time_and_shows_belga_prefix(self):
        """introduction text, BELGA prefix and hide 00:00 timestamps for all-day/no-time events"""
        with self.app.app_context():
            from superdesk.utc import utc_to_local

            contact_id = ObjectId()
            contact = {
                "_id": contact_id,
                "first_name": "Jane",
                "last_name": "Reporter",
                "organisation": "BELGA",
                "job_title": "Journalist",
                "contact_email": ["jane@belga.test"],
                "contact_phone": [{"number": "111222333", "public": True}],
                "mobile": [{"number": "444555666", "public": True}],
                "website": "belga.test",
            }
            self.app.data.insert("contacts", [contact])

            all_day_start = datetime.datetime(
                2025, 1, 9, 23, 0, tzinfo=datetime.timezone.utc
            )
            all_day_end = datetime.datetime(
                2025, 1, 10, 22, 59, 59, tzinfo=datetime.timezone.utc
            )
            all_day_event = {
                "_id": ObjectId(),
                "name": "All Day Festival",
                "definition_long": "All day long",
                "dates": {
                    "start": all_day_start,
                    "end": all_day_end,
                    "tz": "Europe/Brussels",
                },
                "calendars": [{"qcode": "general"}],
                "location": [
                    {
                        "name": "Brussels",
                        "address": {"city": "Brussels", "country": "Belgium"},
                    }
                ],
                "event_contact_info": [str(contact_id)],
                "planning_ids": [],
            }

            timed_start = datetime.datetime(
                2025, 1, 10, 14, 0, tzinfo=datetime.timezone.utc
            )
            timed_end = datetime.datetime(
                2025, 1, 10, 16, 0, tzinfo=datetime.timezone.utc
            )
            timed_event = {
                "_id": ObjectId(),
                "name": "Timed Briefing",
                "definition_long": "Happens in the afternoon",
                "dates": {
                    "start": timed_start,
                    "end": timed_end,
                    "tz": "Europe/Brussels",
                },
                "calendars": [{"qcode": "general"}],
                "location": [
                    {
                        "name": "Brussels",
                        "address": {"city": "Brussels", "country": "Belgium"},
                    }
                ],
                "event_contact_info": [str(contact_id)],
                "planning_ids": [],
            }

            self.app.data.insert("events", [all_day_event, timed_event])

            events_html = render_template(
                "bilingual_news_events_tommorrow.html",
                items=[all_day_event, timed_event],
                app=self.app,
            )

            self.assertIn("BELGA TEXT N", events_html)

            self.assertNotIn("00:00 - 23:59", events_html)

            start_local = utc_to_local("Europe/Brussels", timed_start)
            end_local = utc_to_local("Europe/Brussels", timed_end)
            expected_range = (
                f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')}"
            )
            self.assertIn(expected_range, events_html)

    def test_bilingual_events_excludes_editorial_calendar(self):
        """Events with Editorial calendar must be excluded"""
        with self.app.app_context():
            editorial_event = {
                "_id": ObjectId(),
                "name": "Editorial Event",
                "definition_long": "Should never appear",
                "dates": {
                    "start": datetime.datetime(
                        2025, 1, 10, 10, 0, tzinfo=datetime.timezone.utc
                    ),
                    "end": datetime.datetime(
                        2025, 1, 10, 12, 0, tzinfo=datetime.timezone.utc
                    ),
                    "tz": "Europe/Brussels",
                },
                "calendars": [
                    {"qcode": "Editorial", "name": "(I) Editorial"},
                    {"qcode": "Justice", "name": "(5) Justice"},
                ],
                "location": [],
                "links": [],
                "event_contact_info": [],
            }

            normal_event = {
                "_id": ObjectId(),
                "name": "Public Event",
                "definition_long": "Should appear",
                "dates": {
                    "start": datetime.datetime(
                        2025, 1, 10, 14, 0, tzinfo=datetime.timezone.utc
                    ),
                    "end": datetime.datetime(
                        2025, 1, 10, 16, 0, tzinfo=datetime.timezone.utc
                    ),
                    "tz": "Europe/Brussels",
                },
                "calendars": [{"qcode": "General", "name": "(1) General"}],
                "location": [],
                "links": [],
                "event_contact_info": [],
            }

            html = render_template(
                "bilingual_news_events_tommorrow.html",
                items=[editorial_event, normal_event],
                app=self.app,
            )

            self.assertNotIn("Editorial Event", html)
            self.assertIn("Public Event", html)

    def test_bilingual_planning_excludes_editorial_event_link(self):
        """Planning linked to Editorial events must be excluded"""
        with self.app.app_context():
            editorial_event_id = ObjectId()
            public_event_id = ObjectId()

            self.app.data.insert(
                "events",
                [
                    {
                        "_id": editorial_event_id,
                        "name": "Editorial Event",
                        "dates": {
                            "start": datetime.datetime(
                                2025, 1, 10, 10, 0, tzinfo=datetime.timezone.utc
                            ),
                            "end": datetime.datetime(
                                2025, 1, 10, 12, 0, tzinfo=datetime.timezone.utc
                            ),
                            "tz": "Europe/Brussels",
                        },
                        "calendars": [{"qcode": "Editorial", "name": "(I) Editorial"}],
                    },
                    {
                        "_id": public_event_id,
                        "name": "Public Event",
                        "dates": {
                            "start": datetime.datetime(
                                2025, 1, 10, 14, 0, tzinfo=datetime.timezone.utc
                            ),
                            "end": datetime.datetime(
                                2025, 1, 10, 16, 0, tzinfo=datetime.timezone.utc
                            ),
                            "tz": "Europe/Brussels",
                        },
                        "calendars": [{"qcode": "General", "name": "(1) General"}],
                    },
                ],
            )

            planning_items = [
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "name": "Planning Editorial",
                    "description_text": "Should not appear",
                    "coverages": [
                        {
                            "coverage_id": "cov-editorial-1",
                            "planning": {"g2_content_type": "text"},
                            "news_coverage_status": {"label": "Planned"},
                        }
                    ],
                    "event_item": editorial_event_id,
                },
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "name": "Planning Public",
                    "description_text": "Should appear",
                    "coverages": [
                        {
                            "coverage_id": "cov-public-1",
                            "planning": {"g2_content_type": "text"},
                            "news_coverage_status": {"label": "Planned"},
                        }
                    ],
                    "event_item": public_event_id,
                },
            ]

            self.app.data.insert("planning", planning_items)

            html = render_template(
                "bilingual_planning_advisory_tomorrow.html",
                items=planning_items,
                app=self.app,
            )

            self.assertNotIn("Planning Editorial", html)
            self.assertNotIn("Editorial Event", html)
            self.assertIn("Public Event", html)

    def test_belga_image_photo_planning_renders_picture_only(self):
        """Belga Image Photo Planning renders picture coverage and excludes text/video."""
        with self.app.app_context():
            event_id = ObjectId()
            planning_id = ObjectId()
            user_id = ObjectId()

            user = {
                "_id": user_id,
                "username": f"testuser_photo_{user_id}",
                "sign_off": "TST",
            }
            self.app.data.insert("users", [user])

            event = {
                "_id": event_id,
                "name": "Sports Photo Event",
                "dates": {
                    "start": datetime.datetime(
                        2026, 1, 9, 9, 0, tzinfo=datetime.timezone.utc
                    ),
                    "end": datetime.datetime(
                        2026, 1, 9, 18, 0, tzinfo=datetime.timezone.utc
                    ),
                    "tz": "Europe/Brussels",
                },
                "calendars": [{"qcode": "Sports", "name": "(7) Sports"}],
            }

            planning = {
                "_id": planning_id,
                "type": "planning",
                "planning_date": datetime.datetime(
                    2026, 1, 9, 9, 0, tzinfo=datetime.timezone.utc
                ),
                "name": "Sports Photo Event",
                "description_text": "Planning description",
                "coverages": [
                    {
                        "coverage_id": ObjectId(),
                        "planning": {"g2_content_type": "text"},
                    },
                    {
                        "coverage_id": ObjectId(),
                        "planning": {"g2_content_type": "picture"},
                        "news_coverage_status": {"label": "Planned"},
                        "assigned_to": {"user": user_id},
                    },
                    {
                        "coverage_id": ObjectId(),
                        "planning": {"g2_content_type": "video"},
                    },
                ],
                "event_item": event_id,
            }

            self.app.data.insert("events", [event])
            self.app.data.insert("planning", [planning])

            self.app.data.update(
                "events",
                event_id,
                {"planning_ids": [planning_id]},
                event,
            )

            html = render_template(
                "internal_image_photo_planning.html",
                items=[planning],
                app=self.app,
            )

            self.assertIn("<h1>Belga Image Photo Planning", html)
            self.assertIn("<b>Sports Photo Event</b>", html)
            self.assertNotIn("TEXT", html)
            self.assertNotIn("VIDEO", html)
            self.assertNotIn("BELGA PICTURE", html)
            self.assertIn(user["sign_off"], html)
            self.assertNotIn(planning["description_text"], html)

    def test_belga_image_video_planning_renders_video_only(self):
        """Belga Image Video Planning renders video coverage and excludes picture/text."""
        with self.app.app_context():
            event_id = ObjectId()
            planning_id = ObjectId()
            user_id = ObjectId()

            user = {
                "_id": user_id,
                "username": f"testuser_video_{user_id}",
                "sign_off": "TST",
            }
            self.app.data.insert("users", [user])

            event = {
                "_id": event_id,
                "name": "Video Event",
                "dates": {
                    "start": datetime.datetime(
                        2026, 1, 10, 14, 0, tzinfo=datetime.timezone.utc
                    ),
                    "end": datetime.datetime(
                        2026, 1, 10, 16, 0, tzinfo=datetime.timezone.utc
                    ),
                    "tz": "Europe/Brussels",
                },
                "calendars": [{"qcode": "General", "name": "(1) General"}],
            }

            planning = {
                "_id": planning_id,
                "type": "planning",
                "planning_date": datetime.datetime(
                    2026, 1, 10, 14, 0, tzinfo=datetime.timezone.utc
                ),
                "name": "Video Event",
                "description_text": "Video planning description",
                "coverages": [
                    {
                        "coverage_id": ObjectId(),
                        "planning": {"g2_content_type": "picture"},
                        "news_coverage_status": {"label": "Planned"},
                    },
                    {
                        "coverage_id": ObjectId(),
                        "planning": {"g2_content_type": "video"},
                        "news_coverage_status": {"label": "On Merit"},
                        "assigned_to": {"user": user_id},
                    },
                ],
                "event_item": event_id,
            }

            self.app.data.insert("events", [event])
            self.app.data.insert("planning", [planning])

            self.app.data.update(
                "events",
                event_id,
                {"planning_ids": [planning_id]},
                event,
            )

            html = render_template(
                "internal_image_video_planning.html",
                items=[planning],
                app=self.app,
            )

            self.assertIn("<h1>Belga Image Video Planning", html)
            self.assertIn("<b>Video Event</b>", html)
            self.assertNotIn("PICTURE", html)
            self.assertNotIn("TEXT", html)
            self.assertNotIn("BELGA VIDEO", html)
            self.assertIn(user["sign_off"], html)
            self.assertNotIn(planning["description_text"], html)

    def test_belga_image_video_planning_chronological_order(self):
        """Belga Image Video Planning lists events chronologically by day."""
        with self.app.app_context():
            user_id = ObjectId()

            user = {
                "_id": user_id,
                "username": f"testuser_chrono_{user_id}",
                "sign_off": "TST",
            }
            self.app.data.insert("users", [user])

            event1_id = ObjectId()
            planning1_id = ObjectId()
            event2_id = ObjectId()
            planning2_id = ObjectId()

            event1 = {
                "_id": event1_id,
                "name": "Later Event",
                "dates": {
                    "start": datetime.datetime(
                        2026, 1, 10, 16, 0, tzinfo=datetime.timezone.utc
                    ),
                    "end": datetime.datetime(
                        2026, 1, 10, 18, 0, tzinfo=datetime.timezone.utc
                    ),
                    "tz": "Europe/Brussels",
                },
                "calendars": [{"qcode": "Sports", "name": "(7) Sports"}],
            }

            planning1 = {
                "_id": planning1_id,
                "type": "planning",
                "planning_date": datetime.datetime(
                    2026, 1, 10, 16, 0, tzinfo=datetime.timezone.utc
                ),
                "name": "Later Event",
                "coverages": [
                    {
                        "coverage_id": ObjectId(),
                        "planning": {"g2_content_type": "video"},
                        "assigned_to": {"user": user_id},
                    },
                ],
                "event_item": event1_id,
            }

            event2 = {
                "_id": event2_id,
                "name": "Earlier Event",
                "dates": {
                    "start": datetime.datetime(
                        2026, 1, 10, 10, 0, tzinfo=datetime.timezone.utc
                    ),
                    "end": datetime.datetime(
                        2026, 1, 10, 12, 0, tzinfo=datetime.timezone.utc
                    ),
                    "tz": "Europe/Brussels",
                },
                "calendars": [{"qcode": "General", "name": "(1) General"}],
            }

            planning2 = {
                "_id": planning2_id,
                "type": "planning",
                "planning_date": datetime.datetime(
                    2026, 1, 10, 10, 0, tzinfo=datetime.timezone.utc
                ),
                "name": "Earlier Event",
                "coverages": [
                    {
                        "coverage_id": ObjectId(),
                        "planning": {"g2_content_type": "video"},
                        "assigned_to": {"user": user_id},
                    },
                ],
                "event_item": event2_id,
            }

            self.app.data.insert("events", [event1, event2])
            self.app.data.insert("planning", [planning1, planning2])

            self.app.data.update(
                "events",
                event1_id,
                {"planning_ids": [planning1_id]},
                event1,
            )
            self.app.data.update(
                "events",
                event2_id,
                {"planning_ids": [planning2_id]},
                event2,
            )

            html = render_template(
                "internal_image_video_planning.html",
                items=[planning1, planning2],
                app=self.app,
            )

            earlier_pos = html.find("<b>Earlier Event</b>")
            later_pos = html.find("<b>Later Event</b>")
            self.assertGreater(earlier_pos, -1, "Earlier Event should be in output")
            self.assertGreater(later_pos, -1, "Later Event should be in output")
            self.assertLess(
                earlier_pos, later_pos, "Earlier Event should appear before Later Event"
            )

    def test_belga_image_photo_planning_event_ids_json(self):
        with self.app.app_context():
            photo_event_id = ObjectId()
            video_event_id = ObjectId()

            planning_items = [
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "event_item": photo_event_id,
                    "coverages": [
                        {
                            "coverage_id": ObjectId(),
                            "planning": {"g2_content_type": "picture"},
                        }
                    ],
                },
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "event_item": photo_event_id,
                    "coverages": [
                        {
                            "coverage_id": ObjectId(),
                            "planning": {"g2_content_type": "picture"},
                        }
                    ],
                },
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "event_item": video_event_id,
                    "coverages": [
                        {
                            "coverage_id": ObjectId(),
                            "planning": {"g2_content_type": "video"},
                        }
                    ],
                },
            ]

            output = render_template(
                "internal_image_photo_planning_event_ids.html",
                items=planning_items,
                app=self.app,
            ).strip()

            self.assertEqual(json.loads(output), [str(photo_event_id)])

    def test_belga_image_video_planning_event_ids_json(self):
        with self.app.app_context():
            video_event_id = ObjectId()
            photo_event_id = ObjectId()

            planning_items = [
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "event_item": video_event_id,
                    "coverages": [
                        {
                            "coverage_id": ObjectId(),
                            "planning": {"g2_content_type": "video"},
                        }
                    ],
                },
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "event_item": photo_event_id,
                    "coverages": [
                        {
                            "coverage_id": ObjectId(),
                            "planning": {"g2_content_type": "picture"},
                        }
                    ],
                },
            ]

            output = render_template(
                "internal_image_video_planning_event_ids.html",
                items=planning_items,
                app=self.app,
            ).strip()

            self.assertEqual(json.loads(output), [str(video_event_id)])

    def test_internal_bilingual_planning_advisory_tomorrow_event_ids_json(self):
        with self.app.app_context():
            event_id_1 = ObjectId()
            event_id_2 = ObjectId()
            event_id_internal = ObjectId()

            planning_items = [
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "event_item": event_id_1,
                    "coverages": [
                        {
                            "coverage_id": ObjectId(),
                            "planning": {"g2_content_type": "text"},
                        }
                    ],
                },
                # Duplicate event reference - should be deduplicated
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "event_item": event_id_1,
                    "coverages": [
                        {
                            "coverage_id": ObjectId(),
                            "planning": {"g2_content_type": "picture"},
                        }
                    ],
                },
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "event_item": event_id_2,
                    "coverages": [
                        {
                            "coverage_id": ObjectId(),
                            "planning": {"g2_content_type": "video"},
                        }
                    ],
                },
                # Event with internal Calendar set must still be delivered
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "event_item": event_id_internal,
                    "coverages": [
                        {
                            "coverage_id": ObjectId(),
                            "planning": {"g2_content_type": "text"},
                        }
                    ],
                },
                # Planning item without an event_item should be skipped
                {
                    "_id": ObjectId(),
                    "type": "planning",
                    "coverages": [],
                },
            ]

            output = render_template(
                "internal_bilingual_planning_advisory_tomorrow_event_ids.html",
                items=planning_items,
                app=self.app,
            ).strip()

            self.assertEqual(
                json.loads(output),
                [str(event_id_1), str(event_id_2), str(event_id_internal)],
            )
