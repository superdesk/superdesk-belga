# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : olegpshenichniy
# Creation: 2020-01-03 12:58

from superdesk.commands.data_updates import DataUpdate


class DataUpdate(DataUpdate):

    resource = 'vocabularies'

    def forwards(self, mongodb_collection, mongodb_database):
        mongodb_collection.update(
            {
                '_id': 'keywords'
            },
            {
                '$unset': {'service': ''}
            }
        )

    def backwards(self, mongodb_collection, mongodb_database):
        pass
