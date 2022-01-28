from __future__ import absolute_import, division, print_function

__metaclass__ = type

import importlib
import os
import re
import sys
from collections import namedtuple
from functools import partial
from shutil import copyfile


import yaml
from jinja2 import Environment, FileSystemLoader

from ansible_collections.cisco.ftdansible.plugins.module_utils.common import HTTPMethod
from ansible_collections.cisco.ftdansible.plugins.module_utils.fdm_swagger_client import SpecProp, OperationField, PropName, OperationParams, FILE_MODEL_NAME
from docs.snippets_generation import swagger_ui_bravado, swagger_ui_curlify
from docs import utils
from docs import jinja_filters

ModelSpec = namedtuple('ModelSpec', 'name description properties operations')
OperationSpec = namedtuple('OperationSpec', 'name description model_name path_params query_params data_params')
ModuleSpec = namedtuple('ModuleSpec', 'name short_description description params return_values examples')


class BaseDocGenerator(object):
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

        env.filters['camel_to_snake'] = jinja_filters.camel_to_snake
        env.filters['escape_md_symbols'] = lambda s: s.replace('[', '&#91;').replace(']', '&#93;') \
            .replace('|', '&#124;')

        self._jinja_env = env
        self._template_ctx = template_ctx

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
        with open('%s/%s' % (dir_path, jinja_filters.camel_to_snake(filename)), "wb") as f:
            f.write(content.encode('utf-8'))

    @staticmethod
    def _get_index_data(index_name, index_list):
        return {
            'index_name': index_name,
            'index_list': index_list
        }

    @staticmethod
    def _model_should_be_ignored(model_name, include_models):
        # NOTE(Vitalii Kostenko): made model_name non required here to allow generation of the documentation for
        # the /action/* APIs for example /action/upgrade
        return include_models and model_name not in include_models

    def _write_index_files(self, dir_path, index_name, index_list):
        index_data = self._get_index_data(index_name, index_list)

        for template_name in [self.INDEX_TEMPLATE, self.CONFIG_TEMPLATE]:
            template = self._jinja_env.get_template(template_name)
            content = template.render(**index_data, **self._template_ctx)
            filename = self._get_file_name_from_template_name(template_name)
            self._write_generated_file(dir_path, filename, content)

    def _get_file_name_from_template_name(self, template_name):
        return template_name[:-len(self.J2_SUFFIX)]


class ApiSpecDocGenerator(BaseDocGenerator):
    """Abstract class for documentation generators that create documentation
    pages based on API specification.
    """

    CUSTOM_MODEL_MAPPING = {FILE_MODEL_NAME: 'File'}

    def __init__(self, template_dir, template_ctx, api_spec):
        super().__init__(template_dir, template_ctx)
        self._api_spec = api_spec
        self._jinja_env.filters['show_type_or_reference'] = partial(
            jinja_filters.show_type_or_reference, api_spec=api_spec)
        self._jinja_env.filters['show_description_with_references'] = jinja_filters.show_description_with_references
        self._jinja_env.filters['get_link_to_model_page_by_name'] = jinja_filters.get_link_to_model_page_by_name

    def _get_display_model_name(self, model_name):
        return self.CUSTOM_MODEL_MAPPING.get(model_name, model_name)

    @staticmethod
    def _data_params_are_present(op_spec):
        op_method = op_spec[OperationField.METHOD]
        return op_method == HTTPMethod.POST or op_method == HTTPMethod.PUT

    @staticmethod
    def _get_model_name_from_op_spec(op_spec):
        return op_spec[OperationField.MODEL_NAME]

    def _get_model_properties(self, model_name):
        model_api_spec = self._api_spec[SpecProp.MODELS].get(model_name, {})
        return model_api_spec.get(PropName.PROPERTIES, {})

    def _get_data_params(self, op_name, op_spec):
        op_method = op_spec[OperationField.METHOD]
        if not self._data_params_are_present(op_spec):
            return {}

        model_name = self._get_model_name_from_op_spec(op_spec)
        data_params = self._get_model_properties(model_name)
        return utils.filter_data_params(op_name, op_method, data_params)


