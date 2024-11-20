from typing import Optional, Dict, Any, List
import logging

from superdesk import get_resource_service
from apps.search_providers.proxy import PROXY_ENDPOINT
from planning.types import Event, Planning, Assignment, EventRelatedItem


logger = logging.getLogger(__name__)


def _get_associated_event_from_planning(planning: Planning) -> Optional[Event]:
    event_id = planning.get("event_item")
    if not event_id:
        # No Event associated with the Planning item, no need to continue
        return None

    try:
        event = get_resource_service("events").find_one(req=None, _id=event_id)
    except Exception:
        # Failed to retrieve the Event
        logger.exception("Exception raised while finding event")
        return None

    if not event:
        # Event not found for some reason
        logger.error("Associated event not found")
        return None

    return event


def _get_related_content_field_to_use(content_profile: Dict[str, Any]) -> Optional[str]:
    related_content_fields = [
        field
        for field, schema in (content_profile.get("schema") or {}).items()
        if (schema or {}).get("type") == "related_content"
    ]

    if len(related_content_fields) == 0:
        # No ``related_content`` fields found, no need to continue
        return None
    elif "belga_related_articles" in related_content_fields:
        related_content_field = "belga_related_articles"
    else:
        # ``belga_related_articles`` field not found, but only 1 ``related_content`` field is registered, use that
        logger.warning(
            "'belga_related_articles' field not found, defaulting to first related content field"
        )
        related_content_field = related_content_fields[0]

    return related_content_field


def _get_related_items_from_planning(
    planning: Planning, language: Optional[str] = None
) -> List[EventRelatedItem]:
    event = _get_associated_event_from_planning(planning)
    if not event:
        return []

    return [
        related_item
        for related_item in event.get("related_items") or []
        if not language or related_item.get("language") == language
    ]


def _get_event_related_item_from_search_proxy(
    related_item: EventRelatedItem,
) -> Optional[Dict[str, Any]]:
    provider_id = related_item.get("search_provider")
    if not provider_id:
        logger.error("Related item doesnt have 'search_provider' attribute")
        return None

    related_item_id = related_item.get("guid")
    if not related_item_id:
        logger.error("Related item doesnt have 'guid' attribute")
        return None

    try:
        external_item = get_resource_service(PROXY_ENDPOINT).fetch(
            related_item_id, provider_id
        )
    except Exception:
        logger.exception("Exception raised while fetching item from search proxy")
        return None

    if not external_item:
        logger.error("Item not found using search proxy")
        return None

    return external_item


def on_assignment_start_working(
    _sender: Any,
    assignment: Assignment,
    planning: Planning,
    item: Dict[str, Any],
    content_profile: Dict[str, Any],
):
    # 1. Find related articles field in content_profile
    related_content_field = _get_related_content_field_to_use(content_profile)
    if not related_content_field:
        return

    # 2. Get list of related items, based on language of the content item
    related_items = _get_related_items_from_planning(planning, item.get("language"))
    if not related_items:
        # No related items in the appropriate language attached, no need to continue
        return

    # 3. Iterate over ``related_items`` and:
    #   2.1. Get search provider details
    #   2.2. Fetch entire related item from search provider
    #   2.3. Add entire related item to content's related articles field
    content_index = 1
    for related_item in related_items:
        external_item = _get_event_related_item_from_search_proxy(related_item)
        if not external_item:
            continue

        # Add ``"order": content_index`` to related_item
        external_item["order"] = content_index
        item.setdefault("associations", {})[
            f"{related_content_field}--{content_index}"
        ] = external_item
        content_index += 1
