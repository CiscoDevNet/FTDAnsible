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
API_TOKEN_PATH_ENV_VAR = 'FTD_API_TOKEN_PATH'
DEFAULT_API_TOKEN_PATH = '/api/fdm/v2/fdm/token'
API_SPEC_PATH = '/apispec/ngfw.json'

TOKEN_EXPIRATION_STATUS_CODE = 408
UNAUTHORIZED_STATUS_CODE = 401


class HttpApi(HttpApiBase):
    def __init__(self, connection):
        self.connection = connection
        self.access_token = None
        self.refresh_token = None
        self._api_spec = None

    def login(self, username, password):
        def request_token_payload(username, password):
            return {
                'grant_type': 'password',
                'username': username,
                'password': password
            }

        def refresh_token_payload(refresh_token):
            return {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }

        if self.refresh_token:
            payload = refresh_token_payload(self.refresh_token)
        elif username and password:
            payload = request_token_payload(username, password)
        else:
            raise AnsibleConnectionFailure('Username and password are required for login in absence of refresh token')

        _, response_data = self.connection.send(
            self._get_api_token_path(), json.dumps(payload), method=HTTPMethod.POST, headers=BASE_HEADERS
        )
        response_text = to_text(response_data.getvalue())

        try:
            token_info = json.loads(response_text)
            self.refresh_token = token_info['refresh_token']
            self.access_token = token_info['access_token']
        # JSONDecodeError only available on Python 3.5+
        except (getattr(json.decoder, 'JSONDecodeError', ValueError), KeyError):
            raise ConnectionError('Invalid JSON response during connection authentication: %s' % response_text)

    def logout(self):
        auth_payload = {
            'grant_type': 'revoke_token',
            'access_token': self.access_token,
            'token_to_revoke': self.refresh_token
        }
        self.connection.send(
            self._get_api_token_path(), json.dumps(auth_payload), method=HTTPMethod.POST,
            headers=self._authorized_headers()
        )
        self.refresh_token = None
        self.access_token = None

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

            _, response_data = self.connection.send(url, data=body, method=HTTPMethod.POST, headers=headers)
        try:
            response_text = to_text(response_data.getvalue())
            return json.loads(response_text)
        # JSONDecodeError only available on Python 3.5+
        except getattr(json.decoder, 'JSONDecodeError', ValueError):
            raise ConnectionError('Invalid JSON response after uploading the file: %s' % response_text)

    def download_file(self, from_url, to_path):
        url = construct_url_path(from_url)
        response, response_data = self.connection.send(
            url, data=None, method=HTTPMethod.GET,
            headers=self._authorized_headers()
        )

        if os.path.isdir(to_path):
            filename = extract_filename_from_headers(response.info())
            to_path = os.path.join(to_path, filename)

        with open(to_path, "wb") as output_file:
            shutil.copyfileobj(response_data, output_file)

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

    @staticmethod
    def _get_api_token_path():
        return os.environ.get(API_TOKEN_PATH_ENV_VAR, DEFAULT_API_TOKEN_PATH)

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
