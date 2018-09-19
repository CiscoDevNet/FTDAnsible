import json
import os
from collections import namedtuple

import re

import argparse
from ansible.module_utils._text import to_text
from ansible.module_utils.urls import open_url
from jinja2 import Environment, FileSystemLoader

from httpapi_plugins.ftd import BASE_HEADERS
from module_utils.common import HTTPMethod
from module_utils.fdm_swagger_client import FdmSwaggerParser, SpecProp, OperationField, PropName, OperationParams

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

TOKEN_PATH = '/api/fdm/v2/fdm/token'
SPEC_PATH = '/apispec/ngfw.json'
DOC_PATH = '/apispec/en-us/doc.json'

ModelSpec = namedtuple('ModelSpec', 'name description properties operations')
OperationSpec = namedtuple('OperationSpec', 'name description path_params query_params')


class DocGenerator(object):
    TEMPLATE_FOLDER = os.path.join(DIR_PATH, 'templates')
    MODELS_FOLDER = os.path.join(DIR_PATH, 'models')
    OPERATIONS_FOLDER = os.path.join(DIR_PATH, 'operations')

    MODEL_TEMPLATE = 'model.j2'
    OPERATION_TEMPLATE = 'operation.j2'
    INDEX_FILE = 'index.rst'

    _api_spec = None
    _jinja_env = None

    def __init__(self, api_spec):
        self._api_spec = api_spec
        self._jinja_env = self._init_jinja_env()

    def _init_jinja_env(self):
        env = Environment(loader=FileSystemLoader(self.TEMPLATE_FOLDER), trim_blocks=True, lstrip_blocks=True)
        env.filters['camel_to_snake'] = camel_to_snake
        # TODO: find a proper way to convert HTML tags to reStructuredText format
        env.filters['br_to_newline'] = lambda s: '| ' + s.replace('<br>', '\n    | ') if '<br>' in s else s
        return env

    def generate_model_index(self, include_models=None):
        self._clean_generated_files(self.MODELS_FOLDER)

        for model_name, operations in self._api_spec[SpecProp.MODEL_OPERATIONS].items():
            ignore_model = include_models and model_name not in include_models
            # TODO: investigate why some operations still have None model name
            if model_name is None or ignore_model:
                continue

            model_api_spec = self._api_spec[SpecProp.MODELS].get(model_name, {})
            model_spec = ModelSpec(
                model_name,
                model_api_spec.get(PropName.DESCRIPTION, ''),
                model_api_spec.get(PropName.PROPERTIES, {}),
                operations.keys()
            )
            model_content = self._jinja_env.get_template(self.MODEL_TEMPLATE).render(model=model_spec)
            self._write_generated_file(self.MODELS_FOLDER, model_name, model_content)

    def generate_operation_index(self, include_models=None):
        self._clean_generated_files(self.OPERATIONS_FOLDER)

        for op_name, op_api_spec in self._api_spec[SpecProp.OPERATIONS].items():
            ignore_op = include_models and op_api_spec[OperationField.MODEL_NAME] not in include_models
            if ignore_op:
                continue

            op_spec = OperationSpec(
                op_name,
                op_api_spec.get(OperationField.DESCRIPTION),
                op_api_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.PATH, {}),
                op_api_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.QUERY, {}),
            )
            operation_content = self._jinja_env.get_template(self.MODEL_TEMPLATE).render(operation=op_spec)
            self._write_generated_file(self.OPERATIONS_FOLDER, op_name, operation_content)

    @staticmethod
    def _write_generated_file(dir_path, filename, content):
        with open('%s/%s.rst' % (dir_path, camel_to_snake(filename)), "wb") as f:
            f.write(content.encode('utf-8'))

    def _clean_generated_files(self, dir_path):
        for file_name in os.listdir(dir_path):
            if file_name != self.INDEX_FILE:
                os.remove(os.path.join(dir_path, file_name))


def camel_to_snake(text):
    test_with_underscores = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', test_with_underscores).lower()


def fetch_api_specs_with_docs(hostname, username, password):
    def request_token():
        resp = open_url(
            hostname + TOKEN_PATH,
            method=HTTPMethod.POST,
            data=json.dumps({'grant_type': 'password', 'username': username, 'password': password}),
            headers=BASE_HEADERS,
            validate_certs=False
        ).read()
        return json.loads(to_text(resp))

    headers = dict(BASE_HEADERS)
    headers['Authorization'] = 'Bearer %s' % request_token()['access_token']

    spec_resp = open_url(hostname + SPEC_PATH, method=HTTPMethod.GET, headers=headers, validate_certs=False).read()
    docs_resp = open_url(hostname + DOC_PATH, method=HTTPMethod.GET, headers=headers, validate_certs=False).read()
    return FdmSwaggerParser().parse_spec(json.loads(to_text(spec_resp)), json.loads(to_text(docs_resp)))


def main():
    parser = argparse.ArgumentParser(description='Generates Ansible modules from Swagger documentation')
    parser.add_argument('hostname', type=str, help='Hostname where FTD can be accessed')
    parser.add_argument('username', type=str, help='FTD username that has access to Swagger docs')
    parser.add_argument('password', type=str, help='Password for the username')
    parser.add_argument('--models', type=str, nargs='+', help='A list of models to include in the docs', required=False)
    args = parser.parse_args()

    api_spec = fetch_api_specs_with_docs(args.hostname, args.username, args.password)
    doc_generator = DocGenerator(api_spec)
    doc_generator.generate_model_index(args.models)
    doc_generator.generate_operation_index(args.models)


if __name__ == '__main__':
    main()
