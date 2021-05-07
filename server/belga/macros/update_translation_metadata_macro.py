import logging
from flask_babel import lazy_gettext
from superdesk import get_resource_service

logger = logging.getLogger(__name__)


def update_translation_metadata_macro(item, **kwargs):
    """This macro is used to change the correspondent author role to editor on translation"""

    authoring_roles = get_resource_service("vocabularies").find_one(
        req=None, _id="author_roles"
    )
    if not authoring_roles or not authoring_roles.get("items"):
        logger.warning("Author roles are not specified")
        return

    # get editor role from author roles
    editor = [
        role for role in authoring_roles["items"] if role.get("qcode") == "EDITOR"
    ]

    authors = item.get("authors", [])

    # get correspondents role from authors
    correspondents = [
        author for author in authors if author.get("role") == "CORRESPONDENT"
    ]

    if editor and correspondents:
        editor = editor[0]
        for correspondent in correspondents:
            editor_id = [
                editor["qcode"] if data == "CORRESPONDENT" else data
                for data in correspondent.get("_id", [])
            ]

            # check author with _id is already exists
            author_already_exists = any(
                author for author in authors if author["_id"] == editor_id
            )
            if author_already_exists:
                continue

            # update author role correspondent to editor
            correspondent.update(
                {"name": editor["name"], "role": editor["qcode"], "_id": editor_id}
            )

    return item


name = "Update Translation Metadata Macro"
label = lazy_gettext("Update Translation Metadata Macro")
callback = update_translation_metadata_macro
access_type = "backend"
action_type = "interactive"