class ModelDocGenerator(ApiSpecDocGenerator):
    """Generates documentation for the models defined in the
    Swagger specification. Documentation is written using
    Markdown markup language.
    """

    MODEL_TEMPLATE = 'model.md.j2'

    def __init__(self, template_dir, template_ctx, api_spec):
        super().__init__(template_dir, template_ctx, api_spec)
        self._model_template = self._jinja_env.get_template(self.MODEL_TEMPLATE)
        self._model_dir = None

    def _process_single_model(self, model_name, operations):
        model_api_spec = self._api_spec[SpecProp.MODELS].get(model_name, {})
        displayed_model_name = self._get_display_model_name(model_name)
        model_spec = ModelSpec(
            name=displayed_model_name,
            description=model_api_spec.get(PropName.DESCRIPTION, ''),
            properties=model_api_spec.get(PropName.PROPERTIES, {}),
            operations=[
                {
                    "name": op_name,
                    "tag": op_spec[OperationField.TAGS][0]
                } for op_name, op_spec in operations.items()
            ]
        )
        model_content = self._model_template.render(model=model_spec, **self._template_ctx)
        self._write_generated_file(self._model_dir, displayed_model_name + self.MD_SUFFIX, model_content)
        self._model_index.append(displayed_model_name)

    def _model_should_be_ignored(self, model_name, include_models):
        model_spec = self._api_spec[SpecProp.MODELS][model_name]
        return super()._model_should_be_ignored(model_name, include_models) \
            or model_name.endswith("Wrapper") \
            or PropName.ENUM in model_spec \
            or PropName.PROPERTIES not in model_spec

    def _process_models(self, include_models):
        for model_name in self._api_spec[SpecProp.MODELS]:
            operations = self._api_spec[SpecProp.MODEL_OPERATIONS].get(model_name, {})

            if self._model_should_be_ignored(model_name, include_models):
                continue

            self._process_single_model(model_name, operations)

    def generate_doc_files(self, dest_dir, include_models=None):
        self._model_index = []

        self._model_dir = os.path.join(dest_dir, 'models')

        self._process_models(include_models)

        self._write_index_files(self._model_dir, 'Model', self._model_index)


class OperationDocGenerator(ApiSpecDocGenerator):
    """Generates documentation for the operations defined in the
    Swagger specification. Documentation is written using
    Markdown markup language.
    """

    OPERATION_TEMPLATE = 'operation.md.j2'

    def generate_doc_files(self, dest_dir, include_models=None):
        op_dir = os.path.join(dest_dir, 'operations')

        op_index = []
        op_template = self._jinja_env.get_template(self.OPERATION_TEMPLATE)

        for op_name, op_api_spec in self._api_spec[SpecProp.OPERATIONS].items():
            if self._model_should_be_ignored(op_api_spec[OperationField.MODEL_NAME], include_models):
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

            module_docs = yaml.safe_load(module.DOCUMENTATION)
            module_spec = ModuleSpec(
                name=module_name,
                short_description=self._doc_to_text(module_docs.get('short_description')),
                description=self._doc_to_text(module_docs.get('description')),
                params=self._get_module_params(module),
                return_values=self._get_module_return_values(module),
                examples=module.EXAMPLES
            )
            module_content = module_template.render(module=module_spec, **self._template_ctx)
            print("Generating documentation for %s" % module_name)
            self._write_generated_file(module_dir, module_name + self.MD_SUFFIX, module_content)
            module_index.append(module_name)

        self._write_index_files(module_dir, 'Module', module_index)

    @staticmethod
    def _doc_to_text(text):
        return ' '.join(text) if type(text) == list else text

    @staticmethod
    def _get_module_params(module):
        docs = yaml.safe_load(module.DOCUMENTATION)
        return {k: {
            'description': ModuleDocGenerator._doc_to_text(v.get('description')),
            'required': v.get('required', False),
            'type': v.get('type', '')
        } for k, v in docs.get('options', {}).items()}

    @staticmethod
    def _get_module_return_values(module):
        return_params = yaml.safe_load(module.RETURN)
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

    def __init__(self, template_dir, template_ctx, static_template_dir):
        super().__init__(template_dir, template_ctx)
        self._jinja_env.loader = FileSystemLoader([static_template_dir, template_dir])
        self._static_template_dir = static_template_dir

    def generate_doc_files(self, dest_dir):
        for filename in os.listdir(self._static_template_dir):
            if filename.endswith(self.J2_SUFFIX):
                self._generate_from_template(dest_dir, filename)
            else:
                copyfile(os.path.join(self._static_template_dir, filename), os.path.join(dest_dir, filename))

    def _generate_from_template(self, dest_dir, filename):
        template = self._jinja_env.get_template(filename)
        content = template.render(**self._template_ctx)
        output_filename = self._get_file_name_from_template_name(filename)
        self._write_generated_file(dest_dir, output_filename, content)


