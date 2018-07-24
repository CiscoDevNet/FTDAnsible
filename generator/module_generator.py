import argparse
import os
import re
from collections import defaultdict, OrderedDict

import yaml
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from jinja2 import Environment, FileSystemLoader

from generator.docs_client import SwaggerDocsClient
from generator.param_adapter import SwaggerParamAdapter
from generator.utils import camel_to_snake, request_token, revoke_token

SWAGGER_SPECS_PREFIX = '/apispec/ngfw.json'
SWAGGER_DOCS_PREFIX = '/apispec/en-us/doc.json'

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_FOLDER = os.path.join(DIR_PATH, 'template')
BASE_TEMPLATE = 'base_module.j2'
JOB_BASED_TEMPLATE = 'job_based_module.j2'
OUTPUT_DIR = os.path.join(os.path.dirname(DIR_PATH), 'library/generated')

EXAMPLE_PROPERTIES_FILE_PATH = os.path.join(DIR_PATH, 'resource/example_properties.yml')

IGNORED_MODULES = {'Token', 'CertFileUploadStatus', 'Download', 'Upload'}
JOB_BASED_MODULES = {'BreakHAStatus', 'JoinHAStatus', 'Deployment'}


def init_template_env():
    env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER), trim_blocks=True, lstrip_blocks=True,
                      extensions=['jinja2.ext.do'])
    env.filters['quote'] = lambda a: "'%s'" % a
    env.filters['camel_to_snake'] = lambda a: camel_to_snake(a)
    return env


def construct_swagger_clients(hostname, token):
    http_client = RequestsClient()
    http_client.session.verify = False
    http_client.session.headers = {
        'Authorization': 'Bearer %s' % token
    }
    specs_client = SwaggerClient.from_url(hostname + SWAGGER_SPECS_PREFIX, http_client=http_client,
                                          config={'validate_responses': False, 'also_return_response': False})
    docs_client = SwaggerDocsClient.from_url(hostname + SWAGGER_DOCS_PREFIX, http_client=http_client)
    return specs_client, docs_client


def generate_modules():
    token_info = request_token(args.hostname, args.username, args.password)
    try:
        template_env = init_template_env()
        swagger_specs, swagger_docs = construct_swagger_clients(args.hostname, token_info['access_token'])
        param_adapter = SwaggerParamAdapter(swagger_docs)

        for resource_name in dir(swagger_specs):
            if resource_name not in IGNORED_MODULES:
                template = template_env.get_template(JOB_BASED_TEMPLATE if resource_name in JOB_BASED_MODULES else BASE_TEMPLATE)
                resource = getattr(swagger_specs, resource_name)
                generate_modules_for_resource(resource_name, resource, template, param_adapter)
    finally:
        revoke_token(args.hostname, token_info['access_token'], token_info['refresh_token'])


def generate_modules_for_resource(resource_name, resource, template, param_adapter):
    model_operations_dict = group_operations_by_model(resource_name, resource, param_adapter)

    for model_name, operations in model_operations_dict.items():
        with open('%s/ftd_%s.py' % (OUTPUT_DIR, camel_to_snake(model_name)), "w") as f:
            f.write(template.render(
                model_name=model_name,
                operations=operations,
                example_properties=get_example_properties(model_name),
                params=param_adapter.get_unique_params(operations),
            ))


def group_operations_by_model(resource_name, resource, param_adapter):

    # some container operations end with 'List', thus removing suffix to infer model name correctly
    def remove_list_suffix(operation_name):
        if resource_name.endswith('List'):
            return operation_name.replace('ListList', 'List')
        else:
            return operation_name.replace('List', '')

    def infer_model_name(operation_name):
        groups = re.match(r'^(get|add|edit|delete)(\w+)$', remove_list_suffix(operation_name))
        if groups:
            return groups.group(2)
        else:
            return resource_name

    model_operations = defaultdict(OrderedDict)
    for operation_name in dir(resource):
        operation_spec = get_operation_spec(resource, operation_name, param_adapter)
        model_name = infer_model_name(operation_name)
        model_operations[model_name][operation_name] = operation_spec
    return model_operations


def get_operation_spec(resource, operation_name, param_adapter):
    operation = getattr(resource, operation_name).operation
    return {
        'url_path': operation.path_name,
        'http_method': operation.http_method,
        'path_params': param_adapter.get_path_params(operation),
        'body_params': param_adapter.get_body_params(operation),
        'query_params': param_adapter.get_query_params(operation),
    }


def get_example_properties(model_name):
    with open(EXAMPLE_PROPERTIES_FILE_PATH, 'r') as f:
        example_properties_by_model = yaml.load(f)
    example_properties = example_properties_by_model.get(model_name, {})
    example_properties['type'] = model_name.lower()
    example_properties['name'] = "Ansible %s" % model_name
    example_properties['description'] = "From Ansible with love"
    return example_properties


parser = argparse.ArgumentParser(description='Generates Ansible modules from Swagger documentation')
parser.add_argument('hostname', help='Hostname where FTD can be accessed')
parser.add_argument('username', help='FTD username that has access to Swagger docs')
parser.add_argument('password', help='Password for the username')
args = parser.parse_args()

if __name__ == '__main__':
    generate_modules()
