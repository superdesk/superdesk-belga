# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : Ketan
# Creation: 2024-06-17

import os
import superdesk
import json


class PlanningTemplatesUpdateCommand(superdesk.Command):
    """
    Command use for updating planning_export_templates
    """

    option_list = []

    def run(self):
        planning_export_templates_service = superdesk.get_resource_service(
            "planning_export_templates"
        )
        self.filename = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../data",
            "planning_export_templates.json",
        )
        with open(self.filename, "r", encoding="utf-8") as file:
            templates = json.load(file)

        for template in templates:
            existing_template = planning_export_templates_service.find_one(
                req=None, _id=template["_id"]
            )
            if existing_template.get("init_version", 0) != template.get(
                "init_version", 0
            ):
                planning_export_templates_service.update(
                    existing_template["_id"], template, existing_template
                )
                print(f"Template {template['name']} is updated....")


superdesk.command("planning_export_template:update", PlanningTemplatesUpdateCommand())
