import superdesk


TEMPLATE_IDS = [
    "planning_multiple_agendas",
    "planning_multiple_agendas_internal",
    "french_planning_advisory_tomorrow",
    "dutch_planning_advisory_tomorrow",
]


class CleanupPlanningExportTemplatesCommand(superdesk.Command):
    """Remove deprecated Belga planning export templates."""

    option_list = [
        superdesk.Option("--dry-run", action="store_true"),
    ]

    def run(self, dry_run=False):
        service = superdesk.get_resource_service("planning_export_templates")

        for template_id in TEMPLATE_IDS:
            template = service.find_one(req=None, _id=template_id)
            if not template:
                print(f"Missing {template_id}")
                continue

            if dry_run:
                print(f"Would delete {template_id}")
                continue

            service.delete({"_id": template_id})
            print(f"Deleted {template_id}")


superdesk.command("belga:cleanup_planning_export_templates", CleanupPlanningExportTemplatesCommand())
