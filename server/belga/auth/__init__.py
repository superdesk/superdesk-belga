# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from apps.auth import AuthResource

from apps.auth.service import AuthService
from superdesk import get_resource_service

from flask import g
from flask_oidc import OpenIDConnect
from superdesk.resource import Resource


class AuthResource(Resource):
    schema = {
        'token': {
            'type': 'string'
        },
        'user': Resource.rel('users', True)
    }
    resource_methods = ['POST']
    item_methods = ['GET', 'DELETE']
    public_methods = ['POST', 'DELETE']
    extra_response_fields = ['user', 'token', 'username']
    datasource = {'source': 'auth'}
    mongo_indexes = {'token': ([('token', 1)], {'background': True})}


def init_app(app):
    oidc = OpenIDConnect(app)
    endpoint_name = 'oidcauth'

    app.client_config['oidc_auth'] = False
    if app.config['OIDC_CLIENT_SECRETS']:
        app.client_config['oidc_auth'] = True
        url, realm = oidc.client_secrets['issuer'].split('/realms/')
        app.client_config['keycloak_config'] = {
            'url': url,
            'realm': realm,
            'clientId': app.config['OIDC_BROWSER_ID'],
            'redirectUri': app.config['OIDC_BROWSER_REDIRECT_URI']  # allow redirect uri configuable on client
        }

    class OIDCAuthService(AuthService):
        @oidc.accept_token(require_token=True, scopes_required=['openid'])
        def authenticate(self, credentials, ignore_expire=False):
            auth_service = get_resource_service('auth_users')
            users_service = get_resource_service('users')
            user = auth_service.find_one(req=None,
                                         username=g.oidc_token_info.get('username'))
            role = get_resource_service('roles').find_one(req=None,
                                                          name=g.oidc_token_info.get('role', {}))
            sync_data = {
                "email": g.oidc_token_info.get('email'),
                "first_name": g.oidc_token_info.get('given_name'),
                "last_name": g.oidc_token_info.get('family_name'),
                "needs_activation": False,
                "password": 'xxxxx',
                "user_type": g.oidc_token_info.get('user_type'),
                "username": g.oidc_token_info.get('username'),
                "role": role.get('_id') if role else None,
                "display_name": g.oidc_token_info.get('name'),
            }
            if not user:
                user_id = users_service.post([sync_data])[0]
                user = auth_service.find_one(req=None,
                                             _id=user_id)
            else:
                users_service.put(user.get('_id'), sync_data)
                user = auth_service.find_one(req=None,
                                             _id=user.get('_id'))
            user["oidc"] = g.oidc_token_info

            return user

    service = OIDCAuthService('auth', backend=superdesk.get_backend())
    AuthResource(endpoint_name, app=app, service=service)
