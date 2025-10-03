from .format_news_events_tommorow_bilingual import (
    format_event_for_tommorow_bilingual as format_daily_bilingual,
)
from typing import List, Dict, Any
from superdesk import get_resource_service


def format_event_for_tommorow_bilingual_internal(
    event_data: List[Dict[str, Any]], locale: str
) -> Dict[str, Any]:
    """
    Reuse the daily bilingual formatting for general event info,
    but replace coverages with internal-specific coverage logic
    """
    # # Get the daily program event formatte
    base_formatted = format_daily_bilingual(event_data, locale)

    # Replace coverages with internal coverage info
    for day_group in base_formatted["events"]:
        for event in day_group["events"]:
            # The event dictionary contains all original fields
            # Find the original event by title (or slugline)
            original_event = next(
                (
                    e
                    for e in event_data
                    if (e.get("name") or e.get("slugline"))
                    in (event["title_nl"], event["title_fr"])
                ),
                None,
            )
            if original_event:
                # Use internal coverage logic
                event["coverages"] = get_coverages_bilingual_internal(original_event)

    return base_formatted


def get_coverages_bilingual_internal(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get coverages with language and assigned user/desk info formatted for bilingual output"""
    formatted_coverages = []
    planning_ids = event.get("planning_ids", [])
    planning_service = get_resource_service("planning")
    desk_service = get_resource_service("desks")
    user_service = get_resource_service("users")

    for planning_id in planning_ids:
        planning_item = planning_service.find_one(req=None, _id=planning_id)
        if not planning_item:
            continue

        for coverage in planning_item.get("coverages", []):
            if not isinstance(coverage, dict):
                continue

            planning_info = coverage.get("planning", {})
            cov_type = (planning_info.get("g2_content_type") or "").lower()
            cov_status = (
                coverage.get("news_coverage_status", {})
                .get("label", "ON MERIT")
                .upper()
            )

            desk_language_code = "N"
            desk_id = (
                planning_info.get("desk")
                or coverage.get("assigned_to", {}).get("desk")
                or event.get("task", {}).get("desk")
            )
            assigned_user_id = coverage.get("assigned_to", {}).get("user")

            username = ""
            if assigned_user_id:
                user_item = user_service.find_one(req=None, _id=assigned_user_id)
                if user_item:
                    username = user_item.get("sign_off") or user_item.get("username")
            elif desk_id:
                desk_item = desk_service.find_one(req=None, _id=desk_id)
                if desk_item:
                    lang = desk_item.get("desk_language")
                    if lang:
                        lang = lang.lower()
                        if lang in ("nl", "n", "de"):
                            desk_language_code = "N"
                        elif lang in ("fr", "f"):
                            desk_language_code = "F"
                        else:
                            desk_language_code = "N"

                    # if no assigned user, take first member’s sign_off
                    if desk_item.get("members"):
                        first_member = desk_item["members"][0]
                        user_item = user_service.find_one(
                            req=None, _id=first_member["user"]
                        )
                        if user_item:
                            username = user_item.get("sign_off") or user_item.get(
                                "username"
                            )

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
