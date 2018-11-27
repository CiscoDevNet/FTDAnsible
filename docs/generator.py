import importlib
import os
import sys
import json
from abc import ABCMeta, abstractmethod
from collections import namedtuple

import re
from shutil import copyfile

import yaml
from jinja2 import Environment, FileSystemLoader

from module_utils.common import HTTPMethod, IDENTITY_PROPERTIES
from module_utils.fdm_swagger_client import SpecProp, OperationField, PropName, OperationParams, FILE_MODEL_NAME
from httpapi_plugins.ftd import BASE_HEADERS
from docs import swagger_ui_curlify

ModelSpec = namedtuple('ModelSpec', 'name description properties operations')
OperationSpec = namedtuple('OperationSpec', 'name description model_name path_params query_params data_params')
ModuleSpec = namedtuple('ModuleSpec', 'name short_description description params return_values examples')

CUSTOM_MODEL_MAPPING = {FILE_MODEL_NAME: 'File'}


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

    def __init__(self, template_dir, template_ctx):
        env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True,
                          extensions=['docs.extension.IncludePlaybookTasks'])
        env.filters['camel_to_snake'] = camel_to_snake
        env.filters['escape_md_symbols'] = lambda s: s.replace('[', '&#91;').replace(']', '&#93;') \
            .replace('|', '&#124;')
        self._jinja_env = env
        self._template_ctx = template_ctx

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
    def _write_generated_file(dir_path, filename, content):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open('%s/%s' % (dir_path, camel_to_snake(filename)), "wb") as f:
            f.write(content.encode('utf-8'))

    def _write_index_files(self, dir_path, index_name, index_list):
        index_data = {'index_name': index_name, 'index_list': index_list}

        for template_name in [self.INDEX_TEMPLATE, self.CONFIG_TEMPLATE]:
            template = self._jinja_env.get_template(template_name)
            content = template.render(**index_data, **self._template_ctx)
            filename = template_name[:-len(self.J2_SUFFIX)]
            self._write_generated_file(dir_path, filename, content)


class ModelDocGenerator(BaseDocGenerator):
    """Generates documentation for the models defined in the
    Swagger specification. Documentation is written using
    Markdown markup language.
    """

    MODEL_TEMPLATE = 'model.md.j2'

    def __init__(self, template_dir, template_ctx, api_spec):
        super().__init__(template_dir, template_ctx)
        self._api_spec = api_spec

    def generate_doc_files(self, dest_dir, include_models=None):
        model_dir = os.path.join(dest_dir, 'models')

        model_index = []
        model_template = self._jinja_env.get_template(self.MODEL_TEMPLATE)

        for model_name, operations in self._api_spec[SpecProp.MODEL_OPERATIONS].items():
            ignore_model = include_models and model_name not in include_models
            if model_name is None or ignore_model:
                continue

            model_api_spec = self._api_spec[SpecProp.MODELS].get(model_name, {})
            displayed_model_name = CUSTOM_MODEL_MAPPING.get(model_name, model_name)
            model_spec = ModelSpec(
                name=displayed_model_name,
                description=model_api_spec.get(PropName.DESCRIPTION, ''),
                properties=model_api_spec.get(PropName.PROPERTIES, {}),
                operations=operations.keys()
            )
            model_content = model_template.render(model=model_spec, **self._template_ctx)
            self._write_generated_file(model_dir, displayed_model_name + self.MD_SUFFIX, model_content)
            model_index.append(displayed_model_name)

        self._write_index_files(model_dir, 'Model', model_index)


class OperationDocGenerationMixin(object):

    @staticmethod
    def _get_display_model_name(model_name):
        return CUSTOM_MODEL_MAPPING.get(model_name, model_name)

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


class OperationDocGenerator(BaseDocGenerator, OperationDocGenerationMixin):
    """Generates documentation for the operations defined in the
    Swagger specification. Documentation is written using
    Markdown markup language.
    """

    OPERATION_TEMPLATE = 'operation.md.j2'

    def __init__(self, template_dir, template_ctx, api_spec):
        super().__init__(template_dir, template_ctx)
        self._api_spec = api_spec

    def generate_doc_files(self, dest_dir, include_models=None):
        op_dir = os.path.join(dest_dir, 'operations')

        op_index = []
        op_template = self._jinja_env.get_template(self.OPERATION_TEMPLATE)

        for op_name, op_api_spec in self._api_spec[SpecProp.OPERATIONS].items():
            ignore_op = include_models and op_api_spec[OperationField.MODEL_NAME] not in include_models
            if ignore_op:
                continue

            model_name = op_api_spec[OperationField.MODEL_NAME]
            displayed_model_name = self._get_display_model_name(model_name)
            op_spec = OperationSpec(
                name=op_name,
                description=op_api_spec.get(OperationField.DESCRIPTION),
                model_name=displayed_model_name,
                path_params=op_api_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.PATH, {}),
                query_params=op_api_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.QUERY, {}),
                data_params=self._get_data_params(op_name, op_api_spec)
            )
            op_content = op_template.render(operation=op_spec, **self._template_ctx)
            self._write_generated_file(op_dir, op_name + self.MD_SUFFIX, op_content)
            op_index.append(op_name)

        self._write_index_files(op_dir, 'Operation', op_index)


