from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.config_resource import BaseConfigObjectResource
from ansible.module_utils.connection import Connection
from ansible.module_utils.http import HTTPMethod
from ansible.module_utils.misc import construct_ansible_facts


def get_operation_spec(operation_name):
    # TODO: replace with real data from the 'ngfw.json' file, stub data for now
    operations = [
        dict(
            id='addNetworkObject',
            http_method=HTTPMethod.POST,
            url_path='/object/networks'
        ),
        dict(
            id='deleteNetworkObject',
            http_method=HTTPMethod.DELETE,
            url_path='/object/networks/{objId}'
        )
    ]
    return next((op for op in operations if op['id'] == operation_name), None)


def is_add_operation(operation_spec):
    return operation_spec['id'].startswith('add') and operation_spec['http_method'] == HTTPMethod.POST


def is_edit_operation(operation_spec):
    return operation_spec['id'].startswith('edit') and operation_spec['http_method'] == HTTPMethod.PUT


def is_delete_operation(operation_spec):
    return operation_spec['id'].startswith('delete') and operation_spec['http_method'] == HTTPMethod.DELETE


def main():
    fields = dict(
        operation=dict(type='str', required=True),
        data=dict(type='dict'),
        query_params=dict(typee='dict'),
        path_params=dict(type='dict'),
        register_as=dict(type='str')
    )
    module = AnsibleModule(argument_spec=fields)
    data = module.params['data']
    query_params = module.params['query_params']
    path_params = module.params['path_params']

    operation_spec = get_operation_spec(module.params['operation'])
    if operation_spec is None:
        module.fail_json(msg='Invalid operation name provided: %s' % module.params['operation'])

    connection = Connection(module._socket_path)
    resource = BaseConfigObjectResource(connection)

    url_path = operation_spec['url_path']
    if is_add_operation(operation_spec):
        resp = resource.add_object(url_path, data, path_params, query_params)
    elif is_edit_operation(operation_spec):
        resp = resource.edit_object(url_path, data, path_params, query_params)
    elif is_delete_operation(operation_spec):
        resp = resource.delete_object(url_path, path_params)
    else:
        resp = resource._send_request(url_path, operation_spec['http_method'], data, path_params, query_params)

    module.exit_json(changed=resource.config_changed, response=resp,
                     ansible_facts=construct_ansible_facts(resp, module.params))


if __name__ == '__main__':
    main()
