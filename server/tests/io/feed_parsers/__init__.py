import belga # noqa
import os
from superdesk.tests import TestCase
from apps.prepopulate.app_populate import AppPopulateCommand


class BelgaTestCase(TestCase):

    def setUp(self):
        # we need to prepopulate vocabularies to get qcodes
        voc_file = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(belga.__file__))),
                                'data', 'vocabularies.json')
        AppPopulateCommand().run(voc_file)
