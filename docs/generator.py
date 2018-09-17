import json
import os
import re

import argparse
from ansible.module_utils._text import to_text
from ansible.module_utils.urls import open_url
from jinja2 import Environment, FileSystemLoader

from httpapi_plugins.ftd import BASE_HEADERS
from module_utils.common import HTTPMethod
from module_utils.fdm_swagger_client import FdmSwaggerParser, SpecProp, OperationField

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_FOLDER = os.path.join(DIR_PATH, 'templates')
MODEL_TEMPLATE = 'model.j2'
MODELS_FOLDER = os.path.join(DIR_PATH, 'models')

TOKEN_PATH = '/api/fdm/v1/fdm/token'
SPEC_PATH = '/apispec/ngfw.json'
DOC_PATH = '/apispec/en-us/doc.json'

INDEX_FILE_NAME = 'index.rst'


def generate_model_index(api_spec, docs):
    def clean_model_directory():
        for file_name in os.listdir(MODELS_FOLDER):
            if file_name != INDEX_FILE_NAME:
                os.remove(os.path.join(MODELS_FOLDER, file_name))

    def group_operations_by_model():
        model_operations = {}
        for operations_name, params in api_spec[SpecProp.OPERATIONS].items():
            model_name = params[OperationField.MODEL_NAME]
            model_operations.setdefault(model_name, {})[operations_name] = params
        return model_operations

    clean_model_directory()

    operations_by_model = group_operations_by_model()
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER), trim_blocks=True, lstrip_blocks=True,
                            extensions=['jinja2.ext.do'])
    jinja_env.filters['camel_to_snake'] = camel_to_snake
    model_template = jinja_env.get_template(MODEL_TEMPLATE)

    for model_name in api_spec[SpecProp.MODELS].keys():
        model_def = docs[SpecProp.DEFINITIONS].get(model_name)
        model_operations = operations_by_model.get(model_name)

        if model_operations:
            with open('%s/%s.rst' % (MODELS_FOLDER, camel_to_snake(model_name)), "wb") as f:
                f.write(model_template.render(
                    model_name=model_name,
                    model_description=model_def['description'] if model_def else '',
                    model_operations=model_operations.keys()
                ).encode('utf-8'))


def generate_operation_index():
    pass


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


def camel_to_snake(text):
    test_with_underscores = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', test_with_underscores).lower()


def main():
    parser = argparse.ArgumentParser(description='Generates Ansible modules from Swagger documentation')
    parser.add_argument('hostname', help='Hostname where FTD can be accessed')
    parser.add_argument('username', help='FTD username that has access to Swagger docs')
    parser.add_argument('password', help='Password for the username')
    args = parser.parse_args()

    api_spec, docs = fetch_api_specs(args.hostname, args.username, args.password)
    generate_model_index(api_spec, docs)


if __name__ == '__main__':
    main()
