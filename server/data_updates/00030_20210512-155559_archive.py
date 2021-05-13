# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : GyanP
# Creation: 2021-05-12 15:55

from superdesk.commands.data_updates import BaseDataUpdate
from superdesk import get_resource_service
from eve.utils import config


class DataUpdate(BaseDataUpdate):
    """Unmark published stories.

    Refer to https://dev.sourcefabric.org/browse/SDBELGA-512 for more information
    """

    resource = 'archive' # will use multiple resources, keeping this here so validation passes

    def forwards(self, mongodb_collection, mongodb_database):
        for resource in ["archive", "published"]:
            service = get_resource_service(resource)
            for doc in service.find({"marked_for_user": {"$exists": True}, "state": "published"}):
                if doc.get("marked_for_user"):
                    service.system_update(
                        doc.get(config.ID_FIELD),
                        {"marked_for_user": None, "previous_marked_user": doc["marked_for_user"]},
                        doc
                    )

    def backwards(self, mongodb_collection, mongodb_database):
        pass
