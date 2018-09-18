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

TEMPLATE_FOLDER = os.path.join(DIR_PATH, 'templates')
MODEL_TEMPLATE = 'model.j2'
OPERATION_TEMPLATE = 'operation.j2'

MODELS_FOLDER = os.path.join(DIR_PATH, 'models')
OPERATIONS_FOLDER = os.path.join(DIR_PATH, 'operations')
INDEX_FILE = 'index.rst'

TOKEN_PATH = '/api/fdm/v2/fdm/token'
SPEC_PATH = '/apispec/ngfw.json'
DOC_PATH = '/apispec/en-us/doc.json'

ModelSpec = namedtuple('ModelSpec', 'name description operations')
OperationSpec = namedtuple('OperationSpec', 'name description path_params query_params')


def camel_to_snake(text):
    test_with_underscores = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', test_with_underscores).lower()


def clean_generated_files(dir_path):
    for file_name in os.listdir(dir_path):
        if file_name != INDEX_FILE:
            os.remove(os.path.join(dir_path, file_name))


def generate_model_index(api_spec, model_template, include_models=None):
    clean_generated_files(MODELS_FOLDER)

    for model_name, operations in api_spec[SpecProp.MODEL_OPERATIONS].items():
        ignore_model = include_models and model_name not in include_models
        # TODO: investigate why some operations still have None model name
        if model_name is None or ignore_model:
            continue

        model_spec = ModelSpec(
            model_name,
            api_spec[SpecProp.MODELS].get(model_name, {}).get(PropName.DESCRIPTION, ''),
            operations.keys()
        )
        with open('%s/%s.rst' % (MODELS_FOLDER, camel_to_snake(model_name)), "wb") as f:
            f.write(model_template.render(
                model=model_spec
            ).encode('utf-8'))


def generate_operation_index(api_spec, operation_template, include_models=None):
    clean_generated_files(OPERATIONS_FOLDER)

    for op_name, op_spec in api_spec[SpecProp.OPERATIONS].items():
        ignore_op = include_models and op_spec[OperationField.MODEL_NAME] not in include_models
        if ignore_op:
            continue

        operation = OperationSpec(
            op_name,
            op_spec.get(OperationField.DESCRIPTION),
            op_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.PATH, {}),
            op_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.QUERY, {}),
        )
        with open('%s/%s.rst' % (OPERATIONS_FOLDER, camel_to_snake(op_name)), "wb") as f:
            f.write(operation_template.render(
                operation=operation
            ).encode('utf-8'))


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


def init_jinja_env():
    env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER), trim_blocks=True, lstrip_blocks=True,
                      extensions=['jinja2.ext.do'])
    env.filters['camel_to_snake'] = camel_to_snake
    return env


def main():
    parser = argparse.ArgumentParser(description='Generates Ansible modules from Swagger documentation')
    parser.add_argument('hostname', type=str, help='Hostname where FTD can be accessed')
    parser.add_argument('username', type=str, help='FTD username that has access to Swagger docs')
    parser.add_argument('password', type=str, help='Password for the username')
    parser.add_argument('--models', type=str, nargs='+', help='A list of models to include in the docs', required=False)
    args = parser.parse_args()

    env = init_jinja_env()
    api_spec = fetch_api_specs_with_docs(args.hostname, args.username, args.password)

    generate_model_index(api_spec, env.get_template(MODEL_TEMPLATE), args.models)
    generate_operation_index(api_spec, env.get_template(OPERATION_TEMPLATE), args.models)


if __name__ == '__main__':
    main()
