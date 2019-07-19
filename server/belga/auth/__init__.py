# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from apps.auth import AuthResource
import superdesk
from flask_oidc import OpenIDConnect
from apps.auth.service import AuthService
from superdesk import get_resource_service
from flask import current_app as app, g

oidc = OpenIDConnect()


def init_app(app):
    oidc = OpenIDConnect(app)
    endpoint_name = 'oidcauth'
    service = OIDCAuthService('auth', backend=superdesk.get_backend())
    AuthResource(endpoint_name, app=app, service=service)


class OIDCAuthService(AuthService):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    def authenticate(self, credentials, ignore_expire=False):
        user = get_resource_service('auth_users').find_one(req=None, username=credentials.get('username'))
        user["oidc"] = g.oidc_token_info
        return user
