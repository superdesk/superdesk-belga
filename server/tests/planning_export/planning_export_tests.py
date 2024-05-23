from unittest import TestCase
import datetime
from flask import render_template
from app import get_app
from bson import ObjectId


class PlanningExportTests(TestCase):
    app = get_app()
    events_for_week = [
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
                        "boundingbox": [
                            "40.4765780",
                            "40.9176300",
                            "-74.2588430",
                            "-73.7002330",
                        ],
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
            "links": ["www.google.xom/new"],
        },
    ]
    events_for_tommorow = [
        {
            "calendars": [
                {"is_active": True, "name": "Sport", "qcode": "sport"},
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
                        "boundingbox": [
                            "40.4765780",
                            "40.9176300",
                            "-74.2588430",
                            "-73.7002330",
                        ],
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
            "calendars": [{"is_active": True, "name": "Business", "qcode": "business"}],
            "description_text": "Description of event",
            "name": "NExxxxt Monday 22.04.2024",
            "dates": {
                "start": datetime.datetime(
                    2024, 4, 21, 10, 30, tzinfo=datetime.timezone.utc
                ),
                "end": datetime.datetime(
                    2024, 4, 22, 15, 30, 59, tzinfo=datetime.timezone.utc
                ),
                "tz": "Asia/Calcutta",
            },
            "links": ["www.google.xom/new"],
            "event_contact_info": [
                "5ab491271d41c88e98ad9336",
                "6618415a1704a42950a4eb62",
            ],
            "planning_ids": [ObjectId("6618415a1704a42950a4eb64")],
        },
        {
            "calendars": [{"is_active": True, "name": "Sport", "qcode": "sport"}],
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
                    "public": True,
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
                                "slugline": "coverage slugline",
                                "ednote": "test coverage, I want 250 words",
                                "scheduled": "2029-10-12T14:00:00+0000",
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
                            "coverage_id": "cov1",
                            "planning": {
                                "g2_content_type": "picture",
                                "slugline": "coverage slugline",
                                "ednote": "test coverage, I want 250 words",
                                "scheduled": "2029-10-12T14:00:00+0000",
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

    def tearDown(self):
        # Clean up all documents in the contacts collection after each test
        with self.app.app_context():
            self.app.data.remove("contacts", {})
            self.app.data.remove("planning", {})

    def test_export_week(self):
        with self.app.app_context():
            events = self.events_for_week
            dutch_template_data = render_template(
                "dutch_news_events_list_export.html", items=events, app=self.app
            )
            self.assertIn(
                "<h2>Internationale sportkalender van Zondag 21 tot Maandag 22 April</h2>",
                dutch_template_data,
            )
            self.assertIn(
                (
                    "<p>De belangrijkste sportevenementen op de Belgische en "
                    "internationale sportkalender van Zondag 21 tot Maandag 22 April:</p>"
                ),
                dutch_template_data,
            )
            self.assertIn("<h3>Zondag 21 april</h3>", dutch_template_data)
            self.assertIn("<p>REDWOLVES<br></p>", dutch_template_data)
            self.assertIn("<p>New York, United States<br></p>", dutch_template_data)
            self.assertIn(
                "<p>16u00, NExxxxt Sunday 21.04.2024<br></p>", dutch_template_data
            )
            self.assertIn("<p>Description of event<br></p>", dutch_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a><br></p>',
                dutch_template_data,
            )
            self.assertIn("<h3>Maandag 22 april</h3>", dutch_template_data)
            self.assertIn("<p>SPORTS<br></p>", dutch_template_data)
            self.assertIn(
                "<p>16u00, NExxxxt Monday 22.04.2024<br></p>", dutch_template_data
            )
            self.assertIn("<p>Description of event<br></p>", dutch_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a><br></p>',
                dutch_template_data,
            )

            french_template_data = render_template(
                "french_news_events_list_export.html", items=events, app=self.app
            )
            self.assertIn(
                "<h2>Calendrier sportif international du Dimanche 21 au Lundi 22 Avril</h2>",
                french_template_data,
            )
            self.assertIn(
                (
                    "<p>Principaux événements inscrits au calendrier sportif "
                    "international du Dimanche 21 au Lundi 22 Avril:</p>"
                ),
                french_template_data,
            )
            self.assertIn("<h3>Dimanche 21 avril</h3>", french_template_data)
            self.assertIn("<p>REDWOLVES<br></p>", french_template_data)
            self.assertIn("<p>New York, United States<br></p>", french_template_data)
            self.assertIn(
                "<p>16u00, NExxxxt Sunday 21.04.2024<br></p>", french_template_data
            )
            self.assertIn("<p>Description of event<br></p>", french_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a><br></p>',
                french_template_data,
            )
            self.assertIn("<h3>Lundi 22 avril</h3>", french_template_data)
            self.assertIn("<p>SPORTS<br></p>", french_template_data)
            self.assertIn(
                "<p>16u00, NExxxxt Monday 22.04.2024<br></p>", french_template_data
            )
            self.assertIn("<p>Description of event<br></p>", french_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a><br></p>',
                french_template_data,
            )

            new_events = [
                {
                    "dates": {
                        "start": datetime.datetime(
                            2024, 4, 24, 22, 00, 00, tzinfo=datetime.timezone.utc
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
                            2024, 4, 24, 22, 59, 00, tzinfo=datetime.timezone.utc
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
                "dutch_news_events_list_export.html", items=new_events, app=self.app
            )
            self.assertIn("<h3>Donderdag 25 april</h3>", template_data)
            self.assertIn("<p>00u00, one event<br></p>", template_data)
            self.assertIn("<p>00u59, Two event<br></p>", template_data)

            template_data = render_template(
                "french_news_events_list_export.html", items=new_events, app=self.app
            )
            self.assertIn("<h3>Jeudi 25 avril</h3>", template_data)
            self.assertIn("<p>00u00, one event<br></p>", template_data)
            self.assertIn("<p>00u59, Two event<br></p>", template_data)

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
            self.assertIn("<h3>Business</h3>", dutch_data)
            self.assertIn("<p>16:00 - 21:00<br></p>", dutch_data)
            self.assertIn("<p>NExxxxt Monday 22.04.2024<br></p>", dutch_data)
            self.assertIn("<p>Description of event<br></p>", dutch_data)
            self.assertIn(
                "<p><a href='www.google.xom/new'>www.google.xom/new</a><br></p>",
                dutch_data,
            )
            self.assertIn(
                "<p>FUBAR - John Doe - Media Contact - jdoe@fubar.com - 99999999 - 666 - fubar.com<br></p>",
                dutch_data,
            )
            self.assertIn(
                (
                    "<p>FUBAR - Billiam Doe - Associate Consultant - "
                    "funkbio@fubar.com - 99999999 - 666 - funkbar.com<br></p>"
                ),
                dutch_data,
            )
            self.assertIn("<p>Text, On merit<br></p>", dutch_data)
            self.assertIn("<p>Picture, Planned<br></p>", dutch_data)

            self.assertIn("<h3>Sport</h3>", dutch_data)
            self.assertIn("<p>16:00 - 21:00<br></p>", dutch_data)
            self.assertIn("<p>New York, United States<br></p>", dutch_data)
            self.assertIn("<p>NExxxxt Sunday 21.04.2024<br></p>", dutch_data)
            self.assertIn("<p>Description of event<br></p>", dutch_data)
            self.assertIn(
                "<p><a href='www.google.xom/new'>www.google.xom/new</a><br></p>",
                dutch_data,
            )
            self.assertIn(
                "<p>FUBAR - John Doe - Media Contact - jdoe@fubar.com - 99999999 - 666 - fubar.com<br></p>",
                dutch_data,
            )
            self.assertIn(
                (
                    "<p>FUBAR - Billiam Doe - Associate Consultant "
                    "- funkbio@fubar.com - 99999999 - 666 - funkbar.com<br></p>"
                ),
                dutch_data,
            )
            self.assertIn("<p>Text, On merit<br></p>", dutch_data)
            self.assertIn("<p>Picture, Planned<br></p>", dutch_data)

            self.assertIn("<p>00:00 - 23:59<br></p>", dutch_data)
            self.assertIn("<p>NExxxxt Monday 22.04.2024<br></p>", dutch_data)
            self.assertIn("<p>NExxxxt Sunday 21.04.2024<br></p>", dutch_data)
            self.assertIn("<p>Description of event<br></p>", dutch_data)
            self.assertIn(
                "<p><a href='www.google.xom/new'>www.google.xom/new</a><br></p>",
                dutch_data,
            )
            self.assertIn(
                "<p>FUBAR - John Doe - Media Contact - jdoe@fubar.com - 99999999 - 666 - fubar.com<br></p>",
                dutch_data,
            )
            self.assertIn(
                (
                    "<p>FUBAR - Billiam Doe - Associate Consultant - "
                    "funkbio@fubar.com - 99999999 - 666 - funkbar.com<br></p>"
                ),
                dutch_data,
            )
            self.assertIn("<p>Text, On merit<br></p>", dutch_data)
            self.assertIn("<p>Picture, Planned<br></p>", dutch_data)
