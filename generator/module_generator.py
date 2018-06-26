import argparse
import os
import re
from collections import defaultdict

from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from jinja2 import Environment, FileSystemLoader

from generator.docs_client import SwaggerDocsClient
from generator.param_adapter import SwaggerParamAdapter
from module_utils.authorization import revoke_token, request_token

SWAGGER_SPECS_PREFIX = '/apispec/ngfw.json'
SWAGGER_DOCS_PREFIX = '/apispec/en-us/doc.json'

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_FOLDER = os.path.join(DIR_PATH, 'template')
OUTPUT_DIR = os.path.join(os.path.dirname(DIR_PATH), 'library/generated')

RESOURCE_MODULES = {'NetworkObject', 'AccessPolicy'}


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
    access_token = request_token(args.hostname, args.username, args.password)['access_token']
    try:
        swagger_specs, swagger_docs = construct_swagger_clients(args.hostname, access_token)
        param_adapter = SwaggerParamAdapter(swagger_docs)

        for resource_name in RESOURCE_MODULES:
            if hasattr(swagger_specs, resource_name):
                resource = getattr(swagger_specs, resource_name)
                generate_modules_for_resource(resource, param_adapter)
    finally:
        revoke_token(args.hostname, access_token)


def generate_modules_for_resource(resource, param_adapter):
    model_operations_dict = group_operations_by_model(resource, param_adapter)

    for model_name, operations in model_operations_dict.items():
        with open('%s/fdm_%s.py' % (OUTPUT_DIR, camel_to_snake(model_name)), "w") as f:
            f.write(base_template.render(
                model_name=model_name,
                operations=operations,
                params=param_adapter.get_unique_params(operations),
            ))


def group_operations_by_model(resource, param_adapter):
    def infer_model_name(operation_name):
        reg_ex = r'^(get|add|edit|delete)(\w+?)(List)?$'
        groups = re.match(reg_ex, operation_name)
        if groups:
            return groups[2]
        else:
            raise ValueError("Invalid operation name: %s" % operation_name)

    model_operations = defaultdict(dict)
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


def camel_to_snake(text):
    test_with_underscores = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', test_with_underscores).lower()


parser = argparse.ArgumentParser(description='Generates Ansible modules from Swagger documentation')
parser.add_argument('hostname', help='Hostname where FDM can be accessed')
parser.add_argument('username', help='FDM username that has access to Swagger docs')
parser.add_argument('password', help='Password for the username')
args = parser.parse_args()

env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER), trim_blocks=True, extensions=['jinja2.ext.do'])
env.filters['quote'] = lambda a: "'%s'" % a
env.filters['camel_to_snake'] = lambda a: camel_to_snake(a)
base_template = env.get_template('base_module.j2')

if __name__ == '__main__':
    generate_modules()
