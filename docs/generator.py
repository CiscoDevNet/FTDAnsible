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

TOKEN_PATH = '/api/fdm/v1/fdm/token'
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


def generate_model_index(api_spec, docs, model_template):
    def group_operations_by_model():
        model_operations = {}
        for operation_name, params in api_spec[SpecProp.OPERATIONS].items():
            model_name = params[OperationField.MODEL_NAME]
            model_operations.setdefault(model_name, {})[operation_name] = params
        return model_operations

    clean_generated_files(MODELS_FOLDER)

    operations_by_model = group_operations_by_model()
    for model_name in operations_by_model.keys():
        # delete operations used not to have a model, but the issue is fixed in
        # https://github.com/CiscoDevNet/FTDAnsible/pull/21
        if not model_name:
            continue

        model_def = docs[SpecProp.DEFINITIONS].get(model_name, {})
        model_spec = ModelSpec(
            model_name,
            model_def.get('description', ''),
            operations_by_model.get(model_name)
        )
        with open('%s/%s.rst' % (MODELS_FOLDER, camel_to_snake(model_name)), "wb") as f:
            f.write(model_template.render(
                model=model_spec
            ).encode('utf-8'))


def generate_operation_index(api_spec, docs, operation_template):
    def enrich_params_with_description(op_spec, op_docs):
        param_descriptions = {p['name']: p['description'] for p in op_docs.get('parameters', {})}
        for param_name, params_spec in op_spec[OperationField.PARAMETERS][OperationParams.PATH].items():
            params_spec['description'] = param_descriptions.get(param_name, '')
        for param_name, params_spec in op_spec[OperationField.PARAMETERS][OperationParams.QUERY].items():
            params_spec['description'] = param_descriptions.get(param_name, '')
        return op_spec

    clean_generated_files(OPERATIONS_FOLDER)

    for op_name, op_spec in api_spec[SpecProp.OPERATIONS].items():
        op_docs = docs[PropName.PATHS][op_spec[OperationField.URL][11:]][op_spec[OperationField.METHOD]]
        op_spec = enrich_params_with_description(op_spec, op_docs)
        operation = OperationSpec(
            op_name,
            op_docs.get('description', ''),
            op_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.PATH, {}),
            op_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.QUERY, {}),
        )
        with open('%s/%s.rst' % (OPERATIONS_FOLDER, camel_to_snake(op_name)), "wb") as f:
            f.write(operation_template.render(
                operation=operation
            ).encode('utf-8'))


def fetch_api_specs(hostname, username, password):
    def request_token():
        resp = open_url(
            hostname + TOKEN_PATH,
            method=HTTPMethod.POST,
            data=json.dumps({'grant_type': 'password', 'username': username, 'password': password}),
            headers=BASE_HEADERS
        ).read()
        return json.loads(to_text(resp))

    headers = dict(BASE_HEADERS)
    headers['Authorization'] = 'Bearer %s' % request_token()['access_token']

    spec_resp = open_url(hostname + SPEC_PATH, method=HTTPMethod.GET, headers=headers).read()
    api_spec = FdmSwaggerParser().parse_spec(json.loads(to_text(spec_resp)))
    docs_resp = open_url(hostname + DOC_PATH, method=HTTPMethod.GET, headers=headers).read()
    docs = json.loads(to_text(docs_resp))
    return api_spec, docs


def init_jinja_env():
    env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER), trim_blocks=True, lstrip_blocks=True,
                      extensions=['jinja2.ext.do'])
    env.filters['camel_to_snake'] = camel_to_snake
    return env


def main():
    parser = argparse.ArgumentParser(description='Generates Ansible modules from Swagger documentation')
    parser.add_argument('hostname', help='Hostname where FTD can be accessed')
    parser.add_argument('username', help='FTD username that has access to Swagger docs')
    parser.add_argument('password', help='Password for the username')
    args = parser.parse_args()

    env = init_jinja_env()
    api_spec, docs = fetch_api_specs(args.hostname, args.username, args.password)

    generate_model_index(api_spec, docs, env.get_template(MODEL_TEMPLATE))
    generate_operation_index(api_spec, docs, env.get_template(OPERATION_TEMPLATE))


if __name__ == '__main__':
    main()
