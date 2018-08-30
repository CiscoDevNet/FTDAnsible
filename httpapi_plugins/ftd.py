# Copyright (c) 2018 Cisco and/or its affiliates.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
import os
import re

from ansible.module_utils.basic import to_text
from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.plugins.httpapi import HttpApiBase
from urllib3 import encode_multipart_formdata
from urllib3.fields import RequestField
from ansible.module_utils.connection import ConnectionError

from module_utils.fdm_swagger_client import FdmSwaggerParser, SpecProp, FdmSwaggerValidator
from module_utils.common import HTTPMethod, ResponseParams

BASE_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
API_TOKEN_PATH_ENV_VAR = 'FTD_API_TOKEN_PATH'
DEFAULT_API_TOKEN_PATH = '/api/fdm/v2/fdm/token'
API_SPEC_PATH = '/apispec/ngfw.json'

TOKEN_EXPIRATION_STATUS_CODE = 408
UNAUTHORIZED_STATUS_CODE = 401

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class HttpApi(HttpApiBase):
    def __init__(self, connection):
        self.connection = connection
        self.access_token = None
        self.refresh_token = None
        self._api_spec = None
        self._api_validator = None

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

        dummy, response_data = self.connection.send(
            self._get_api_token_path(), json.dumps(payload), method=HTTPMethod.POST, headers=BASE_HEADERS
        )
        response = self._response_to_json(response_data.getvalue())

        try:
            self.refresh_token = response['refresh_token']
            self.access_token = response['access_token']
        except KeyError:
            raise ConnectionError(
                'Server returned response without token info during connection authentication: %s' % response)

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
        try:
            self._display(http_method, 'url', url)
            if data:
                self._display(http_method, 'data', data)

            response, response_data = self.connection.send(
                url, data, method=http_method,
                headers=self._authorized_headers()
            )

            value = response_data.getvalue()
            self._display(http_method, 'response', value)

            return {
                ResponseParams.SUCCESS: True,
                ResponseParams.STATUS_CODE: response.getcode(),
                ResponseParams.RESPONSE: self._response_to_json(value)
            }
        # Being invoked via JSON-RPC, this method does not serialize and pass HTTPError correctly to the method caller.
        # Thus, in order to handle non-200 responses, we need to wrap them into a simple structure and pass explicitly.
        except HTTPError as e:
            read = e.read()
            self._display(http_method, 'error', read)
            return {
                ResponseParams.SUCCESS: False,
                ResponseParams.STATUS_CODE: e.code,
                ResponseParams.RESPONSE: self._response_to_json(read)
            }

    def upload_file(self, from_path, to_url):
        url = construct_url_path(to_url)
        request_type = 'upload'
        self._display(request_type, 'url', url)
        with open(from_path, 'rb') as src_file:
            rf = RequestField('fileToUpload', src_file.read(), os.path.basename(src_file.name))
            rf.make_multipart()
            body, content_type = encode_multipart_formdata([rf])

            headers = self._authorized_headers()
            headers['Content-Type'] = content_type
            headers['Content-Length'] = len(body)

            dummy, response_data = self.connection.send(url, data=body, method=HTTPMethod.POST, headers=headers)
            value = response_data.getvalue()
            self._display(request_type, 'response', value)
            return self._response_to_json(value)

    def download_file(self, from_url, to_path, path_params=None):
        url = construct_url_path(from_url, path_params=path_params)
        request_type = 'download'
        self._display(request_type, 'url', url)
        response, response_data = self.connection.send(
            url, data=None, method=HTTPMethod.GET,
            headers=self._authorized_headers()
        )

        if os.path.isdir(to_path):
            filename = extract_filename_from_headers(response.info())
            to_path = os.path.join(to_path, filename)

        with open(to_path, "wb") as output_file:
            output_file.write(response_data.getvalue())

    def handle_httperror(self, exc):
        if exc.code == TOKEN_EXPIRATION_STATUS_CODE or exc.code == UNAUTHORIZED_STATUS_CODE:
            self.connection._auth = None
            self.login(self.connection.get_option('remote_user'), self.connection.get_option('password'))
            return True
        # None means that the exception will be passed further to the caller
        return None

    def _authorized_headers(self):
        headers = dict(BASE_HEADERS)
        headers['Authorization'] = 'Bearer %s' % self.access_token
        return headers

    def _display(self, http_method, title, msg=''):
        if display.verbosity > 2:
            display.vvv('REST:{0}:{1}:{2}\n{3}'.format(http_method, self.connection._url, title, to_text(msg)))

    @staticmethod
    def _get_api_token_path():
        return os.environ.get(API_TOKEN_PATH_ENV_VAR, DEFAULT_API_TOKEN_PATH)

    @staticmethod
    def _response_to_json(response_data):
        response_text = to_text(response_data)
        try:
            return json.loads(response_text) if response_text else {}
        # JSONDecodeError only available on Python 3.5+
        except getattr(json.decoder, 'JSONDecodeError', ValueError):
            raise ConnectionError('Invalid JSON response: %s' % response_text)

    def get_operation_spec(self, operation_name):
        return self.api_spec[SpecProp.OPERATIONS].get(operation_name, None)

    def get_model_spec(self, model_name):
        return self.api_spec[SpecProp.MODELS].get(model_name, None)

    def validate_data(self, operation_name, data):
        return self.api_validator.validate_data(operation_name, data)

    def validate_query_params(self, operation_name, params):
        return self.api_validator.validate_query_params(operation_name, params)

    def validate_path_params(self, operation_name, params):
        return self.api_validator.validate_path_params(operation_name, params)

    @property
    def api_spec(self):
        if self._api_spec is None:
            response = self.send_request(url_path=API_SPEC_PATH, http_method=HTTPMethod.GET)
            if response[ResponseParams.SUCCESS]:
                self._api_spec = FdmSwaggerParser().parse_spec(response[ResponseParams.RESPONSE])
            else:
                raise ConnectionError('Failed to download API specification. Status code: %s. Response: %s' % (
                    response[ResponseParams.STATUS_CODE], response[ResponseParams.RESPONSE]))
        return self._api_spec

    @property
    def api_validator(self):
        if self._api_validator is None:
            self._api_validator = FdmSwaggerValidator(self.api_spec)
        return self._api_validator


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
