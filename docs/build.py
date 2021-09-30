from __future__ import absolute_import, division, print_function

__metaclass__ = type

import argparse
import json
import logging
import os
import shutil
from enum import Enum
from http import HTTPStatus
from urllib import error as urllib_error

from ansible.module_utils._text import to_text
from ansible.module_utils.urls import open_url

from docs import generator
from docs.enricher import ApiSpecAutocomplete
from ansible_collections.cisco.ftdansible.plugins.httpapi.ftd import BASE_HEADERS
from ansible_collections.cisco.ftdansible.plugins.module_utils.common import HTTPMethod
from ansible_collections.cisco.ftdansible.plugins.module_utils.fdm_swagger_client import FdmSwaggerParser, SpecProp, OperationField

BASE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DEFAULT_TEMPLATE_DIR = os.path.join(BASE_DIR_PATH, 'templates')
FTD_ANSIBLE_STATIC_TEMPLATE_DIR = os.path.join(DEFAULT_TEMPLATE_DIR, 'static', 'ftd_ansible')
FTD_API_STATIC_TEMPLATE_DIR = os.path.join(DEFAULT_TEMPLATE_DIR, 'static', 'ftd_api')
DEFAULT_SAMPLES_DIR = os.path.join(os.path.dirname(BASE_DIR_PATH), 'samples')
DEFAULT_DIST_DIR = os.path.join(BASE_DIR_PATH, 'dist')
DEFAULT_MODULE_DIR = os.path.join(os.path.dirname(BASE_DIR_PATH), 'ansible_collections/cisco/ftdansible/plugins/modules')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class FtdApiClient(object):
    """
    A client that helps to interact with FTD device and takes care of authentication
    and token-related aspects.
    """

    SUPPORTED_VERSIONS = ['latest', 'v3', 'v2', 'v1']
    TOKEN_PATH_TEMPLATE = '/api/fdm/{}/fdm/token'

    API_VERSIONS_PATH = '/api/versions'
    SPEC_PATH = '/apispec/ngfw.json'
    DOC_PATH = '/apispec/en-us/doc.json'
    ERRORS_PATH = '/apispec/customErrorCode.json'

    def __init__(self, hostname, username, password):
        self._hostname = hostname
        self._base_path = None
        token_info = self._authorize(username, password)
        self._auth_headers = self._construct_auth_headers(token_info)

    def _fetch_api_versions(self):
        try:
            # In case of 6.2.3 when Api Versions resource does not exists HTTP 401 will be returned
            resp = open_url(
                self._hostname + self.API_VERSIONS_PATH,
                method=HTTPMethod.GET,
                headers=BASE_HEADERS,
                validate_certs=False
            ).read()
            supported_versions = json.loads(to_text(resp))["supportedVersions"]
        except Exception:
            logger.debug("Can't fetch supported API versions", exc_info=True)
            supported_versions = self.SUPPORTED_VERSIONS

        return supported_versions

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

        api_versions = sorted(self._fetch_api_versions(), reverse=True)

        for version in api_versions:
            token_url = self._hostname + self.TOKEN_PATH_TEMPLATE.format(version)
            try:
                token = request_token(token_url)
            except urllib_error.HTTPError as e:
                logger.debug("Can't get token for API version: %s", version, exc_info=True)
                if e.code != HTTPStatus.UNAUTHORIZED:
                    raise
            else:
                return token

        raise Exception("Can't fetch token via API")

    @property
    def base_path(self):
        return self._base_path

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
        return self._parse_swagger_spec(spec=spec, doc=doc)

    def _parse_swagger_spec(self, spec, doc):
        swagger_parser = FdmSwaggerParser()
        spec = swagger_parser.parse_spec(spec, doc)
        self._base_path = swagger_parser.base_path
        return spec

    def fetch_error_codes(self):
        """
        Downloads an API Error codes specification for FTD device.

        :return: a documented API specification containing error code definitions for FTD device
        :rtype: dict in case error code description fetched successfully
        :rtype: None in case error code description was not present at server side
        """
        try:
            spec = self._send_request(self.ERRORS_PATH, HTTPMethod.GET)
        except json.decoder.JSONDecodeError:
            # All FTD versions before 6.4 will not have such documents
            spec = None

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


def _parse_args():
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


def _fetch_api_spec_and_version(api_client, args):
    api_spec = api_client.fetch_api_specs()

    if args.doctype == DocType.ftd_ansible:
        spec_autocomplete = ApiSpecAutocomplete(api_spec)
        spec_autocomplete.lookup_and_complete()

    ftd_version = api_client.fetch_ftd_version(api_spec)
    return api_spec, ftd_version


def _clean_dist_dir(args):
    if os.path.exists(args.dist):
        shutil.rmtree(args.dist)


def _generate_ansible_docs(args, api_spec, template_ctx):
    generator.ModelDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, api_spec) \
        .generate_doc_files(args.dist, args.models)
    generator.OperationDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, api_spec) \
        .generate_doc_files(args.dist, args.models)
    generator.ModuleDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, DEFAULT_MODULE_DIR) \
        .generate_doc_files(args.dist)
    generator.StaticDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, FTD_ANSIBLE_STATIC_TEMPLATE_DIR) \
        .generate_doc_files(args.dist)


def _generate_ftd_api_docs(args, api_spec, template_ctx, errors_codes):
    if template_ctx['ftd_version'] == '7.0.0':
        # SSLGroupType has incorrect representation in 7.0.0 API spec, as it doesn't contain possible enum values.
        # We need to add these enum values here to generate docs and represent possible values.
        api_spec['models']['SSLGroupType']['enum'] = ["GROUP_14", "GROUP_15", "GROUP_19", "GROUP_20", "GROUP_21"]

    generator.ResourceDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, api_spec) \
        .generate_doc_files(args.dist, args.models)
    generator.ModelDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, api_spec) \
        .generate_doc_files(args.dist, args.models)
    generator.ApiIntroductionDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx) \
        .generate_doc_files(args.dist)
    if errors_codes:
        generator.ErrorDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx) \
            .generate_doc_files(args.dist, errors_codes)
    generator.StaticDocGenerator(DEFAULT_TEMPLATE_DIR, template_ctx, FTD_API_STATIC_TEMPLATE_DIR) \
        .generate_doc_files(args.dist)


def _generate_docs(args, api_client):
    api_spec, ftd_version = _fetch_api_spec_and_version(api_client, args)

    template_ctx = dict(ftd_version=ftd_version,
                        sample_dir=DEFAULT_SAMPLES_DIR,
                        doctype=args.doctype,
                        base_path=api_client.base_path)

    if args.doctype == DocType.ftd_ansible:
        _generate_ansible_docs(args, api_spec, template_ctx)
    elif args.doctype == DocType.ftd_api:
        error_codes = api_client.fetch_error_codes()
        template_ctx['error_codes'] = bool(error_codes)
        _generate_ftd_api_docs(args, api_spec, template_ctx, error_codes)


if __name__ == '__main__':
    arguments = _parse_args()
    _clean_dist_dir(arguments)
    _generate_docs(
        arguments,
        FtdApiClient(arguments.hostname, arguments.username, arguments.password)
    )
