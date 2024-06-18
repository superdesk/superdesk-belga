# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : Ketan
# Creation: 2024-06-18

from superdesk.commands.data_updates import BaseDataUpdate


UPDATED_TEMPLATES = [
    {
        "_id": "planning_multiple_agendas",
        "name": "multiple-agendas",
        "init_version": 1,
        "type": "planning",
        "data": {
            "slugline": "multiple-agendas",
            "body_html_template": "planning_multiple_agendas_template.html",
        },
        "label": "Multiple Agendas",
    },
    {
        "_id": "planning_multiple_agendas_internal",
        "name": "internal",
        "init_version": 1,
        "type": "planning",
        "data": {
            "slugline": "internal",
            "body_html_template": "planning_multiple_agendas_internal_template.html",
        },
        "label": "Internal",
    },
    {
        "_id": "dutch_news_events_list",
        "init_version": 1,
        "name": "dutch_news_events_list",
        "type": "event",
        "data": {"body_html_template": "dutch_news_events_list_export.html"},
        "label": "Internationale sportkalender",
    },
    {
        "_id": "french_news_events_list",
        "init_version": 1,
        "name": "french_news_events_list",
        "type": "event",
        "data": {"body_html_template": "french_news_events_list_export.html"},
        "label": "Calendrier sportif international",
    },
    {
        "_id": "french_news_events_list_tommorrow",
        "init_version": 1,
        "name": "french_news_events_list_tommorrow",
        "type": "event",
        "data": {"body_html_template": "french_news_events_tommorrow.html"},
        "label": "Program of the day - NPF",
    },
    {
        "_id": "dutch_news_events_list_tommorrow",
        "init_version": 1,
        "name": "dutch_news_events_list_tommorrow",
        "type": "event",
        "data": {"body_html_template": "dutch_news_events_tommorrow.html"},
        "label": "Program of the day - NPN",
    },
]


class DataUpdate(BaseDataUpdate):
    resource = "planning_export_templates"

    def forwards(self, mongodb_collection, mongodb_database):
        updated_templates_dict = {
            template["_id"]: template for template in UPDATED_TEMPLATES
        }

        for _id, template in updated_templates_dict.items():
            mongodb_collection.update_one({"_id": _id}, {"$set": template}, upsert=True)

    def backwards(self, mongodb_collection, mongodb_database):
        pass
