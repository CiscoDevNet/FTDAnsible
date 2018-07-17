# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json

from ansible.module_utils._text import to_text
from ansible.plugins.httpapi import HttpApiBase
from ansible.module_utils.six.moves.urllib.parse import urlencode

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

    def send_request(self, url_path, **message_kwargs):
        url = construct_url_path(url_path, message_kwargs.get('path_params'), message_kwargs.get('query_params'))
        data = json.dumps(message_kwargs['body_params']) if 'body_params' in message_kwargs else None
        response = self.connection.send(url, data, method=message_kwargs.get('http_method'), headers=self._authorized_headers()).read()
        return json.loads(to_text(response)) if response else response

    def _authorized_headers(self):
        headers = dict(BASE_HEADERS)
        headers['Authorization'] = 'Bearer %s' % self.access_token
        return headers


def construct_url_path(path, path_params=None, query_params=None):
    url = API_PREFIX + path
    if path_params:
        url = url.format(**path_params)
    if query_params:
        url += "?" + urlencode(query_params)
    return url
