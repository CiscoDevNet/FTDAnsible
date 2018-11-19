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

SUPPORTED_VERSIONS = ['v2', 'v1']
TOKEN_PATH_TEMPLATE = '/api/fdm/{}/fdm/token'

SPEC_PATH = '/apispec/ngfw.json'
DOC_PATH = '/apispec/en-us/doc.json'


def fetch_api_specs_with_docs(hostname, username, password):
    def request_token(token_url):
        resp = open_url(
            hostname + token_url,
            method=HTTPMethod.POST,
            data=json.dumps({'grant_type': 'password', 'username': username, 'password': password}),
            headers=BASE_HEADERS,
            validate_certs=False
        ).read()
        return json.loads(to_text(resp))

    def get_token():
        for version in SUPPORTED_VERSIONS:
            token_url = TOKEN_PATH_TEMPLATE.format(version)
            try:
                token = request_token(token_url)
            except urllib_error.HTTPError as e:
                if e.code != HTTPStatus.UNAUTHORIZED:
                    raise
            else:
                return token

    def fetch_ftd_version(spec, headers):
        operation = spec[SpecProp.OPERATIONS]['getSystemInformation']

        url = hostname + operation[OperationField.URL].format(objId='default')
        resp = open_url(url, method=operation[OperationField.METHOD], headers=headers, validate_certs=False).read()
        system_info = json.loads(to_text(resp))

        build_version = system_info['softwareVersion']
        ftd_version = build_version.split('-')[0]
        return ftd_version

    headers = dict(BASE_HEADERS)
    headers['Authorization'] = 'Bearer %s' % get_token()['access_token']

    spec_resp = open_url(hostname + SPEC_PATH, method=HTTPMethod.GET, headers=headers, validate_certs=False).read()
    docs_resp = open_url(hostname + DOC_PATH, method=HTTPMethod.GET, headers=headers, validate_certs=False).read()
    api_spec = FdmSwaggerParser().parse_spec(json.loads(to_text(spec_resp)), json.loads(to_text(docs_resp)))
    ftd_version = fetch_ftd_version(api_spec, headers)

    return api_spec, ftd_version


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

    api_spec, ftd_version = fetch_api_specs_with_docs(args.hostname, args.username, args.password)
    clean_dist_dir()

    spec_autocomplete = ApiSpecAutocomplete(api_spec)
    spec_autocomplete.lookup_and_complete()

    model_generator = ModelDocGenerator(DEFAULT_TEMPLATE_DIR, api_spec)
    model_generator.generate_doc_files(args.dist, args.models)

    op_generator = OperationDocGenerator(DEFAULT_TEMPLATE_DIR, api_spec)
    op_generator.generate_doc_files(args.dist, args.models)

    module_generator = ModuleDocGenerator(DEFAULT_TEMPLATE_DIR, DEFAULT_MODULE_DIR)
    module_generator.generate_doc_files(args.dist)

    static_generator = StaticDocGenerator(STATIC_TEMPLATE_DIR, dict(sample_dir=DEFAULT_SAMPLES_DIR, ftd_version=ftd_version))
    static_generator.generate_doc_files(args.dist)


if __name__ == '__main__':
    main()
