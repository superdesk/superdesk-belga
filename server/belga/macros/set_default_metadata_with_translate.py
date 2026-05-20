# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
import logging
from copy import deepcopy
from .common import get_cv_by_qcode
from superdesk import get_resource_service
from superdesk.errors import StopDuplication
from superdesk.types import ContentFiltersResource
from superdesk.publish_async.publish_cache import PublishCache
from superdesk.publish_async.utils import item_matches_content_filter
from superdesk.metadata.utils import generate_guid
from superdesk.metadata.item import GUID_TAG
from apps.archive.common import ITEM_DUPLICATE
from .set_default_metadata import get_default_content_template, set_default_metadata
from .update_translation_metadata_macro import update_translation_metadata_macro

logger = logging.getLogger(__name__)


def _map_eco_package_subject(original_item):
    """Map BTL/ECO to EXT/ECO and vice versa if present in original_item."""
    mapping = {"BTL/ECO": "EXT/ECO", "EXT/ECO": "BTL/ECO"}

    for subj in original_item.get("subject", []):
        if subj.get("scheme") == "services-products":
            return mapping.get(subj.get("qcode"))
    return None


async def _preserve_eco_package(original_item, new_item):
    """Preserve and map ECO package subject from original_item to new_item using CV."""

    mapped_qcode = _map_eco_package_subject(original_item)

    if not mapped_qcode:
        return

    vocab_item = (await get_cv_by_qcode("services-products")).get(mapped_qcode)

    if not vocab_item:
        return

    # Remove all existing ECO-related services-products entries
    new_item["subject"] = [
        s
        for s in new_item.get("subject", [])
        if not (
            s.get("scheme") == "services-products"
            and s.get("qcode", "").endswith("/ECO")
        )
    ]
    new_item["subject"].append(vocab_item)


async def set_belga_keywords(item):
    """This field is used to set belga keyword field with the value "Brief" upon translation"""
    subjects = item.setdefault("subject", [])

    # check brief value is already exists in subjects
    brief_already_exists = any(
        subject
        for subject in subjects
        if subject["qcode"] == "BRIEF" and subject["scheme"] == "belga-keywords"
    )
    if brief_already_exists:
        return

    # get Belga keywords
    belga_keywords = await get_resource_service("vocabularies").find_one_async(
        req=None, _id="belga-keywords"
    )

    if not belga_keywords or not belga_keywords.get("items"):
        logger.warning("Belga keywords are not specified")
        return

    # get Brief value from Belga keywords
    brief = [
        keyword
        for keyword in belga_keywords["items"]
        if keyword.get("qcode") == "BRIEF"
    ]
    if brief:
        subjects.append(
            {
                "name": brief[0].get("name"),
                "qcode": brief[0].get("qcode"),
                "translations": brief[0].get("translations"),
                "scheme": "belga-keywords",
            }
        )

    return item


async def set_default_metadata_with_translate(item, **kwargs):
    """Replace some metadata from default content template and set translation id

    This macro is the same as "Set Default Metadata" + adding a translation
    link to original item.
    """
    archive_service = get_resource_service("archive")
    move_service = get_resource_service("move")
    original_item = await archive_service.find_one_async(None, _id=item["_id"])

    desk_id = kwargs.get("dest_desk_id")
    if not desk_id:
        logger.warning("no destination id specified")
        return
    stage_id = kwargs.get("dest_stage_id")
    if not stage_id:
        logger.warning("no stage id specified")
        return

    # SDBELGA-538
    if item.get("subject"):
        services_subjects = [
            s for s in item["subject"] if s.get("scheme") == "services-products"
        ]
        internal_destination = kwargs.get("internal_destination", {})
        content_filter_id = internal_destination.get("filter", "")
        content_filter_service = ContentFiltersResource.get_service()
        if content_filter_id:
            content_filter = await content_filter_service.find_by_id(content_filter_id)
        else:
            content_filter = None

        if content_filter:
            await PublishCache.init()
            for subject in services_subjects:
                temp_item = item.copy()
                # Generate a unique ID for the temporary item,
                # so result of checking temp item against the filter is not re-used in subsequent checks
                temp_item["item_id"] = generate_guid(type=GUID_TAG)
                temp_item["subject"] = [subject]

                if item_matches_content_filter(temp_item, content_filter):
                    # Use the first matching subject for translation
                    original_item["subject"] = [subject]
                    break
            else:
                raise StopDuplication()

    # we first do the translation, we need destination language for that
    content_template = await get_default_content_template(item, **kwargs)
    template_language = content_template["data"].get("language")
    if not template_language:
        logger.warning("no language set in default content template")
        new_id = await archive_service.duplicate_item(
            original_doc=original_item, operation=ITEM_DUPLICATE
        )
    elif template_language == original_item.get("language"):
        new_id = await archive_service.duplicate_item(
            original_doc=original_item, operation=ITEM_DUPLICATE
        )
    else:
        new_item = deepcopy(original_item)
        new_item["language"] = template_language
        translate_service = get_resource_service("translate")
        new_id = (await translate_service.create_async([new_item]))[0]

    # translation/duplication is done, we now move the item to the new desk
    dest = {"task": {"desk": desk_id, "stage": stage_id}}
    await move_service.move_content(new_id, dest)

    # and now we apply the update
    new_item = await archive_service.find_one_async(req=None, _id=new_id)

    # set overwrite_keywords to True to overwrite the keywords.
    if "overwrite_keywords" not in kwargs:
        kwargs["overwrite_keywords"] = False

    await set_default_metadata(new_item, **kwargs)

    # preserve original ECO package mapping
    await _preserve_eco_package(original_item, new_item)

    # untoggle coming up
    if new_item.get("extra", {}).get("DueBy"):
        del new_item["extra"]["DueBy"]

    # Set the "Belga Keywords" field with the value "Brief" upon translation
    await set_belga_keywords(new_item)

    # Change the correspondent author role to editor on translation
    await update_translation_metadata_macro(new_item)

    await archive_service.put_async(new_id, new_item)

    # no need for further treatment, we stop here internal_destinations workflow
    raise StopDuplication()


name = "Set Default Metadata With Translate"
label = name
callback = set_default_metadata_with_translate
access_type = "frontend"
action_type = "direct"
