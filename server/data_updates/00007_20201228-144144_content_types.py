# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : olegpshenichniy
# Creation: 2020-12-28 14:41

from copy import copy

from flask import current_app

from superdesk.commands.data_updates import BaseDataUpdate


class DataUpdate(BaseDataUpdate):

    resource = 'content_types'

    def __init__(self):
        super().__init__()

        self._resource_content_types = current_app.data.get_mongo_collection(self.resource)
        self._resource_content_templates = current_app.data.get_mongo_collection('content_templates')
        self._resource_desks = current_app.data.get_mongo_collection('desks')
        self._resource_archive = current_app.data.get_mongo_collection('archive')
        self._resource_published = current_app.data.get_mongo_collection('published')
        self._resource_archive_autosave = current_app.data.get_mongo_collection('archive_autosave')
        self._resource_archive_versions = current_app.data.get_mongo_collection('archive_versions')
        self._map_content_types_ids = {
            # replaceable_id: replacement_id
        }

    def forwards(self, mongodb_collection, mongodb_database):
        # fill content types mapping
        cursor = self._resource_content_types.find(
            {
                'label': {
                    '$in': ('ALERT custom', 'BRIEF custom', 'TEXT custom', 'TIP custom')
                }
            },
            {'_id': 1, 'label': 1}
        )
        for item in cursor:
            old_id = item['_id']
            new_id = item['label'].split(' custom')[0].lower()
            self._map_content_types_ids[old_id] = new_id

        # replace old `data.profile` id with new one in content templates
        for old_id, new_id in self._map_content_types_ids.items():
            print(f'Replace "{old_id}" with "{new_id}" in "content_templates.data.profile"')
            result = self._resource_content_templates.update_many(
                {'data.profile': str(old_id)},
                {'$set': {'data.profile': new_id}}
            )
            print('matched={} updated={}'.format(result.matched_count, result.modified_count))

        # replace old `default_content_profile` id with new one in desks
        for old_id, new_id in self._map_content_types_ids.items():
            print(f'Replace "{old_id}" with "{new_id}" in "desks.default_content_profile"')
            result = self._resource_desks.update_many(
                {'default_content_profile': str(old_id)},
                {'$set': {'default_content_profile': new_id}}
            )
            print('matched={} updated={}'.format(result.matched_count, result.modified_count))

        # replace old `profile` id with new one in archive
        for old_id, new_id in self._map_content_types_ids.items():
            print(f'Replace "{old_id}" with "{new_id}" in "archive.profile"')
            result = self._resource_archive.update_many(
                {
                    '$or': [
                        {'profile': str(old_id)},
                        {'profile': old_id}
                    ]
                },
                {'$set': {'profile': new_id}}
            )
            print('matched={} updated={}'.format(result.matched_count, result.modified_count))

        # replace old `profile` id with new one in (archive/published/archive_autosave).associations.*.profile

        # add the same ids but without ObjectID
        map_content_types_ids = copy(self._map_content_types_ids)
        map_content_types_ids.update({str(k): v for k, v in map_content_types_ids.items()})

        for resource, resource_name in ((self._resource_archive, 'archive'),
                                        (self._resource_published, 'published'),
                                        (self._resource_archive_versions, 'archive_versions'),
                                        (self._resource_archive_autosave, 'archive_autosave')):
            for item in resource.find({'associations': {'$exists': True}}):
                hitdb = False

                if not item['associations']:
                    continue

                for k, v in item['associations'].items():
                    if v and v.get('profile') in map_content_types_ids.keys():
                        old_id = v['profile']
                        new_id = map_content_types_ids[v['profile']]
                        item['associations'][k]['profile'] = map_content_types_ids[v['profile']]
                        hitdb = True
                        print(f'Item: {item["_id"]}. Replace "{old_id}" with "{new_id}" '
                              f'in "{resource_name}.associations.{k}.profile"')
                if not hitdb:
                    continue
                resource.update_one(
                    {'_id': item['_id']},
                    {'$set': {'associations': item['associations']}}
                )

        # remove old content types
        print(f'Remove "{self._map_content_types_ids.keys()}" from "content_types"')
        _filter = {
            '_id': {
                '$in': tuple(self._map_content_types_ids.keys())
            }
        }
        result = self._resource_content_types.delete_many(_filter)
        print(f'deleted={{{result.deleted_count}}}')

    def backwards(self, mongodb_collection, mongodb_database):
        raise NotImplementedError()
