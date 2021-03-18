from superdesk import get_resource_service
from apps.archive.common import CONTENT_STATE
from .set_default_metadata import set_default_metadata


def desk_incoming_rule_macro(item, **kwargs):
    """This macro runs two macros set_default_metadata and desk_routing."""

    macro_service = get_resource_service('macros')
    desk_routing_macro = macro_service.get_macro_by_name('desk_routing')

    new_item = item
    if item.get('state') == CONTENT_STATE.INGESTED:
        new_item = set_default_metadata(item, **kwargs)

    desk_routing_macro['callback'](new_item, **kwargs)


name = 'desk_incoming_rule_macro'
label = 'Desk Incoming Rule Macro'
callback = desk_incoming_rule_macro
access_type = 'backend'
action_type = 'direct'
