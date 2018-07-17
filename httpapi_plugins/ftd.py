# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json

from ansible.module_utils._text import to_text
from ansible.plugins.httpapi import HttpApiBase

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

BASE_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
API_PREFIX = "/api/fdm/v2"


class HttpApi(HttpApiBase):
    def __init__(self, connection):
        self.connection = connection
        self.access_token = False
        self.refresh_token = False

    def login(self, username, password):
        auth_payload = {
            'grant_type': 'password',
            'username': username,
            'password': password
        }
        response = self.connection.send(API_PREFIX + "/fdm/token", json.dumps(auth_payload), method='POST', headers=BASE_HEADERS)
        content = json.loads(to_text(response.read()))

        self.refresh_token = content['refresh_token']
        self.access_token = content['access_token']

    def send_request(self, **message_kwargs):
        return self.connection.send(message_kwargs['url'], message_kwargs['data'], method=message_kwargs['http_method'],
                                    headers=self._authorized_headers()).read()

    def _authorized_headers(self):
        headers = dict(BASE_HEADERS)
        headers['Authorization'] = 'Bearer %s' % self.access_token
        return headers
