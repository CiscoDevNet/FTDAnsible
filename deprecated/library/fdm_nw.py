#!/usr/bin/python

from ansible.module_utils.basic import *
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient


def get_spec_json(hostname, token):
    http_client = RequestsClient()

    http_client.session.verify = False

    http_client.session.headers = {
        'Authorization': 'Bearer %s' % token
    }

    # bravado will validate field type if it's in the JSON

    cli = SwaggerClient.from_url(hostname + '/apispec/ngfw.json', http_client=http_client,
                                 config={'validate_responses': False, 'also_return_response': False})

    return cli


def get_callable_operation(fdm, operation, module_params):
    if operation == 'create':
        return get_create_network_object_operation(fdm, module_params)
    else:
        existing_objects = fdm.NetworkObject.getNetworkObjectList(limit=10000).result()
        existing_object = __find_network_object_by_name(module_params['name'], existing_objects['items'])

        if operation == 'delete':
            return fdm.NetworkObject.deleteNetworkObject(objId=existing_object.id)
        elif operation == 'update':
            return get_update_network_object_operation(fdm, module_params, existing_object)
        else:
            if existing_object:
                return get_update_network_object_operation(fdm, module_params, existing_object)
            else:
                return get_create_network_object_operation(fdm, module_params)


def get_create_network_object_operation(fdm, module_params):
    body = populate_create_network_object_body(module_params)
    return fdm.NetworkObject.addNetworkObject(body=body)


def get_update_network_object_operation(fdm, module_params, existing_object):
    body = populate_update_network_object_body(module_params, existing_object)
    return fdm.NetworkObject.editNetworkObject(body=body, objId=existing_object.id)


def populate_create_network_object_body(module_params):
    body = dict(
        name=module_params['name'],
        description=module_params['description'],
        subType=module_params['sub_type'],
        value=module_params['value'],
        type='networkobject'
    )
    return body


def populate_update_network_object_body(module_params, existing_object):
    body = dict(
        name=module_params.get('name', existing_object['name']),
        description=module_params.get('description', existing_object['description']),
        subType=module_params.get('sub_type', existing_object['subType']),
        value=module_params.get('value', existing_object['value']),
        version=existing_object['version'],
        type='networkobject'
    )
    return body


def __find_network_object_by_name(name, objects):
    for existing_object in objects:
        if existing_object.name == name:
            return existing_object
    return None


def main():
    fields = dict(
        name=dict(type='str', required=True),
        description=dict(type='str', required=False),
        sub_type=dict(choices=['HOST', 'NETWORK'], required=True),
        value=dict(type='str', required=True),
        operation=dict(choices=['create', 'update', 'delete'], required=False),

        token=dict(type='str', required=True, no_log=True),
        device_url=dict(type='str', required=True)
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        fdm = get_spec_json(params['device_url'], params['token'])
        callable_operation = get_callable_operation(fdm, operation=params['operation'], module_params=params)
        callable_operation.result()
        module.exit_json(changed=True)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
