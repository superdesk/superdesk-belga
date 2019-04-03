import superdesk
import json
from superdesk import get_resource_service


def import_contacts_via_file(path_file, unit_test=False):
    with open(path_file, 'rt', encoding='latin-1') as contacts_data:
        json_data = json.load(contacts_data)
        contact_service = get_resource_service('contacts')
        docs = []
        for item in json_data:
            if contact_service.find_one(req=None, original_id=item.get('contactId')) and unit_test is False:
                continue
            doc = {}
            # mapping data
            doc.setdefault('schema', {}).update({"is_active": True,
                                                 "public": item.get("belgaPublic", True)
                                                 })
            doc['organisation'] = item.get("company", "")
            doc['first_name'] = item.get("firstName", "")
            doc['last_name'] = item.get("lastName", "")
            doc['honorific'] = ""
            doc['job_title'] = item.get('function')
            if item.get('mobile247'):
                doc.setdefault('mobile', []).append({'number': item.get('mobile247'),
                                                     'usage': 'Business',
                                                     'public': True
                                                     })
            if item.get('personalMobile'):
                doc.setdefault('mobile', []).append({'number': item.get('personalMobile'),
                                                     'usage': 'Confidential',
                                                     'public': True
                                                     })
            if item.get('phoneGeneral'):
                doc.setdefault('contact_phone', []).append({'number': item.get('phoneGeneral'),
                                                            'usage': 'Business',
                                                            'public': True
                                                            })
            if item.get('directPhone1'):
                doc.setdefault('contact_phone', []).append({'number': item.get('directPhone1'),
                                                            'usage': 'Business',
                                                            'public': True
                                                            })
            if item.get('directPhone2'):
                doc.setdefault('contact_phone', []).append({'number': item.get('directPhone2'),
                                                            'usage': 'Business',
                                                            'public': True
                                                            })
            if item.get('personalPhone'):
                doc.setdefault('contact_phone', []).append({'number': item.get('personalPhone'),
                                                            'usage': 'Confidential',
                                                            'public': True
                                                            })
            doc['fax'] = ''
            if item.get('email1'):
                doc.setdefault('contact_email', []).append(item.get('email1'))
            if item.get('email2'):
                doc.setdefault('contact_email', []).append(item.get('personalEmail'))
            doc['twitter'] = item.get('twitter')
            doc['twitter_personal'] = item.get('personalTwitter')
            doc['facebook'] = item.get('facebook')
            doc['facebook_personal'] = item.get('personalFacebook')
            doc['instagram'] = None
            doc['website'] = item.get('url')
            if item.get('professionalAddress'):
                doc.setdefault('contact_address', []).append(item.get('professionalAddress'))
            if item.get('professionalAddress'):
                doc.setdefault('contact_address', []).append(item.get('personalAddress'))
            doc['locality'] = None
            doc['city'] = None
            doc['contact_state'] = None
            doc['postcode'] = None
            doc['country'] = None
            doc['notes'] = item.get('Comment1', '')
            doc['keywords'] = item.get('keywords')
            # use original_id check the contact exist
            doc['original_id'] = item.get('contactId')
            docs.append(doc)
        if docs:
            contact_service.post(docs)


class ContactImportCommand(superdesk.Command):
    """Prepopulate Superdesk using sample data.

    Useful for demo/development environment, but don't run in production,
    it's hard to get rid of such data later.
    """

    option_list = [
        superdesk.Option('--file', '-f', dest='contacts_file_path',
                         default='/home/thanhnguyen/workspace/0_test/contact/export.json'),
    ]

    def run(self, contacts_file_path, directory=None):
        import_contacts_via_file(contacts_file_path)


superdesk.command('contact:import', ContactImportCommand())