class ResourceDocGenerator(ApiSpecDocGenerator):
    """Generates documentation for the HTTP resources defined in the
    Swagger specification. Describes available endpoints with their methods,
    models, query/body/path parameters, etc.
    Documentation is written using Markdown markup language.
    """

    OPERATION_TEMPLATE = 'resource_operation.md.j2'
    CONFIG_TEMPLATE = 'config.json.j2'
    RESOURCES_CONFIG_TEMPLATE = 'resources_config.json.j2'

    def __init__(self, template_dir, template_ctx, api_spec):
        super().__init__(template_dir, template_ctx, api_spec)
        self._tags_being_described = []

    @staticmethod
    def _get_tag_operations(operations):
        tag_operations = {}
        for operations_name, params in operations.items():
            tag_name = params[OperationField.TAGS][0]
            tag_operations.setdefault(tag_name, {})[operations_name] = params

        return tag_operations

    def generate_doc_files(self, dest_dir, include_models=None):
        base_dest_dir = os.path.join(dest_dir, "resources")
        tag_operations = self._get_tag_operations(self._api_spec[SpecProp.OPERATIONS])

        for tag_name, operations in tag_operations.items():
            display_name = self._get_display_model_name(tag_name)
            output_dir = os.path.join(base_dest_dir, display_name)

            self._generate_config_json(operations, output_dir)
            self._generate_operation_docs(operations, output_dir, include_models=include_models)
            # add model to the list of models being processed so it can be added to index config file later
            self._tags_being_described.append(display_name)

        self._generate_resources_config_file(base_dest_dir)

    def _generate_operation_docs(self, operations, dest_dir, include_models=None):
        template = self._jinja_env.get_template(self.OPERATION_TEMPLATE)

        for op_name, op_spec in operations.items():
            model_name = self._get_model_name_from_op_spec(op_spec)
            if self._model_should_be_ignored(model_name, include_models):
                continue
            data_params = self._get_data_params(op_name, op_spec)
            data_params_are_present = self._data_params_are_present(op_spec)

            op_content = template.render(
                name=op_name,
                description=op_spec.get(OperationField.DESCRIPTION),
                method=op_spec.get(OperationField.METHOD),
                url=op_spec.get(OperationField.URL),
                path_params=op_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.PATH, {}),
                query_params=op_spec.get(OperationField.PARAMETERS, {}).get(OperationParams.QUERY, {}),
                data_params=data_params,
                model_name=model_name,
                curl_sample=swagger_ui_curlify.generate_sample(
                    op_spec, data_params_are_present, model_name, self._api_spec[SpecProp.MODELS], self._jinja_env),
                bravado_sample=swagger_ui_bravado.generate_sample(
                    op_name, op_spec, data_params_are_present, model_name, self._api_spec[SpecProp.MODELS],
                    self._jinja_env),
                **self._template_ctx
            )

            self._write_generated_file(dest_dir, op_name + self.MD_SUFFIX, op_content)

    def _generate_config_json(self, operations, dest_dir):
        template = self._jinja_env.get_template(self.CONFIG_TEMPLATE)
        content = template.render(index_list=operations.keys(), **self._template_ctx)
        self._write_generated_file(dest_dir, 'config.json', content)

    def _generate_resources_config_file(self, base_dest_dir):
        self._tags_being_described.sort()

        template = self._jinja_env.get_template(self.RESOURCES_CONFIG_TEMPLATE)
        content = template.render(
            tags_being_described=self._tags_being_described,
            **self._template_ctx
        )
        self._write_generated_file(base_dest_dir, 'config.json', content)


class ErrorDocGenerator(BaseDocGenerator):
    """Generates Page with FTD API native error codes description."""

    ERRORS_TEMPLATE = 'error_codes.md.j2'

    def generate_doc_files(self, dest_dir, errors_codes):
        template = self._jinja_env.get_template(self.ERRORS_TEMPLATE)
        errors_content = template.render(error_types=errors_codes, **self._template_ctx)
        error_codes_file = self._get_file_name_from_template_name(self.ERRORS_TEMPLATE)
        self._write_generated_file(dest_dir, error_codes_file, errors_content)
        return error_codes_file


class ApiIntroductionDocGenerator(BaseDocGenerator):
    """Introduction pages for FTD API documentation generation """

    INTRO_TEMPLATE = 'intro.md.j2'
    AUTH_TEMPLATE = 'auth.md.j2'
    DEPLOY_TEMPLATE = 'deploy_config.md.j2'
    TEMPLATES_TO_RENDER = [INTRO_TEMPLATE, AUTH_TEMPLATE, DEPLOY_TEMPLATE]
    DEST_DIR = "introduction"

    @staticmethod
    def _get_index_data(index_name, index_list):
        return {'index_list': index_list}

    def generate_doc_files(self, dest_dir):
        introduction_dir = os.path.join(dest_dir, self.DEST_DIR)
        for template_name in self.TEMPLATES_TO_RENDER:
            template = self._jinja_env.get_template(template_name)
            page_content = template.render(**self._template_ctx)
            filename = self._get_file_name_from_template_name(template_name)
            self._write_generated_file(introduction_dir, filename, page_content)