class ModuleDocGenerator(BaseDocGenerator):
    """Generates documentation for FTD Ansible modules. Content of
    the docs is fetched directly from the `.py` files of Ansible
    modules. Documentation is written using Markdown markup language.
    """

    MODULE_TEMPLATE = 'module.md.j2'
    MODULE_NAME_REGEX = r'^ftd_.*\.py$'

    def __init__(self, template_dir, template_ctx, module_dir):
        super().__init__(template_dir, template_ctx)
        self._module_dir = module_dir

    def generate_doc_files(self, dest_dir):
        module_dir = os.path.join(dest_dir, 'modules')

        module_index = []
        module_template = self._jinja_env.get_template(self.MODULE_TEMPLATE)

        # add the module dir to the Python path
        sys.path.insert(0, self._module_dir)
        for module_filename in os.listdir(self._module_dir):
            if not re.match(self.MODULE_NAME_REGEX, module_filename):
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
            module_content = module_template.render(module=module_spec, **self._template_ctx)
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


class StaticDocGenerator(BaseDocGenerator):
    """Generates documentation for static pages (e.g., "Introduction" or "Installation Guide")
    from Jinja templates. Templates might include simple expressions (e.g., to include variables
    or examples), so context is provided to the template engine when rendering the output.

    Template files must have `j2` file extension. Other files are copied to the output folder as is
    without being rendered by the template engine.

    Documentation is written using Markdown markup language.
    """

    def __init__(self, template_dir, template_ctx):
        super().__init__(template_dir, template_ctx)
        self._template_dir = template_dir

    def generate_doc_files(self, dest_dir):
        for filename in os.listdir(self._template_dir):
            if filename.endswith(self.J2_SUFFIX):
                self._generate_from_template(dest_dir, filename)
            else:
                copyfile(os.path.join(self._template_dir, filename), os.path.join(dest_dir, filename))

    def _generate_from_template(self, dest_dir, filename):
        template = self._jinja_env.get_template(filename)
        content = template.render(**self._template_ctx)
        output_filename = filename[:-len(self.J2_SUFFIX)]
        self._write_generated_file(dest_dir, output_filename, content)


class ResourceDocGenerator(BaseDocGenerator, OperationDocGenerationMixin):
    """Generates documentation for the HTTP resources defined in the
    Swagger specification. Describes available endpoints with their methods,
    models, query/body/path parameters, etc.
    Documentation is written using Markdown markup language.
    """

    OPERATION_TEMPLATE = 'resource_operation.md.j2'
    OVERVIEW_TEMPLATE = 'resource_overview.md.j2'
    CONFIG_TEMPLATE = 'resource_config.json.j2'

    def __init__(self, template_dir, template_ctx, api_spec):
        super().__init__(template_dir, template_ctx)
        self._api_spec = api_spec
        self._models_being_described = []

    @staticmethod
    def model_should_be_ignored(model_name, include_models):
        return model_name is None or (include_models and model_name not in include_models)

    def generate_doc_files(self, dest_dir, include_models=None):
        # TODO:2018-11-22:anton.nikulin: Group operations as in API explorer, not on model name.
        base_dest_dir = os.path.join(dest_dir, "resources")

        for model_name, operations in self._api_spec[SpecProp.MODEL_OPERATIONS].items():
            if self.model_should_be_ignored(model_name, include_models):
                continue

            display_name = self._get_display_model_name(model_name)
            output_dir = os.path.join(base_dest_dir , display_name)
            # model_spec = self._api_spec[SpecProp.MODELS].get(model_name, {})
            self._generate_overview_docs(model_name, operations, output_dir)
            self._generate_config_json(operations, output_dir)
            self._generate_operation_docs(operations, output_dir)
            # add model to the list of models being processed so it can be added to index config file later
            self._models_being_described.append(display_name)

        self._generate_resources_config_file(base_dest_dir)

    def _generate_operation_docs(self, operations, dest_dir):
        template = self._jinja_env.get_template(self.OPERATION_TEMPLATE)

        for op_name, op_spec in operations.items():
            data_params = self._get_data_params(op_name, op_spec)
            op_content = template.render(
                name=op_name,
                description=op_spec.get(OperationField.DESCRIPTION),
                method=op_spec.get(OperationField.METHOD),
                url=op_spec.get(OperationField.URL),
                path_params=op_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.PATH, {}),
                query_params=op_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.QUERY, {}),
                data_params=data_params,
                curl_sample=swagger_ui_curlify.curlify(
                    op_spec, data_params, self._api_spec[SpecProp.MODELS], BASE_HEADERS),
                **self._template_ctx
            )

            self._write_generated_file(dest_dir, op_name + self.MD_SUFFIX, op_content)

    def _generate_overview_docs(self, model_name, operations, dest_dir):
        template = self._jinja_env.get_template(self.OVERVIEW_TEMPLATE)
        model_api_spec = self._api_spec[SpecProp.MODELS].get(model_name, {})
        content = template.render(
            name=self._get_display_model_name(model_name),
            operations=operations.keys(),
            description=model_api_spec.get(PropName.DESCRIPTION, {}),
            properties=model_api_spec.get(PropName.PROPERTIES, {}),
            **self._template_ctx
        )
        self._write_generated_file(dest_dir, 'overview.md', content)

    def _generate_config_json(self, operations, dest_dir):
        template = self._jinja_env.get_template(self.CONFIG_TEMPLATE)
        content = template.render(operations=operations.keys(), **self._template_ctx)
        self._write_generated_file(dest_dir, 'config.json', content)

    def _generate_resources_config_file(self, base_dest_dir):
        config_file_name = os.path.join(base_dest_dir, "config.json")
        self._models_being_described.sort()
        config = {
            "items": [
                {
                    "title": model_name,
                    "type": "config",
                    "content": "{}/config.json".format(model_name)
                }
                for model_name in self._models_being_described
            ]
        }
        with open(config_file_name, "w+") as resource_config_file:
            json.dump(config, resource_config_file, indent=4)


def camel_to_snake(text):
    test_with_underscores = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', test_with_underscores).lower()
