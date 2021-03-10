from bson import ObjectId
from superdesk import get_resource_service
from superdesk.tests import TestCase
from superdesk.errors import StopDuplication
from belga.macros.set_default_metadata_with_translate import set_default_metadata_with_translate


class SetDefaultMetadataWithTranslateTestCase(TestCase):

    def test_no_destination_data(self):
        item = {
            'headline': 'test headline',
            'slugine': 'test slugline',
            'keywords': ['foo', 'bar'],
        }
        self.app.data.insert(
            'archive',
            [item]
        )
        self.assertIsNone(set_default_metadata_with_translate(item))

    def test_no_template_language(self):
        self.app.data.insert(
            'desks',
            [{
                '_id': ObjectId('5d385f17fe985ec5e1a78b49'),
                'name': 'Politic Desk',
                'default_content_profile': 'belga_text',
                'default_content_template': 'content_template_1',
                'desk_language': 'fr',
                'source': 'politic'
            }]
        )
        self.app.data.insert(
            'stages',
            [{
                '_id': ObjectId('5d385f31fe985ec67a0ca583'),
                'name': 'Incoming Stage',
                'default_incoming': True,
                'desk_order': 2,
                'content_expiry': None,
                'working_stage': False,
                'is_visible': True,
                'desk': ObjectId('5d385f17fe985ec5e1a78b49')
            }]
        )
        self.app.data.insert(
            'content_templates',
            [{

                '_id': 'content_template_1',
                'template_name': 'belga text',
                'is_public': True,
                'data': {
                    'profile': 'belga_text',
                    'type': 'text',
                    'pubstatus': 'usable',
                    'format': 'HTML',
                    'headline': '',
                    'subject': [
                        {
                            'name': 'INT/GENERAL',
                            'qcode': 'INT/GENERAL',
                            'parent': 'INT',
                            'scheme': 'services-products'
                        },
                        {
                            'name': 'default',
                            'qcode': 'default',
                            'scheme': 'distribution'
                        },
                    ],
                    'keywords': [
                        'some',
                        'keyword'
                    ],
                    'body_html': ''
                },
                'template_type': 'create',
            }])
        item = {
            '_id': 'urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564',
            'guid': 'urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564',
            'headline': 'test headline',
            'slugine': 'test slugline',
            'state': 'published',
            'type': 'text',
            'keywords': ['foo', 'bar'],
        }
        self.app.data.insert(
            'archive',
            [item]
        )
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
            item,
            dest_desk_id=ObjectId('5d385f17fe985ec5e1a78b49'),
            dest_stage_id=ObjectId('5d385f31fe985ec67a0ca583')
        )
        archive_service = get_resource_service('archive')
        new_item = archive_service.find_one(
            req=None,
            original_id='urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564'
        )
        self.assertNotIn('translated_from', new_item)

    def test_duplicate(self):
        self.app.data.insert(
            'desks',
            [{
                '_id': ObjectId('5d385f17fe985ec5e1a78b49'),
                'name': 'Politic Desk',
                'default_content_profile': 'belga_text',
                'default_content_template': 'content_template_1',
                'desk_language': 'fr',
                'source': 'politic'
            }]
        )
        self.app.data.insert(
            'stages',
            [{
                '_id': ObjectId('5d385f31fe985ec67a0ca583'),
                'name': 'Incoming Stage',
                'default_incoming': True,
                'desk_order': 2,
                'content_expiry': None,
                'working_stage': False,
                'is_visible': True,
                'desk': ObjectId('5d385f17fe985ec5e1a78b49')
            }]
        )
        self.app.data.insert(
            'content_templates',
            [{

                '_id': 'content_template_1',
                'template_name': 'belga text',
                'is_public': True,
                'data': {
                    'profile': 'belga_text',
                    'type': 'text',
                    'pubstatus': 'usable',
                    'format': 'HTML',
                    'headline': '',
                    'subject': [
                        {
                            'name': 'INT/GENERAL',
                            'qcode': 'INT/GENERAL',
                            'parent': 'INT',
                            'scheme': 'services-products'
                        },
                        {
                            'name': 'default',
                            'qcode': 'default',
                            'scheme': 'distribution'
                        },
                    ],
                    'language': 'en',
                    'keywords': [
                        'some',
                        'keyword'
                    ],
                    'body_html': ''
                },
                'template_type': 'create',
            }])
        item = {
            '_id': 'urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564',
            'guid': 'urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564',
            'headline': 'test headline',
            'slugine': 'test slugline',
            'state': 'published',
            'type': 'text',
            'keywords': ['foo', 'bar'],
            'language': 'en'
        }
        self.app.data.insert(
            'archive',
            [item]
        )
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
            item,
            dest_desk_id=ObjectId('5d385f17fe985ec5e1a78b49'),
            dest_stage_id=ObjectId('5d385f31fe985ec67a0ca583')
        )

        archive_service = get_resource_service('archive')
        new_item = archive_service.find_one(
            req=None,
            original_id='urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564'
        )
        self.assertNotIn('translated_from', new_item)

    def test_translate(self):
        self.app.data.insert(
            'desks',
            [{
                '_id': ObjectId('5d385f17fe985ec5e1a78b49'),
                'name': 'Politic Desk',
                'default_content_profile': 'belga_text',
                'default_content_template': 'content_template_1',
                'desk_language': 'fr',
                'source': 'politic'
            }]
        )
        self.app.data.insert(
            'stages',
            [{
                '_id': ObjectId('5d385f31fe985ec67a0ca583'),
                'name': 'Incoming Stage',
                'default_incoming': True,
                'desk_order': 2,
                'content_expiry': None,
                'working_stage': False,
                'is_visible': True,

                'desk': ObjectId('5d385f17fe985ec5e1a78b49')
            }]
        )
        self.app.data.insert(
            'content_templates',
            [{

                '_id': 'content_template_1',
                'template_name': 'belga text',
                'is_public': True,
                'data': {
                    'profile': 'belga_text',
                    'type': 'text',
                    'pubstatus': 'usable',
                    'format': 'HTML',
                    'headline': '',
                    'subject': [
                        {
                            'name': 'INT/GENERAL',
                            'qcode': 'INT/GENERAL',
                            'parent': 'INT',
                            'scheme': 'services-products'
                        },
                        {
                            'name': 'default',
                            'qcode': 'default',
                            'scheme': 'distribution'
                        },
                    ],
                    'language': 'en',
                    'keywords': [
                        'some',
                        'keyword'
                    ],
                    'body_html': ''
                },
                'template_type': 'create',
            }])
        item = {
            '_id': 'urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564',
            'guid': 'urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564',
            'headline': 'test headline',
            'slugine': 'test slugline',
            'state': 'published',
            'type': 'text',
            'keywords': ['foo', 'bar'],
            'language': 'fr'
        }
        self.app.data.insert(
            'archive',
            [item]
        )
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
            item,
            dest_desk_id=ObjectId('5d385f17fe985ec5e1a78b49'),
            dest_stage_id=ObjectId('5d385f31fe985ec67a0ca583')
        )
        archive_service = get_resource_service('archive')
        new_item = archive_service.find_one(
            req=None,
            original_id='urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564'
        )
        self.assertEqual(
            new_item['translated_from'],
            item['guid']
        )

    def test_keywords_not_to_overwrite(self):
        self.app.data.insert(
            'desks',
            [{
                '_id': ObjectId('5d385f17fe985ec5e1a78b49'),
                'name': 'Politic Desk',
                'default_content_profile': 'belga_text',
                'default_content_template': 'content_template_1',
                'desk_language': 'fr',
                'source': 'politic'
            }]
        )
        self.app.data.insert(
            'stages',
            [{
                '_id': ObjectId('5d385f31fe985ec67a0ca583'),
                'name': 'Incoming Stage',
                'default_incoming': True,
                'desk_order': 2,
                'content_expiry': None,
                'working_stage': False,
                'is_visible': True,

                'desk': ObjectId('5d385f17fe985ec5e1a78b49')
            }]
        )
        self.app.data.insert(
            'content_templates',
            [{

                '_id': 'content_template_1',
                'template_name': 'belga text',
                'is_public': True,
                'data': {
                    'profile': 'belga_text',
                    'type': 'text',
                    'pubstatus': 'usable',
                    'format': 'HTML',
                    'headline': '',
                    'language': 'en',
                    'keywords': [
                        'some',
                        'keyword'
                    ],
                    'body_html': ''
                },
                'template_type': 'create',
            }])
        item = {
            '_id': 'urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564',
            'guid': 'urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564',
            'headline': 'test headline',
            'slugine': 'test slugline',
            'state': 'published',
            'type': 'text',
            'keywords': ['foo', 'bar'],
            'language': 'fr'
        }
        self.app.data.insert(
            'archive',
            [item]
        )
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
            item,
            dest_desk_id=ObjectId('5d385f17fe985ec5e1a78b49'),
            dest_stage_id=ObjectId('5d385f31fe985ec67a0ca583'),
            overwrite_keywords=False
        )
        archive_service = get_resource_service('archive')
        new_item = archive_service.find_one(
            req=None,
            original_id='urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564'
        )
        self.assertEqual(
            new_item['translated_from'],
            item['guid']
        )

        self.assertEqual(['foo', 'bar'], new_item['keywords'])

    def test_keywords_to_overwrite(self):
        self.app.data.insert(
            'desks',
            [{
                '_id': ObjectId('5d385f17fe985ec5e1a78b49'),
                'name': 'Politic Desk',
                'default_content_profile': 'belga_text',
                'default_content_template': 'content_template_1',
                'desk_language': 'fr',
                'source': 'politic'
            }]
        )
        self.app.data.insert(
            'stages',
            [{
                '_id': ObjectId('5d385f31fe985ec67a0ca583'),
                'name': 'Incoming Stage',
                'default_incoming': True,
                'desk_order': 2,
                'content_expiry': None,
                'working_stage': False,
                'is_visible': True,

                'desk': ObjectId('5d385f17fe985ec5e1a78b49')
            }]
        )
        self.app.data.insert(
            'content_templates',
            [{

                '_id': 'content_template_1',
                'template_name': 'belga text',
                'is_public': True,
                'data': {
                    'profile': 'belga_text',
                    'type': 'text',
                    'pubstatus': 'usable',
                    'format': 'HTML',
                    'headline': '',
                    'language': 'en',
                    'keywords': [
                        'some',
                        'keyword'
                    ],
                    'body_html': ''
                },
                'template_type': 'create',
            }])
        item = {
            '_id': 'urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564',
            'guid': 'urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564',
            'headline': 'test headline',
            'slugine': 'test slugline',
            'state': 'published',
            'type': 'text',
            'keywords': ['foo', 'bar'],
            'language': 'fr'
        }
        self.app.data.insert(
            'archive',
            [item]
        )
        self.assertRaises(
            StopDuplication,
            set_default_metadata_with_translate,
            item,
            dest_desk_id=ObjectId('5d385f17fe985ec5e1a78b49'),
            dest_stage_id=ObjectId('5d385f31fe985ec67a0ca583'),
            overwrite_keywords=True
        )
        archive_service = get_resource_service('archive')
        new_item = archive_service.find_one(
            req=None,
            original_id='urn:newsml:localhost:5000:2019-12-10T14:43:46.224107:d13ac5ae-7f43-4b7f-89a5-2c6835389564'
        )

        self.assertEqual(['some', 'keyword'], new_item['keywords'])
