import argparse
import importlib
import json
import os
import re
import sys
from abc import ABCMeta, abstractmethod
from collections import namedtuple

import yaml
from ansible.module_utils._text import to_text
from ansible.module_utils.urls import open_url
from jinja2 import Environment, FileSystemLoader

from httpapi_plugins.ftd import BASE_HEADERS
from module_utils.common import HTTPMethod, IDENTITY_PROPERTIES
from module_utils.fdm_swagger_client import FdmSwaggerParser, SpecProp, OperationField, PropName, OperationParams

BASE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DEFAULT_TEMPLATE_DIR = os.path.join(BASE_DIR_PATH, 'templates')
DEFAULT_SAMPLES_DIR = os.path.join(os.path.dirname(BASE_DIR_PATH), 'samples')
DEFAULT_DOCSITE_DIR = os.path.join(BASE_DIR_PATH, 'docsite')
DEFAULT_MODULE_DIR = os.path.join(os.path.dirname(BASE_DIR_PATH), 'library')

TOKEN_PATH = '/api/fdm/v2/fdm/token'
SPEC_PATH = '/apispec/ngfw.json'
DOC_PATH = '/apispec/en-us/doc.json'

ModelSpec = namedtuple('ModelSpec', 'name description properties operations')
OperationSpec = namedtuple('OperationSpec', 'name description model_name path_params query_params data_params')
ModuleSpec = namedtuple('ModuleSpec', 'name short_description description params return_values examples')


class BaseDocGenerator(metaclass=ABCMeta):
    """Abstract class for documentation generators that produce
    docs from Jinja templates. Contains common methods for working
    with templates, writing and cleaning doc files, etc. Subclasses
    must implement `generate_doc_files` method.
    """

    INDEX_TEMPLATE = 'index.md.j2'
    CONFIG_TEMPLATE = 'config.json.j2'

    MD_SUFFIX = '.md'
    J2_SUFFIX = '.j2'

    def __init__(self, template_dir):
        env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True,
                          extensions=['extension.IncludePlaybookTasks'])
        env.filters['camel_to_snake'] = camel_to_snake
        self._jinja_env = env

    @abstractmethod
    def generate_doc_files(self, dest_dir):
        """
        Generates documentation and writes it to files on the filesystem.
        Must be implemented in the subclasses.

        :param dest_dir: the base directory to write the doc files to
        :return: None
        """
        pass

    @staticmethod
    def _clean_generated_files(dir_path):
        for file_name in os.listdir(dir_path):
            os.remove(os.path.join(dir_path, file_name))

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


class ModelDocGenerator(BaseDocGenerator):
    """Generates documentation for the models defined in the
    Swagger specification. Documentation is written using
    Markdown markup language.
    """

    MODEL_TEMPLATE = 'model.md.j2'

    def __init__(self, template_dir, api_spec):
        super().__init__(template_dir)
        self._api_spec = api_spec

    def generate_doc_files(self, dest_dir, include_models=None):
        model_dir = os.path.join(dest_dir, 'models')
        self._clean_generated_files(model_dir)

        model_index = []
        model_template = self._jinja_env.get_template(self.MODEL_TEMPLATE)

        for model_name, operations in self._api_spec[SpecProp.MODEL_OPERATIONS].items():
            ignore_model = include_models and model_name not in include_models
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
            self._write_generated_file(model_dir, model_name + self.MD_SUFFIX, model_content)
            model_index.append(model_name)

        self._write_index_files(model_dir, 'Model', model_index)


class OperationDocGenerator(BaseDocGenerator):
    """Generates documentation for the operations defined in the
    Swagger specification. Documentation is written using
    Markdown markup language.
    """

    OPERATION_TEMPLATE = 'operation.md.j2'

    def __init__(self, template_dir, api_spec):
        super().__init__(template_dir)
        self._api_spec = api_spec

    def generate_doc_files(self, dest_dir, include_models=None):
        op_dir = os.path.join(dest_dir, 'operations')
        self._clean_generated_files(op_dir)

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
                data_params=self._get_data_params(op_name, op_api_spec)
            )
            op_content = op_template.render(operation=op_spec)
            self._write_generated_file(op_dir, op_name + self.MD_SUFFIX, op_content)
            op_index.append(op_name)

        self._write_index_files(op_dir, 'Operation', op_index)

    def _get_data_params(self, op_name, op_spec):
        op_method = op_spec[OperationField.METHOD]
        if op_method != HTTPMethod.POST and op_method != HTTPMethod.PUT:
            return {}

        model_name = op_spec[OperationField.MODEL_NAME]
        model_api_spec = self._api_spec[SpecProp.MODELS].get(model_name, {})
        data_params = model_api_spec.get(PropName.PROPERTIES, {})

        if op_name.startswith('add') and op_method == HTTPMethod.POST:
            data_params = {k: v for k, v in data_params.items() if k not in IDENTITY_PROPERTIES}

        return data_params


