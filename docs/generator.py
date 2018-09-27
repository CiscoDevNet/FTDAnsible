import argparse
import importlib
import json
import os
import re
import sys
from collections import namedtuple

import yaml
from ansible.module_utils._text import to_text
from ansible.module_utils.urls import open_url
from jinja2 import Environment, FileSystemLoader

from httpapi_plugins.ftd import BASE_HEADERS
from module_utils.common import HTTPMethod
from module_utils.fdm_swagger_client import FdmSwaggerParser, SpecProp, OperationField, PropName, OperationParams

BASE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

TOKEN_PATH = '/api/fdm/v2/fdm/token'
SPEC_PATH = '/apispec/ngfw.json'
DOC_PATH = '/apispec/en-us/doc.json'

ModelSpec = namedtuple('ModelSpec', 'name description properties operations')
OperationSpec = namedtuple('OperationSpec', 'name description model_name path_params query_params data_params')
ModuleSpec = namedtuple('ModuleSpec', 'name short_description description params return_values examples')


class DocGenerator(object):
    TEMPLATE_FOLDER = os.path.join(BASE_DIR_PATH, 'templates')
    DOCSITE_DIR_PATH = os.path.join(BASE_DIR_PATH, 'docsite')
    LIBRARY_DIR_PATH = os.path.join(os.path.dirname(BASE_DIR_PATH), 'library')

    MODEL_TEMPLATE = 'model.md.j2'
    OPERATION_TEMPLATE = 'operation.md.j2'
    MODULE_TEMPLATE = 'module.md.j2'
    INDEX_TEMPLATE = 'index.md.j2'
    CONFIG_TEMPLATE = 'config.json.j2'

    MD_SUFFIX = '.md'
    J2_SUFFIX = '.j2'

    _api_spec = None
    _jinja_env = None

    def __init__(self, api_spec):
        self._api_spec = api_spec
        self._jinja_env = self._init_jinja_env()

    def _init_jinja_env(self):
        env = Environment(loader=FileSystemLoader(self.TEMPLATE_FOLDER), trim_blocks=True, lstrip_blocks=True)
        env.filters['camel_to_snake'] = camel_to_snake
        return env

    def generate_model_docs(self, include_models=None, dest=None):
        model_folder = os.path.join(dest if dest else self.DOCSITE_DIR_PATH, 'models')
        self._clean_generated_files(model_folder)

        model_index = []
        model_template = self._jinja_env.get_template(self.MODEL_TEMPLATE)

        for model_name, operations in self._api_spec[SpecProp.MODEL_OPERATIONS].items():
            ignore_model = include_models and model_name not in include_models
            # TODO: investigate why some operations still have None model name
            if model_name is None or ignore_model:
                continue

            model_api_spec = self._api_spec[SpecProp.MODELS].get(model_name, {})
            model_spec = ModelSpec(
                name=model_name,
                description=model_api_spec.get(PropName.DESCRIPTION, ''),
                properties=model_api_spec.get(PropName.PROPERTIES, {}),
                operations=operations.keys()
            )
            model_content = model_template.render(model=model_spec)
            self._write_generated_file(model_folder, model_name + self.MD_SUFFIX, model_content)
            model_index.append(model_name)

        self._write_index_files(model_folder, 'Model', model_index)

    def generate_operation_docs(self, include_models=None, dest=None):
        def get_data_params(op):
            if op[OperationField.METHOD] == HTTPMethod.POST or op[OperationField.METHOD] == HTTPMethod.PUT:
                model_name = op[OperationField.MODEL_NAME]
                model_api_spec = self._api_spec[SpecProp.MODELS].get(model_name, {})
                return model_api_spec.get(PropName.PROPERTIES, {})
            return {}

        op_folder = os.path.join(dest if dest else self.DOCSITE_DIR_PATH, 'operations')
        self._clean_generated_files(op_folder)

        op_index = []
        op_template = self._jinja_env.get_template(self.OPERATION_TEMPLATE)

        for op_name, op_api_spec in self._api_spec[SpecProp.OPERATIONS].items():
            ignore_op = include_models and op_api_spec[OperationField.MODEL_NAME] not in include_models
            if ignore_op:
                continue

            op_spec = OperationSpec(
                name=op_name,
                description=op_api_spec.get(OperationField.DESCRIPTION),
                model_name=op_api_spec[OperationField.MODEL_NAME],
                path_params=op_api_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.PATH, {}),
                query_params=op_api_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.QUERY, {}),
                data_params=get_data_params(op_api_spec)
            )
            op_content = op_template.render(operation=op_spec)
            self._write_generated_file(op_folder, op_name + self.MD_SUFFIX, op_content)
            op_index.append(op_name)

        self._write_index_files(op_folder, 'Operation', op_index)

    def generate_module_docs(self, dest=None):
        def to_text(text):
            return ' '.join(text) if type(text) == list else text

        def get_module_params(docs):
            return {k: {
                'description': to_text(v.get('description')),
                'required': v.get('required', False),
                'type': v.get('type', '')
            } for k, v in docs.get('options', {}).items()}

        def get_module_return_values(mod):
            return_params = yaml.load(mod.RETURN)
            return {k: {
                'description': to_text(v.get('description')),
                'returned': v.get('returned', ''),
                'type': v.get('type', '')
            } for k, v in return_params.items()}

        module_folder = os.path.join(dest if dest else self.DOCSITE_DIR_PATH, 'modules')
        self._clean_generated_files(module_folder)

        module_index = []
        module_template = self._jinja_env.get_template(self.MODULE_TEMPLATE)

        # add the module folder to the Python path
        sys.path.insert(0, self.LIBRARY_DIR_PATH)
        for module_filename in os.listdir(self.LIBRARY_DIR_PATH):
            if not module_filename.startswith('ftd_'):
                continue

            module_name = os.path.splitext(module_filename)[0]
            module = importlib.import_module(module_name)

            module_docs = yaml.load(module.DOCUMENTATION)
            module_spec = ModuleSpec(
                name=module_name,
                short_description=to_text(module_docs.get('short_description')),
                description=to_text(module_docs.get('description')),
                params=get_module_params(module_docs),
                return_values=get_module_return_values(module),
                examples=module.EXAMPLES
            )
            module_content = module_template.render(module=module_spec)
            self._write_generated_file(module_folder, module_name + self.MD_SUFFIX, module_content)
            module_index.append(module_name)

        self._write_index_files(module_folder, 'Module', module_index)

    @staticmethod
    def _write_generated_file(dir_path, filename, content):
        with open('%s/%s' % (dir_path, camel_to_snake(filename)), "wb") as f:
            f.write(content.encode('utf-8'))

    def _write_index_files(self, dir_path, index_name, index_list):
        index_data = {'index_name': index_name, 'index_list': index_list}

        for template_name in [self.INDEX_TEMPLATE, self.CONFIG_TEMPLATE]:
            template = self._jinja_env.get_template(template_name)
            content = template.render(**index_data)
            filename = template_name[:-len(self.J2_SUFFIX)]
            self._write_generated_file(dir_path, filename, content)

    @staticmethod
    def _clean_generated_files(dir_path):
        for file_name in os.listdir(dir_path):
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
    parser.add_argument('--dest', type=str, help='An output directory for generated files', required=False)
    args = parser.parse_args()

    api_spec = fetch_api_specs_with_docs(args.hostname, args.username, args.password)
    doc_generator = DocGenerator(api_spec)
    doc_generator.generate_model_docs(args.models, args.dest)
    doc_generator.generate_operation_docs(args.models, args.dest)
    doc_generator.generate_module_docs(args.dest)


if __name__ == '__main__':
    main()
