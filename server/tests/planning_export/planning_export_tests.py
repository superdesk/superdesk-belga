from unittest import TestCase
import datetime
from flask import render_template
from app import get_app


class PlanningExportTests(TestCase):
    def test_export(self):
        events = [
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
                        "translations": {
                            "name": {"nl": "REDWOLVES", "fr": "REDWOLVES"}
                        },
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
        app = get_app()
        with app.app_context():
            dutch_template_data = render_template(
                "dutch_news_events_list_export.html", items=events, app=app
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
            self.assertIn("<p>REDWOLVES</p>", dutch_template_data)
            self.assertIn("<p>New York, United States</p>", dutch_template_data)
            self.assertIn("<p>16u00</p>", dutch_template_data)
            self.assertIn("<p>NExxxxt Sunday 21.04.2024</p>", dutch_template_data)
            self.assertIn("<p>Description of event</p>", dutch_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a></p>',
                dutch_template_data,
            )
            self.assertIn("<h3>Maandag 22 april</h3>", dutch_template_data)
            self.assertIn("<p>SPORTS</p>", dutch_template_data)
            self.assertIn("<p>16u00</p>", dutch_template_data)
            self.assertIn("<p>NExxxxt Monday 22.04.2024</p>", dutch_template_data)
            self.assertIn("<p>Description of event</p>", dutch_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a></p>',
                dutch_template_data,
            )

            french_template_data = render_template(
                "french_news_events_list_export.html", items=events, app=app
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
            self.assertIn("<p>REDWOLVES</p>", french_template_data)
            self.assertIn("<p>New York, United States</p>", french_template_data)
            self.assertIn("<p>16u00</p>", french_template_data)
            self.assertIn("<p>NExxxxt Sunday 21.04.2024</p>", french_template_data)
            self.assertIn("<p>Description of event</p>", french_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a></p>',
                french_template_data,
            )
            self.assertIn("<h3>Lundi 22 avril</h3>", french_template_data)
            self.assertIn("<p>SPORTS</p>", french_template_data)
            self.assertIn("<p>16u00</p>", french_template_data)
            self.assertIn("<p>NExxxxt Monday 22.04.2024</p>", french_template_data)
            self.assertIn("<p>Description of event</p>", french_template_data)
            self.assertIn(
                '<p><a href="www.google.xom/new">www.google.xom/new</a></p>',
                french_template_data,
            )
