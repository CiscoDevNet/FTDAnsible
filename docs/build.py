import argparse
import json
import os
import shutil
from http import HTTPStatus
from urllib import error as urllib_error

from ansible.module_utils._text import to_text
from ansible.module_utils.urls import open_url

from docs.enricher import ApiSpecAutocomplete
from docs.generator import ModelDocGenerator, OperationDocGenerator, ModuleDocGenerator, StaticDocGenerator
from httpapi_plugins.ftd import BASE_HEADERS
from module_utils.common import HTTPMethod
from module_utils.fdm_swagger_client import FdmSwaggerParser, SpecProp, OperationField

BASE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DEFAULT_TEMPLATE_DIR = os.path.join(BASE_DIR_PATH, 'templates')
STATIC_TEMPLATE_DIR = os.path.join(DEFAULT_TEMPLATE_DIR, 'static')
DEFAULT_SAMPLES_DIR = os.path.join(os.path.dirname(BASE_DIR_PATH), 'samples')
DEFAULT_DIST_DIR = os.path.join(BASE_DIR_PATH, 'dist')
DEFAULT_MODULE_DIR = os.path.join(os.path.dirname(BASE_DIR_PATH), 'library')


class FtdApiClient(object):
    SUPPORTED_VERSIONS = ['v2', 'v1']
    TOKEN_PATH_TEMPLATE = '/api/fdm/{}/fdm/token'

    SPEC_PATH = '/apispec/ngfw.json'
    DOC_PATH = '/apispec/en-us/doc.json'

    def __init__(self, hostname, username, password):
        self._hostname = hostname
        token_info = self._authorize(username, password)
        self._auth_headers = self._construct_auth_headers(token_info)

    def _authorize(self, username, password):
        def request_token(url):
            resp = open_url(
                url,
                method=HTTPMethod.POST,
                data=json.dumps({'grant_type': 'password', 'username': username, 'password': password}),
                headers=BASE_HEADERS,
                validate_certs=False
            ).read()
            return json.loads(to_text(resp))

        for version in self.SUPPORTED_VERSIONS:
            token_url = self._hostname + self.TOKEN_PATH_TEMPLATE.format(version)
            try:
                token = request_token(token_url)
            except urllib_error.HTTPError as e:
                if e.code != HTTPStatus.UNAUTHORIZED:
                    raise
            else:
                return token

    @staticmethod
    def _construct_auth_headers(token_info):
        headers = dict(BASE_HEADERS)
        headers['Authorization'] = 'Bearer %s' % token_info['access_token']
        return headers

    def fetch_api_specs(self):
        spec = self._send_request(self.SPEC_PATH, HTTPMethod.GET)
        doc = self._send_request(self.DOC_PATH, HTTPMethod.GET)
        return FdmSwaggerParser().parse_spec(spec, doc)

    def fetch_ftd_version(self, spec):
        operation = spec[SpecProp.OPERATIONS]['getSystemInformation']
        url_path = operation[OperationField.URL].format(objId='default')

        system_info = self._send_request(url_path, operation[OperationField.METHOD])

        build_version = system_info['softwareVersion']
        ftd_version = build_version.split('-')[0]
        return ftd_version

    def _send_request(self, url_path, method):
        url = self._hostname + url_path
        response = open_url(url, method=method, headers=self._auth_headers, validate_certs=False).read()
        return json.loads(to_text(response))


def main():
    def clean_dist_dir():
        if os.path.exists(args.dist):
            shutil.rmtree(args.dist)

    parser = argparse.ArgumentParser(description='Generates Ansible modules from Swagger documentation')
    parser.add_argument('hostname', type=str, help='Hostname where FTD can be accessed')
    parser.add_argument('username', type=str, help='FTD username that has access to Swagger docs')
    parser.add_argument('password', type=str, help='Password for the username')
    parser.add_argument('--models', type=str, nargs='+', help='A list of models to include in the docs', required=False)
    parser.add_argument('--dist', type=str, help='An output directory for distribution files', required=False,
                        default=DEFAULT_DIST_DIR)
    args = parser.parse_args()

    api_client = FtdApiClient(args.hostname, args.username, args.password)
    api_spec = api_client.fetch_api_specs()
    spec_autocomplete = ApiSpecAutocomplete(api_spec)
    spec_autocomplete.lookup_and_complete()

    clean_dist_dir()

    template_ctx = dict(ftd_version=api_client.fetch_ftd_version(api_spec), sample_dir=DEFAULT_SAMPLES_DIR)
    ModelDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, api_spec).generate_doc_files(args.dist, args.models)
    OperationDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, api_spec).generate_doc_files(args.dist, args.models)
    ModuleDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, DEFAULT_MODULE_DIR).generate_doc_files(args.dist)
    StaticDocGenerator(STATIC_TEMPLATE_DIR, template_ctx).generate_doc_files(args.dist)


if __name__ == '__main__':
    main()
