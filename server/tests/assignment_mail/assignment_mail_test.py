from unittest import TestCase
from flask import render_template
from app import get_app


class AssignmentMailsTests(TestCase):
    app = get_app()
    event = {
        "name": "Tech Expo 2024",
        "_id": "67890",
        "calendars": [{"name": "Upcoming Events"}, {"name": "Industry Conferences"}],
        "slugline": "Innovations in Technology",
        "definition_short": "A showcase of the latest advancements in technology",
        "ednote": "Focus on new AI products.",
        "internal_note": "Coordinate with the marketing team for live coverage.",
        "related_items": [
            {
                "_id": "urn:belga.be:360archive:50457251",
                "headline": "AI Breakthroughs in 2024",
            },
            {
                "_id": "urn:belga.be:360archive:98765",
                "slugline": "Future of Tech Expos",
            },
        ],
    }
    assignment = {"name": "New Product"}

    def test_assignment_data(self):
        with self.app.app_context():
            rendered = render_template(
                "assignment_details_email.html",
                event=self.event,
                assignment=self.assignment,
                app=self.app,
            )
            self.assertIn("<h3>Event: Tech Expo 2024</h3>", rendered)
            self.assertIn(
                "<p><strong>Calendars:</strong> Upcoming Events, Industry Conferences</p>",
                rendered,
            )
            self.assertIn(
                "<p><strong>Event Topic:</strong> Innovations in Technology</p>",
                rendered,
            )
            self.assertIn(
                "<p><strong>Description:</strong> A showcase of the latest advancements in technology</p>",
                rendered,
            )
            self.assertIn(
                "<p><strong>Ed Note:</strong> Focus on new AI products.</p>", rendered
            )
            self.assertIn(
                "<p><strong>Internal Note:</strong> Coordinate with the marketing team for live coverage.</p>",
                rendered,
            )
            self.assertIn("<h3>Related Articles:</h3>", rendered)
            self.assertIn(
                (
                    '<a href="https://www.belgabox.be/belgabox/fo/detail?'
                    "contentType=news&targetSide=Right&id=50457251&parentId="
                    '50457251&isArchive=true">View Article</a>'
                ),
                rendered,
            )
            self.assertIn(
                (
                    '<a href="https://www.belgabox.be/belgabox/fo/detail?'
                    "contentType=news&targetSide=Right&id=98765&parentId="
                    '98765&isArchive=true">View Article</a>'
                ),
                rendered,
            )
