from superdesk.signals import item_create, item_update, item_move, item_rewrite, item_duplicate

from . import generate_id_for_url
from . import unmark_user_when_moved_to_incoming_stage
from . import update
from . import handle_translate


def init_app(_app):
    # generate id for belga url
    item_create.connect(generate_id_for_url.handle_create)
    item_update.connect(generate_id_for_url.handle_update)
    # unmark user when moved to incoming stage
    item_move.connect(unmark_user_when_moved_to_incoming_stage.unmark_user)
    # change profile from ALERT to TEXT on update
    item_rewrite.connect(update.handle_update)
    # remove all belga archive 360 associations from a translation item
    item_duplicate.connect(handle_translate.handle_duplicate)
