from superdesk.signals import (
    item_create,
    item_update,
    item_move,
    item_rewrite,
    item_duplicate,
)
from planning.signals import assignment_content_create

from . import generate_id_for_url
from . import unmark_user_when_moved_to_incoming_stage
from . import update
from . import handle_translate
from . import copy_related_article_from_assignment


def init_app(_app):
    # generate id for belga url
    item_create.connect(generate_id_for_url.handle_create)
    item_update.connect(generate_id_for_url.handle_update)
    # unmark user when moved to incoming stage
    item_move.connect(unmark_user_when_moved_to_incoming_stage.unmark_user)
    # change profile from ALERT to TEXT on update
    item_rewrite.connect(update.handle_update)
    # Disable and empty date time for coming_up field
    item_rewrite.connect(update.handle_coming_up_field)
    # remove all belga archive 360 associations from a translation item
    item_duplicate.connect(handle_translate.handle_duplicate)

    assignment_content_create.connect(
        copy_related_article_from_assignment.on_assignment_start_working
    )
