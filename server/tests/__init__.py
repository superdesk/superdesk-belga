import os

from superdesk.tests import TestCase as CoreTestCase
from apps.prepopulate.app_populate import AppPopulateCommand

import belga  # noqa


class TestCase(CoreTestCase):
    def setUp(self):
        # we need to prepopulate vocabularies to get qcodes
        voc_file = os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(belga.__file__))),
            "data",
            "vocabularies.json",
        )
        AppPopulateCommand().run(voc_file)

    def setUpForChildren(self):
        super().setUpForChildren()

        # belga related configs
        self.app.config["OUTPUT_BELGA_URN_SUFFIX"] = "tst"
