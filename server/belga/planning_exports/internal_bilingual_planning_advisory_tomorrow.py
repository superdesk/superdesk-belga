from .format_planning_for_tomorrow_bilingual import (
    format_planning_for_tomorrow_bilingual as format_public_planning,
)
from typing import List, Dict, Any
from superdesk import get_resource_service


def format_planning_for_tomorrow_bilingual_internal(
    planning_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Reuse the bilingual planning formatter for general info,
    but replace coverages with internal-specific coverage logic.
    """
    # Get the daily program planning formatte
    base_formatted = format_public_planning(planning_data)

    planning_service = get_resource_service("planning")
    desk_service = get_resource_service("desks")
    user_service = get_resource_service("users")

    # Replace coverages with internal logic
    for calendar_group in base_formatted["events"]:
        for planning in calendar_group["events"]:
            # Find the original planning item
            original = next(
                (
                    p
                    for p in planning_data
                    if (p.get("name") or p.get("slugline") or p.get("headline"))
                    in (planning["title_nl"], planning["title_fr"])
                ),
                None,
            )
            if original:
                planning["coverages"] = get_coverages_bilingual_internal(
                    original, planning_service, desk_service, user_service
                )

    return base_formatted


def get_coverages_bilingual_internal(
    item: Dict[str, Any], planning_service, desk_service, user_service
) -> List[Dict[str, Any]]:
    """Get coverage info with proper status, language and assigned user for export"""
    formatted_coverages = []
    lang_map = {"nl": "N", "n": "N", "fr": "F", "f": "F", "de": "DE"}

    planning_ids = item.get("planning_ids") or [item.get("_id")]

    for planning_id in planning_ids:
        planning_item = planning_service.find_one(req=None, _id=planning_id)
        if not planning_item:
            continue

        for coverage in planning_item.get("coverages", []):
            if not isinstance(coverage, dict):
                continue

            # Coverage type
            planning_info = coverage.get("planning") or {}
            cov_type = (
                planning_info.get("g2_content_type")
                or coverage.get("g2_content_type")
                or ""
            ).lower()

            # Coverage status
            cov_status = (
                coverage.get("news_coverage_status", {}).get("label") or "ON MERIT"
            ).upper()

            # Desk language
            desk_language_code = "N"
            desk_id = (
                planning_info.get("desk")
                or coverage.get("assigned_to", {}).get("desk")
                or item.get("task", {}).get("desk")
            )

            assigned_user_id = coverage.get("assigned_to", {}).get("user")
            username = ""

            if assigned_user_id:
                # Coverage assigned to a user
                user_item = user_service.find_one(req=None, _id=assigned_user_id)
                if user_item:
                    username = user_item.get("sign_off") or user_item.get("username")

            elif desk_id:
                desk_item = desk_service.find_one(req=None, _id=desk_id)
                if desk_item and desk_item.get("desk_language"):
                    desk_language_code = lang_map.get(
                        desk_item["desk_language"].lower(), "N"
                    )
                    # first member’s sign_off as fallback
                    if desk_item.get("members"):
                        first_member = desk_item["members"][0]
                        user_item = user_service.find_one(
                            req=None, _id=first_member["user"]
                        )
                        if user_item:
                            username = user_item.get("sign_off") or user_item.get(
                                "username"
                            )

            # Format coverage display
            if cov_type == "text":
                coverage_display = f"TEXT {desk_language_code} ({cov_status})"
            else:
                coverage_display = f"{cov_type.upper()} ({cov_status})"

            if username:
                coverage_display = f"{coverage_display} BY {username.upper()}"

            formatted_coverages.append(
                {
                    "display": coverage_display,
                    "type": cov_type,
                    "status": cov_status,
                    "language": desk_language_code,
                    "username": username,
                }
            )

    return formatted_coverages
