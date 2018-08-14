# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os
import re
import shutil

from ansible.module_utils.basic import to_text
from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.plugins.httpapi import HttpApiBase
from urllib3 import encode_multipart_formdata
from urllib3.fields import RequestField
from ansible.module_utils.connection import ConnectionError


from module_utils.fdm_swagger_client import FdmSwaggerParser, OPERATIONS, MODELS
from module_utils.http import HTTPMethod

BASE_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
API_VERSION = "v1"
API_TOKEN_PATH = "/api/fdm/{version}/fdm/token"
API_SPEC_PATH = '/apispec/ngfw.json'

TOKEN_EXPIRATION_STATUS_CODE = 408
UNAUTHORIZED_STATUS_CODE = 401


class HttpApi(HttpApiBase):
    def __init__(self, connection):
        self.connection = connection
        self.access_token = False
        self.refresh_token = False
        self._api_spec = None

    def login(self, username, password):
        if self.refresh_token:
            payload = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
        elif username and password:
            payload = {
                'grant_type': 'password',
                'username': username,
                'password': password
            }
        else:
            raise AnsibleConnectionFailure(
                'Username and password are required for login in absence of refresh token'
            )

        _, response_data = self.connection.send(
            API_TOKEN_PATH.format(version=API_VERSION),
            json.dumps(payload), method=HTTPMethod.POST, headers=BASE_HEADERS
        )
        try:
            self._set_token_info(response_data)
        # JSONDecodeError only available on Python 3.5+
        except getattr(json.decoder, 'JSONDecodeError', ValueError) as e:
            raise ConnectionError('Invalid JSON response during connection authentication: %s' % e)

    def logout(self):
        auth_payload = {
            'grant_type': 'revoke_token',
            'access_token': self.access_token,
            'token_to_revoke': self.refresh_token
        }
        self.connection.send(
            API_TOKEN_PATH.format(version=API_VERSION),
            json.dumps(auth_payload), method=HTTPMethod.POST, headers=self._authorized_headers()
        )
        self.refresh_token = False
        self.access_token = False

    def update_auth(self, response, response_data):
        # With tokens, authentication should not be checked and updated on each request
        return None

    def send_request(self, url_path, http_method, body_params=None, path_params=None, query_params=None):
        url = construct_url_path(url_path, path_params, query_params)
        data = json.dumps(body_params) if body_params else None
        _, response_data = self.connection.send(
            url, data, method=http_method,
            headers=self._authorized_headers()
        )
        try:
            response_text = to_text(response_data.getvalue())
            return json.loads(response_text) if response_text else ''
        # JSONDecodeError only available on Python 3.5+
        except getattr(json.decoder, 'JSONDecodeError', ValueError):
            raise ConnectionError('Invalid JSON response: %s' % response_text)

    def upload_file(self, from_path, to_url):
        url = construct_url_path(to_url)
        with open(from_path, 'rb') as src_file:
            rf = RequestField('fileToUpload', src_file.read(), os.path.basename(src_file.name))
            rf.make_multipart()
            body, content_type = encode_multipart_formdata([rf])

            headers = self._authorized_headers()
            headers['Content-Type'] = content_type
            headers['Content-Length'] = len(body)

            response = self.connection.send(url, data=body, method=HTTPMethod.POST, headers=headers).read()
        return json.loads(to_text(response))

    def download_file(self, from_url, to_path):
        url = construct_url_path(from_url)
        response = self.connection.send(url, data=None, method=HTTPMethod.GET, headers=self._authorized_headers())

        if os.path.isdir(to_path):
            filename = extract_filename_from_headers(response.info())
            to_path = os.path.join(to_path, filename)

        with open(to_path, "wb") as output_file:
            shutil.copyfileobj(response, output_file)

    def handle_httperror(self, exc):
        # Called by connection plugin when it gets HTTP Error for a request.
        # Connection plugin will resend this request if we return true here.
        if exc.code == TOKEN_EXPIRATION_STATUS_CODE or exc.code == UNAUTHORIZED_STATUS_CODE:
            self.connection._auth = None
            self.login(self.connection.get_option('remote_user'), self.connection.get_option('password'))
            return True
        return False

    def _authorized_headers(self):
        headers = dict(BASE_HEADERS)
        headers['Authorization'] = 'Bearer %s' % self.access_token
        return headers

    def _set_token_info(self, response_data):
        token_info = json.loads(to_text(response_data.getvalue()))
        self.refresh_token = token_info['refresh_token']
        self.access_token = token_info['access_token']

    def get_operation_spec(self, operation_name):
        return self.api_spec[OPERATIONS].get(operation_name, None)

    def get_model_spec(self, model_name):
        return self.api_spec[MODELS].get(model_name, None)

    @property
    def api_spec(self):
        if self._api_spec is None:
            data = self.send_request(url_path=API_SPEC_PATH, http_method=HTTPMethod.GET)
            self._api_spec = FdmSwaggerParser().parse_spec(data)
        return self._api_spec


def construct_url_path(path, path_params=None, query_params=None):
    url = path
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
