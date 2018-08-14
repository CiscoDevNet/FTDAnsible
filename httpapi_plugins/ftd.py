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

from module_utils.fdm_swagger_client import FdmSwaggerParser, OPERATIONS, MODELS
from module_utils.http import HTTPMethod

BASE_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
API_VERSION = "v2"
API_TOKEN_PATH = "/api/fdm/{version}/fdm/token"
API_SPEC_PATH = '/apispec/ngfw.json'

TOKEN_EXPIRATION_STATUS_CODE = 408
UNAUTHORIZED_STATUS_CODE = 401


def retry_on_token_expiration(func):
    @wraps(func)
    def f_retry(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except HTTPError as e:
            if e.code == TOKEN_EXPIRATION_STATUS_CODE or e.code == UNAUTHORIZED_STATUS_CODE:
                self._refresh_token()
                return func(self, *args, **kwargs)
            else:
                raise e

    return f_retry


class HttpApi(HttpApiBase):
    def __init__(self, connection):
        self.connection = connection
        self.access_token = False
        self.refresh_token = False
        self._api_spec = None

    def login(self, username, password):
        auth_payload = {
            'grant_type': 'password',
            'username': username,
            'password': password
        }
        response = self.connection.send(API_TOKEN_PATH.format(version=API_VERSION), json.dumps(auth_payload),
                                        method=HTTPMethod.POST, headers=BASE_HEADERS)
        self._set_token_info(response)

    @retry_on_token_expiration
    def send_request(self, url_path, http_method, body_params=None, path_params=None, query_params=None):
        url = construct_url_path(url_path, path_params, query_params)
        data = json.dumps(body_params) if body_params else None
        response = self.connection.send(url, data, method=http_method, headers=self._authorized_headers()).read()
        return json.loads(to_text(response)) if response else ''

    @retry_on_token_expiration
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

    @retry_on_token_expiration
    def download_file(self, from_url, to_path):
        url = construct_url_path(from_url)
        response = self.connection.send(url, data=None, method=HTTPMethod.GET, headers=self._authorized_headers())

        if os.path.isdir(to_path):
            filename = extract_filename_from_headers(response.info())
            to_path = os.path.join(to_path, filename)

        with open(to_path, "wb") as output_file:
            shutil.copyfileobj(response, output_file)

    def _authorized_headers(self):
        headers = dict(BASE_HEADERS)
        headers['Authorization'] = 'Bearer %s' % self.access_token
        return headers

    def _refresh_token(self):
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        response = self.connection.send(API_TOKEN_PATH.format(version=API_VERSION), json.dumps(payload),
                                        method=HTTPMethod.POST, headers=BASE_HEADERS)
        self._set_token_info(response)

    def _set_token_info(self, token_response):
        token_info = json.loads(to_text(token_response.read()))
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
