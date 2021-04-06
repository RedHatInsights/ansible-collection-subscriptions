#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback
from oauthlib.oauth2 import Client
from requests_oauthlib import OAuth2Session

class RedHatAPIClient:

    def __init__(self, module):
        self.module = module
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
        self.session = OAuth2Session(module.params['refresh_token_client'], token=self.token, auto_refresh_url=self.sso_token_url,
                                     auto_refresh_kwargs=extra, token_updater=self._save_token)

    def _build_url(self, path):
        if path[0] == '/':
            path = path[1:]
        return '%s/%s' % (self.base_url, path)

    def _save_token(self, token):
        self.token=token

    def request(self, method, path, data=None):
        url = self._build_url(path)
        return self.session.request(method, url, json=data, timeout=self.timeout)

    def get(self, path, data=None):
        return self.request('GET', path, data)

    def put(self, path, data=None):
        return self.request('PUT', path, data)

    def post(self, path, data=None):
        return self.request('POST', path, data)

    def delete(self, path, data=None):
        return self.request('DELETE', path, data)