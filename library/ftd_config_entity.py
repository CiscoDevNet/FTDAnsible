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
            method=HTTPMethod.POST,
            url='/object/networks'
        ),
        dict(
            id='deleteNetworkObject',
            method=HTTPMethod.DELETE,
            url='/object/networks/{objId}'
        )
    ]
    return next((op for op in operations if op['id'] == operation_name), None)


def is_add_operation(operation_spec):
    return operation_spec['id'].startswith('add') and operation_spec['method'] == HTTPMethod.POST


def is_edit_operation(operation_spec):
    return operation_spec['id'].startswith('edit') and operation_spec['method'] == HTTPMethod.PUT


def is_delete_operation(operation_spec):
    return operation_spec['id'].startswith('delete') and operation_spec['method'] == HTTPMethod.DELETE


def main():
    fields = dict(
        operation=dict(type='str', required=True),
        data=dict(type='dict'),
        query_params=dict(typee='dict'),
        path_params=dict(type='dict'),
        register_as=dict(type='str')
    )
    module = AnsibleModule(argument_spec=fields)
    params = module.params

    op_spec = get_operation_spec(params['operation'])
    if op_spec is None:
        module.fail_json(msg='Invalid operation name provided: %s' % params['operation'])

    data, query_params, path_params = params['data'], params['query_params'], params['path_params']
    # TODO: implement validation for input parameters

    resource = BaseConfigObjectResource(Connection(module._socket_path))

    if is_add_operation(op_spec):
        resp = resource.add_object(op_spec['url'], data, path_params, query_params)
    elif is_edit_operation(op_spec):
        resp = resource.edit_object(op_spec['url'], data, path_params, query_params)
    elif is_delete_operation(op_spec):
        resp = resource.delete_object(op_spec['url'], path_params)
    else:
        resp = resource._send_request(op_spec['url'], op_spec['method'], data, path_params, query_params)

    module.exit_json(changed=resource.config_changed, response=resp,
                     ansible_facts=construct_ansible_facts(resp, module.params))


if __name__ == '__main__':
    main()