class ModuleDocGenerator(BaseDocGenerator):
    """Generates documentation for FTD Ansible modules. Content of
    the docs is fetched directly from the `.py` files of Ansible
    modules. Documentation is written using Markdown markup language.
    """

    MODULE_TEMPLATE = 'module.md.j2'

    def __init__(self, template_dir, module_dir):
        super().__init__(template_dir)
        self._module_dir = module_dir

    def generate_doc_files(self, dest_dir):
        module_dir = os.path.join(dest_dir, 'modules')
        self._clean_generated_files(module_dir)

        module_index = []
        module_template = self._jinja_env.get_template(self.MODULE_TEMPLATE)

        # add the module dir to the Python path
        sys.path.insert(0, self._module_dir)
        for module_filename in os.listdir(self._module_dir):
            if not module_filename.startswith('ftd_'):
                continue

            module_name = os.path.splitext(module_filename)[0]
            module = importlib.import_module(module_name)

            module_docs = yaml.load(module.DOCUMENTATION)
            module_spec = ModuleSpec(
                name=module_name,
                short_description=self._doc_to_text(module_docs.get('short_description')),
                description=self._doc_to_text(module_docs.get('description')),
                params=self._get_module_params(module),
                return_values=self._get_module_return_values(module),
                examples=module.EXAMPLES
            )
            module_content = module_template.render(module=module_spec)
            self._write_generated_file(module_dir, module_name + self.MD_SUFFIX, module_content)
            module_index.append(module_name)

        self._write_index_files(module_dir, 'Module', module_index)

    @staticmethod
    def _doc_to_text(text):
        return ' '.join(text) if type(text) == list else text

    @staticmethod
    def _get_module_params(module):
        docs = yaml.load(module.DOCUMENTATION)
        return {k: {
            'description': ModuleDocGenerator._doc_to_text(v.get('description')),
            'required': v.get('required', False),
            'type': v.get('type', '')
        } for k, v in docs.get('options', {}).items()}

    @staticmethod
    def _get_module_return_values(module):
        return_params = yaml.load(module.RETURN)
        return {k: {
            'description': ModuleDocGenerator._doc_to_text(v.get('description')),
            'returned': v.get('returned', ''),
            'type': v.get('type', '')
        } for k, v in return_params.items()}


class ExampleDocGenerator(BaseDocGenerator):
    """Generates documentation for examples. Task examples
    are dynamically copied from real Ansible playbooks.
    Documentation is written using Markdown markup language.
    """

    EXAMPLES_TEMPLATE = 'examples.md.j2'

    def __init__(self, template_dir, sample_dir):
        super().__init__(template_dir)
        self._sample_dir = sample_dir

    def generate_doc_files(self, dest_dir):
        example_template = self._jinja_env.get_template(self.EXAMPLES_TEMPLATE)
        example_content = example_template.render(sample_dir=self._sample_dir)

        filename = self.EXAMPLES_TEMPLATE[:-len(self.J2_SUFFIX)]
        self._write_generated_file(dest_dir, filename, example_content)


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
    parser.add_argument('--dest', type=str, help='An output directory for generated files', required=False,
                        default=DEFAULT_DOCSITE_DIR)
    args = parser.parse_args()

    api_spec = fetch_api_specs_with_docs(args.hostname, args.username, args.password)

    model_generator = ModelDocGenerator(DEFAULT_TEMPLATE_DIR, api_spec)
    model_generator.generate_doc_files(args.dest, args.models)

    op_generator = OperationDocGenerator(DEFAULT_TEMPLATE_DIR, api_spec)
    op_generator.generate_doc_files(args.dest, args.models)

    module_generator = ModuleDocGenerator(DEFAULT_TEMPLATE_DIR, DEFAULT_MODULE_DIR)
    module_generator.generate_doc_files(args.dest)

    example_generator = ExampleDocGenerator(DEFAULT_TEMPLATE_DIR, DEFAULT_SAMPLES_DIR)
    example_generator.generate_doc_files(args.dest)


if __name__ == '__main__':
    main()
