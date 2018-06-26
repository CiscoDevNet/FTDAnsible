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


def populate_create_access_rule_object_body(fdm, module_params):
    source_networks_bodies = populate_network_bodies(fdm, module_params['source_networks'])
    if source_networks_bodies is None:
        source_networks_bodies = []

    destination_network_bodies = populate_network_bodies(fdm, module_params['destination_networks'])
    if destination_network_bodies is None:
        destination_network_bodies = []

    body = dict(
        name=module_params['name'],
        sourceNetworks=source_networks_bodies,
        destinationNetworks=destination_network_bodies,
        type='accessrule'
    )
    return body


def populate_update_access_rule_body(fdm, module_params, existing_object):
    body = dict(
        name=module_params.get('name', existing_object['name']),
        sourceNetworks=get_source_networks(fdm, existing_object, module_params),
        destinationNetworks=get_destination_networks(fdm, existing_object, module_params),
        version=existing_object['version'],
        ruleId=existing_object['ruleId'],
        type='accessrule'
    )
    return body


def get_destination_networks(fdm, existing_object, module_params):
    playbook_data = populate_network_bodies(fdm, module_params['destination_networks'])

    if playbook_data is None:
        return existing_object.destinationNetworks
    else:
        return playbook_data


def get_source_networks(fdm, existing_object, module_params):
    playbook_data = populate_network_bodies(fdm, module_params['source_networks'])

    if playbook_data is None:
        return existing_object.sourceNetworks
    else:
        return playbook_data


def get_parent_access_policy_id(fdm):
    access_policy_list = fdm.AccessPolicy.getAccessPolicyList().result()
    return access_policy_list['items'][0].id


def get_callable_operation(fdm, operation, module_params):
    parent_id = get_parent_access_policy_id(fdm)
    if operation == 'create':
        return get_create_access_rule_operation(fdm, module_params, parent_id)
    else:
        existing_objects = fdm.AccessPolicy.getAccessRuleList(limit=10000, parentId=parent_id).result()
        existing_object = __find_object_by_name(module_params['name'], existing_objects['items'])

        if operation == 'delete':
            return fdm.AccessPolicy.deleteAccessRule(objId=existing_object.id, parentId=parent_id)
        elif operation == 'update':
            return get_update_access_rule_operation(fdm, module_params, existing_object, parent_id)
        else:
            if existing_object:
                return get_update_access_rule_operation(fdm, module_params, existing_object, parent_id)
            else:
                return get_create_access_rule_operation(fdm, module_params, parent_id)


def get_create_access_rule_operation(fdm, module_params, parent_id):
    body = populate_create_access_rule_object_body(fdm, module_params)
    return fdm.AccessPolicy.addAccessRule(body=body, parentId=parent_id)


def get_update_access_rule_operation(fdm, module_params, existing_object, parent_id):
    body = populate_update_access_rule_body(fdm, module_params, existing_object)
    return fdm.AccessPolicy.editAccessRule(body=body, objId=existing_object.id, parentId=parent_id)


def populate_network_bodies(fdm, playbook_values):
    network_object_bodies = None

    if playbook_values is not None:
        network_object_bodies = []
        for network_object_keys in playbook_values:
            object_type, name = network_object_keys.split('.')

            if object_type == 'networks':
                network_object_list = fdm.NetworkObject.getNetworkObjectList(limit=10000).result()
                network_object = __find_object_by_name(name, network_object_list['items'])

                network_object_body = dict(
                    id=network_object.id,
                    type=network_object.type,
                    version=network_object.version,
                    name=network_object.name
                )
                network_object_bodies.append(network_object_body)

    return network_object_bodies


def __find_object_by_name(name, objects):
    for existing_object in objects:
        if existing_object.name == name:
            return existing_object
    return None


def main():
    fields = dict(
        name=dict(type='str', required=True),
        description=dict(type='str', required=False),
        source_networks=dict(type='list', required=False),
        destination_networks=dict(type='list', required=False),
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
