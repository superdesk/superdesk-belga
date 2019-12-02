from superdesk import get_resource_service
from .set_default_metadata import set_default_metadata


def set_default_meta_with_desk_routing(item, **kwargs):
    """This macro run two macros set_default_metadata and desk_routing."""

    macro_service = get_resource_service('macros')
    desk_routing_macro = macro_service.get_macro_by_name('desk_routing')

    new_item = set_default_metadata(item, **kwargs)
    desk_routing_macro['callback'](new_item, **kwargs)


name = 'set_default_meta_with_desk_routing'
label = 'Set Default Metadata With Desk Routing'
callback = set_default_meta_with_desk_routing
access_type = 'backend'
action_type = 'direct'
