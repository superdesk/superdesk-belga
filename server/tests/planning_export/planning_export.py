from unittest import TestCase
import datetime
from belga.planning_exports.france_news_event_list import format_event_french
from belga.planning_exports.dutch_news_events_list import format_event_dutch


class PlanningTests(TestCase):
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
                        "name": "REDWOLVES",
                        "scheme": "belga-keywords",
                        "qcode": "REDWOLVES",
                        "translations": {
                            "name": {"nl": "REDWOLVES", "fr": "REDWOLVES"}
                        },
                    }
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
                "name": "NExxxxt Tuesday 23.04.2024",
                "dates": {
                    "start": datetime.datetime(
                        2024, 4, 23, 10, 30, tzinfo=datetime.timezone.utc
                    ),
                    "end": datetime.datetime(
                        2024, 4, 24, 15, 30, 59, tzinfo=datetime.timezone.utc
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
                "name": "NExxxxt Wednesday 24.04.2024",
                "dates": {
                    "start": datetime.datetime(
                        2024, 4, 24, 10, 30, tzinfo=datetime.timezone.utc
                    ),
                    "end": datetime.datetime(
                        2024, 4, 25, 15, 30, 59, tzinfo=datetime.timezone.utc
                    ),
                    "tz": "Asia/Calcutta",
                },
                "subject": [
                    {
                        "name": "BLACKARROWS",
                        "scheme": "belga-keywords",
                        "qcode": "BLACKARROWS",
                        "translations": {
                            "name": {"nl": "BLACKARROWS", "fr": "BLACKARROWS"}
                        },
                    }
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
                "name": "NExxxxt Thursday 25.04.2024",
                "dates": {
                    "start": datetime.datetime(
                        2024, 4, 25, 10, 30, tzinfo=datetime.timezone.utc
                    ),
                    "end": datetime.datetime(
                        2024, 4, 26, 15, 30, 59, tzinfo=datetime.timezone.utc
                    ),
                    "tz": "Asia/Calcutta",
                },
                "subject": [
                    {
                        "name": "SPORTS",
                        "qcode": "SPORTS",
                        "scheme": "belga-keywords",
                        "translations": {"name": {"nl": "SPORTS", "fr": "SPORTS"}},
                    }
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
                "name": "NExxxxt Friday 26.04.2024",
                "dates": {
                    "start": datetime.datetime(
                        2024, 4, 26, 10, 30, tzinfo=datetime.timezone.utc
                    ),
                    "end": datetime.datetime(
                        2024, 4, 27, 15, 30, 59, tzinfo=datetime.timezone.utc
                    ),
                    "tz": "Asia/Calcutta",
                },
                "subject": [
                    {
                        "name": "BLACKARROWS",
                        "qcode": "BLACKARROWS",
                        "scheme": "belga-keywords",
                        "translations": {
                            "name": {"nl": "BLACKARROWS", "fr": "BLACKARROWS"}
                        },
                    }
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
                "name": "NExxxxt Saturday 27.04.2024",
                "dates": {
                    "start": datetime.datetime(
                        2024, 4, 27, 10, 30, tzinfo=datetime.timezone.utc
                    ),
                    "end": datetime.datetime(
                        2024, 4, 28, 15, 30, 59, tzinfo=datetime.timezone.utc
                    ),
                    "tz": "Asia/Calcutta",
                },
                "subject": [
                    {
                        "name": "MUSIC FESTIVALS",
                        "qcode": "MUSIC FESTIVALS",
                        "scheme": "belga-keywords",
                        "translations": {
                            "name": {"nl": "MUSIC FESTIVALS", "fr": "MUSIC FESTIVALS"}
                        },
                    }
                ],
            },
        ]

        data = format_event_french(events)
        events_list = data.get("events")

        self.assertEqual(len(data), 2)
        self.assertEqual(
            data["intro"]["title"],
            "Calendrier sportif international du Dimanche 21 au Samedi 27 Avril",
        )
        self.assertEqual(
            data["intro"]["subtitle"],
            "Principaux événements inscrits au calendrier sportif international du Dimanche 21 au Samedi 27 Avril:",
        )

        self.assertEqual(len(events_list), 7)
        self.assertEqual(events_list[0]["date"], "Dimanche 21 avril")
        self.assertEqual(len(events_list[0]["events"]), 1)

        event = events_list[0]["events"][0]
        self.assertEqual(event["title"], "NExxxxt Sunday 21.04.2024")
        self.assertEqual(event["description"], "Description of event")
        self.assertEqual(event["address"]["country"], "United States")
        self.assertEqual(event["subject"], "REDWOLVES")
        self.assertEqual(event["local_time"], "16u00")

        data = format_event_dutch(events)
        events_list = data.get("events")

        self.assertEqual(len(data), 2)
        self.assertEqual(
            data["intro"]["title"],
            "Internationale sportkalender van Zondag 21 tot Zaterdag 27 April",
        )
        self.assertEqual(
            data["intro"]["subtitle"],
            "De belangrijkste sportevenementen op de Belgische en internationale sportkalender van Zondag 21 tot Zaterdag 27 April:",
        )

        self.assertEqual(len(events_list), 7)
        self.assertEqual(events_list[0]["date"], "Zondag 21 april")
        self.assertEqual(len(events_list[0]["events"]), 1)

        event = events_list[0]["events"][0]
        self.assertEqual(event["title"], "NExxxxt Sunday 21.04.2024")
        self.assertEqual(event["description"], "Description of event")
        self.assertEqual(event["address"]["country"], "United States")
        self.assertEqual(event["subject"], "REDWOLVES")
        self.assertEqual(event["local_time"], "16u00")
