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

from httpapi_plugins.helper import equal_objects

BASE_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
API_PREFIX = "/api/fdm/v2"
API_TOKEN_PATH = "/fdm/token"

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

    def login(self, username, password):
        auth_payload = {
            'grant_type': 'password',
            'username': username,
            'password': password
        }
        response = self.connection.send(API_PREFIX + API_TOKEN_PATH, json.dumps(auth_payload), method='POST',
                                        headers=BASE_HEADERS)
        self._set_token_info(response)

    @retry_on_token_expiration
    def send_request(self, url_path, http_method, body_params=None, path_params=None, query_params=None):
        url = construct_url_path(url_path, path_params, query_params)
        data = json.dumps(body_params) if body_params else None
        response = self.connection.send(url, data, method=http_method, headers=self._authorized_headers()).read()
        return json.loads(to_text(response)) if response else ''

    @retry_on_token_expiration
    def delete_object(self, url_path, path_params):
        def is_invalid_uuid_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to an invalid UUID" in err_msg

        try:
            resp = self.send_request(url_path=url_path, http_method='DELETE', path_params=path_params)
            return {'changed': True, 'response': resp}
        except HTTPError as e:
            if is_invalid_uuid_error(e):
                return {'changed': False, 'response': 'Referenced object does not exist'}
            else:
                raise e

    @retry_on_token_expiration
    def update_object(self, url_path, body_params, path_params):
        existing_object = self.send_request(url_path=url_path, http_method='GET', path_params=path_params)

        if not existing_object:
            raise ValueError('Referenced object does not exist')
        elif equal_objects(existing_object, body_params):
            return {'changed': False, 'response': 'Referenced object is already updated'}
        else:
            resp = self.send_request(url_path=url_path, http_method='PUT', body_params=body_params, path_params=path_params)
            return {'changed': True, 'response': resp}

    @retry_on_token_expiration
    def add_object(self, url_path, body_params, path_params=None, query_params=None):
        def find_existing_object():
            object_name = body_params['name']
            if not object_name:
                raise Exception('New object cannot be added without name. The name field is mandatory for new objects.')

            result = self.send_request(url_path=url_path, http_method='GET', path_params=path_params,
                                       query_params={'filter': 'name:%s' % object_name})
            return next((i for i in result['items'] if i['name'] == object_name), None)

        existing_obj = find_existing_object()
        if not existing_obj:
            resp = self.send_request(url_path=url_path, http_method='POST', body_params=body_params,
                                     path_params=path_params, query_params=query_params)
            return {'changed': True, 'response': resp}
        elif equal_objects(existing_obj, body_params):
            return {'changed': False, 'response': existing_obj}
        else:
            raise Exception('Cannot add new object. An object with the same name but different parameters already exists.')

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

            response = self.connection.send(url, data=body, method='POST', headers=headers).read()
        return json.loads(to_text(response))

    @retry_on_token_expiration
    def download_file(self, from_url, to_path):
        url = construct_url_path(from_url)
        response = self.connection.send(url, data=None, method='GET', headers=self._authorized_headers())

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
        response = self.connection.send(API_PREFIX + API_TOKEN_PATH, json.dumps(payload), method='POST', headers=BASE_HEADERS)
        self._set_token_info(response)

    def _set_token_info(self, token_response):
        token_info = json.loads(to_text(token_response.read()))
        self.refresh_token = token_info['refresh_token']
        self.access_token = token_info['access_token']


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
