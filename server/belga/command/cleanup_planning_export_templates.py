import superdesk


TEMPLATE_IDS = [
    "planning_multiple_agendas",
    "planning_multiple_agendas_internal",
    "french_planning_advisory_tomorrow",
    "dutch_planning_advisory_tomorrow",
]


class CleanupPlanningExportTemplatesCommand(superdesk.Command):
    """Remove deprecated Belga planning export templates."""

    def run(self):
        service = superdesk.get_resource_service("planning_export_templates")

        for template_id in TEMPLATE_IDS:
            service.delete({"_id": template_id})
            print(f"Deleted {template_id}")


superdesk.command("belga:cleanup_planning_export_templates", CleanupPlanningExportTemplatesCommand())
