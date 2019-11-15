# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2019 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os.path
from superdesk.macros import load_macros


macros_folder = os.path.realpath(os.path.dirname(__file__))
load_macros(macros_folder, package_prefix="belga.macros")

