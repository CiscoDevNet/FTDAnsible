# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

import json
import os
import re
import shutil

from ansible.module_utils._text import to_text
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.plugins.httpapi import HttpApiBase
from six import wraps
from urllib3 import encode_multipart_formdata
from urllib3.fields import RequestField
from ansible.module_utils.connection import ConnectionError
import q

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
API_TOKEN_PATH = "/fdm/token"

TOKEN_EXPIRATION_STATUS_CODE = 408
UNAUTHORIZED_STATUS_CODE = 401


class HttpApi(HttpApiBase):
    def __init__(self, connection):
        self.connection = connection
        self.access_token = False
        self.refresh_token = False

    def login(self, username, password):
        if self.refresh_token:
            payload = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
        else:
            payload = {
                'grant_type': 'password',
                'username': username,
                'password': password
            }
        self.connection.send(
            API_PREFIX + API_TOKEN_PATH,
            json.dumps(payload), method='POST', headers=BASE_HEADERS
        )

    def send_request(self, url_path, http_method, body_params=None, path_params=None, query_params=None):
        url = construct_url_path(url_path, path_params, query_params)
        data = json.dumps(body_params) if body_params else None
        response, response_text = self.connection.send(
            url, data, method=http_method,
            headers=BASE_HEADERS
        )
        ret = json.loads(response_text) if response_text else response_text
        return ret

    def upload_file(self, from_path, to_url):
        url = construct_url_path(to_url)
        with open(from_path, 'rb') as src_file:
            rf = RequestField('fileToUpload', src_file.read(), os.path.basename(src_file.name))
            rf.make_multipart()
            body, content_type = encode_multipart_formdata([rf])
            headers = BASE_HEADERS
            headers['Content-Type'] = content_type
            headers['Content-Length'] = len(body)
            response, response_text = self.connection.send(url, data=body, method='POST', headers=headers)
        return json.loads(response_text)

    def download_file(self, from_url, to_path):
        url = construct_url_path(from_url)
        q(url)
        response, response_text = self.connection.send(
            url, data=None, method='GET',
            headers=BASE_HEADERS
        )
        if os.path.isdir(to_path):
            filename = extract_filename_from_headers(response.info())
            to_path = os.path.join(to_path, filename)

        with open(to_path, "wb") as output_file:
            output_file.write(response_text)

    def update_auth(self, response, response_text):
        q(response_text)
        if response_text:
            token_info = json.loads(to_text(response_text))
            if 'refresh_token' in token_info:
                self.refresh_token = token_info['refresh_token']
            if 'access_token' in token_info:
                self.access_token = token_info['access_token']
                return {'Authorization': 'Bearer %s' % token_info['access_token']}
        return None

    def logout(self):
        # Revoke the tokens
        auth_payload = {
            'grant_type': 'revoke_token',
            'access_token': self.access_token,
            'token_to_revoke': self.refresh_token
        }
        self.connection.send(
            API_PREFIX + API_TOKEN_PATH + 'junk', json.dumps(auth_payload),
            method='POST', headers=BASE_HEADERS
        )
        # HTTP error would cause exception Connection failure in connection
        # plugin
        self.refresh_token = False
        self.access_token = False
        display.vvvv("logged out successfully")


def construct_url_path(path, path_params=None, query_params=None):
    url = API_PREFIX + path
    if path_params:
        url = url.format(**path_params)
    if query_params:
        url += "?" + urlencode(query_params)
    return url


def extract_filename_from_headers(response_info):
    content_header_regex = r'attachment; ?filename="?([^"]+)'
    match = re.match(content_header_regex, response_info.get('Content-Disposition'))
    if match:
        return match.group(1)
    else:
        raise ValueError("No appropriate Content-Disposition header is specified.")
