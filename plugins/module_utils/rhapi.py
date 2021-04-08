#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import traceback

try:
    from requests_oauthlib import OAuth2Session
    from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
    HAS_REQUESTS_OAUTH = True
except ImportError:
    HAS_REQUESTS_OAUTH = False

class RedHatAPIClient:

    def __init__(self, module):
        self.module = module

        if not HAS_REQUESTS_OAUTH:
            module.fail_json(msg="This module requires the python 'requests-oauthlib' package. Try `pip install requests-oauthlib`.")

        self.base_url = os.getenv('RHSMAPI_BASE_URL', 'https://api.access.redhat.com/management/v1')
        self.sso_token_url = os.getenv('RHSMAPI_TOKEN_URL', 'https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token')
        self.timeout = 30
        self.token = {
            'refresh_token': module.params['refresh_token'],
            'access_token': 'xxx',
            'token_type': 'Bearer',
            'expires_in': '-1',
        }
        extra = {'client_id': module.params['refresh_token_client']}

        try:
            self.session = OAuth2Session(module.params['refresh_token_client'], token=self.token, auto_refresh_url=self.sso_token_url,
                                        auto_refresh_kwargs=extra, token_updater=self._save_token)
        except InvalidGrantError:
            module.fail_json(msg='Invalid refresh token provided', exception=traceback.format_exc())


    def _build_url(self, path):
        if path[0] == '/':
            path = path[1:]
        return '%s/%s' % (self.base_url, path)

    def _save_token(self, token):
        self.token=token

    def request(self, method, path, data=None):
        url = self._build_url(path)
        try:
            response = self.session.request(method, url, json=data, timeout=self.timeout)
        except InvalidGrantError:
            self.module.fail_json(msg='Invalid refresh token provided', exception=traceback.format_exc())
        return response

    def get(self, path, data=None):
        return self.request('GET', path, data)

    def put(self, path, data=None):
        return self.request('PUT', path, data)

    def post(self, path, data=None):
        return self.request('POST', path, data)

    def delete(self, path, data=None):
        return self.request('DELETE', path, data)
