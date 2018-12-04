import argparse
import json
import os
import shutil
from enum import Enum
from http import HTTPStatus
from urllib import error as urllib_error

from ansible.module_utils._text import to_text
from ansible.module_utils.urls import open_url

from docs.enricher import ApiSpecAutocomplete
from docs.generator import ModelDocGenerator, OperationDocGenerator, ModuleDocGenerator, StaticDocGenerator, \
    ResourceDocGenerator, ResourceModelDocGenerator, ErrorsDocGenerator, APIIntroductionDocGenerator
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
    """
    A client that helps to interact with FTD device and takes care of authentication
    and token-related aspects.
    """

    SUPPORTED_VERSIONS = ['v2', 'v1']
    TOKEN_PATH_TEMPLATE = '/api/fdm/{}/fdm/token'

    SPEC_PATH = '/apispec/ngfw.json'
    DOC_PATH = '/apispec/en-us/doc.json'
    ERRORS_PATH = '/apispec/customErrorCode.json'

    def __init__(self, hostname, username, password):
        self._hostname = hostname
        token_info = self._authorize(username, password)
        self._api_version = None
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
                self._api_version = version
                return token

    def get_api_version(self):
        return self._api_version

    @staticmethod
    def _construct_auth_headers(token_info):
        headers = dict(BASE_HEADERS)
        headers['Authorization'] = 'Bearer %s' % token_info['access_token']
        return headers

    def fetch_api_specs(self):
        """
        Downloads an API specification for FTD device, parses it, and enriches with documentation.

        :return: a documented API specification containing operation and model definitions for FTD device
        :rtype: dict
        """
        spec = self._send_request(self.SPEC_PATH, HTTPMethod.GET)
        doc = self._send_request(self.DOC_PATH, HTTPMethod.GET)
        return FdmSwaggerParser().parse_spec(spec, doc)

    def fetch_error_codes(self):
        """
        Downloads an API Error codes specification for FTD device.

        :return: a documented API specification containing error codes definitions for FTD device
        :rtype: dict
        """
        spec = self._send_request(self.ERRORS_PATH, HTTPMethod.GET)
        return spec

    def fetch_ftd_version(self, spec):
        """
        Fetches FTD software version currently installed on the device.

        :param spec: an API specification for FTD device
        :type spec: dict
        :return: an FTD version being deployed on the device
        :rtype: str
        """
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


class DocType(Enum):
    """
    Defines documentation type: `ftd_ansible` stands for docs describing FTD Ansible modules,
    `ftd_api` corresponds to docs containing HTTP API endpoints with urls, methods, etc.
    """
    ftd_ansible = 'ftd-ansible'
    ftd_api = 'ftd-api'


def main():
    def parse_args():
        parser = argparse.ArgumentParser(description='Generates docs for FTD based on Swagger documentation')
        parser.add_argument('hostname', type=str, help='Hostname where FTD can be accessed')
        parser.add_argument('username', type=str, help='FTD username that has access to Swagger docs')
        parser.add_argument('password', type=str, help='Password for the username')
        parser.add_argument('--doctype', type=DocType,
                            help='Documentation type to generate (either for FTD Ansible modules or FTD API endpoints)',
                            default=DocType.ftd_ansible, choices=list(DocType), required=False)
        parser.add_argument('--models', type=str, nargs='+', help='A list of models to include in the docs', required=False)
        parser.add_argument('--dist', type=str, help='An output directory for distribution files', required=False,
                            default=DEFAULT_DIST_DIR)
        return parser.parse_args()

    def fetch_api_spec_and_version(api_client):
        api_spec = api_client.fetch_api_specs()

        if args.doctype == DocType.ftd_ansible:
            spec_autocomplete = ApiSpecAutocomplete(api_spec)
            spec_autocomplete.lookup_and_complete()

        ftd_version = api_client.fetch_ftd_version(api_spec)
        return api_spec, ftd_version

    def clean_dist_dir():
        if os.path.exists(args.dist):
            shutil.rmtree(args.dist)

    def generate_docs():
        template_ctx = dict(ftd_version=ftd_version, sample_dir=DEFAULT_SAMPLES_DIR)
        if args.doctype == DocType.ftd_ansible:
            ModelDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, api_spec).generate_doc_files(args.dist, args.models)
            OperationDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, api_spec).generate_doc_files(args.dist, args.models)
            ModuleDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, DEFAULT_MODULE_DIR).generate_doc_files(args.dist)
            StaticDocGenerator(STATIC_TEMPLATE_DIR, template_ctx).generate_doc_files(args.dist)
        elif args.doctype == DocType.ftd_api:
            try:
                errors_codes = api_client.fetch_error_codes()
            except Exception as e:
                # All FTD versions before 6.4 will not have such documents
                errors_codes_file = None
            else:
                errors_codes_file = ErrorsDocGenerator(
                    DEFAULT_TEMPLATE_DIR, template_ctx).generate_doc_files(args.dist, errors_codes)
            ResourceDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, api_spec, errors_codes_file)\
                .generate_doc_files(args.dist, args.models)
            ResourceModelDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, api_spec).generate_doc_files(args.dist, args.models)
            APIIntroductionDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, api_version=api_client.get_api_version())\
                .generate_doc_files(args.dist)

    args = parse_args()

    api_client = FtdApiClient(args.hostname, args.username, args.password)
    api_spec, ftd_version = fetch_api_spec_and_version(api_client)

    clean_dist_dir()
    generate_docs()


if __name__ == '__main__':
    main()
