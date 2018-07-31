#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_network_object_group
short_description: Manages NetworkObjectGroup objects on Cisco FTD devices
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  operation:
    description:
      - Specified the name of the operation to execute in the task.
    required: true
  register_as:
    description:
      - Specifies Ansible fact name that is used to register received response from the FTD device.
  description
    description:
      - A string containing the description information<br>Field level constraints: length must be between 0 and 200 (inclusive). (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  isSystemDefined
    description:
      - A Boolean value, TRUE or FALSE(the default). The TRUE value indicates that this Network object group is a system defined object
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A string that is the name of the network group object.
  objects
    description:
      - A comma-delimited list of the names of NetworkObject objects that are part of this group<br>Allowed types are: [NetworkObject]
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch NetworkObjectGroup with a given name
  ftd_network_object_group:
    operation: "getNetworkObjectGroupByName"
    name: "Ansible NetworkObjectGroup"

- name: Create a NetworkObjectGroup
  ftd_network_object_group:
    operation: 'addNetworkObjectGroup'
    description: "From Ansible with love"
    name: "Ansible NetworkObjectGroup"
    objects: ["{{ networkObject }}"]
    type: "networkobjectgroup"
"""

RETURN = """
response:
  description: HTTP response returned from the API call.
  returned: success
  type: dict
error_code:
  description: HTTP error code returned from the server.
  returned: error
  type: int
msg:
  description: Error message returned from the server.
  returned: error
  type: dict
"""
import json

from ansible.module_utils.basic import AnsibleModule, to_text
from ansible.module_utils.http import iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_ansible_facts, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.connection import Connection


class NetworkObjectGroupResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addNetworkObjectGroup(self, params):
        body_params = dict_subset(params, ['description', 'id', 'isSystemDefined', 'name', 'objects', 'type', 'version'])

        return self._conn.send_request(
            url_path='/object/networkgroups',
            http_method='POST',
            body_params=body_params,
        )

    def deleteNetworkObjectGroup(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/object/networkgroups/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editNetworkObjectGroup(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['description', 'id', 'isSystemDefined', 'name', 'objects', 'type', 'version'])

        return self._conn.send_request(
            url_path='/object/networkgroups/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getNetworkObjectGroup(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/object/networkgroups/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getNetworkObjectGroupList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/object/networkgroups',
            http_method='GET',
            query_params=query_params,
        )

    def getNetworkObjectGroupByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getNetworkObjectGroupList, search_params)
        return next((item for item in item_generator if item['name'] == params['name']), None)

    def upsertNetworkObjectGroup(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addNetworkObjectGroup(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getNetworkObjectGroupByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editNetworkObjectGroup(params)
            else:
                raise e

    def editNetworkObjectGroupByName(self, params):
        existing_object = self.getNetworkObjectGroupByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editNetworkObjectGroup(params)

    def deleteNetworkObjectGroupByName(self, params):
        existing_object = self.getNetworkObjectGroupByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteNetworkObjectGroup(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertNetworkObjectGroup', choices=['addNetworkObjectGroup', 'deleteNetworkObjectGroup', 'editNetworkObjectGroup', 'getNetworkObjectGroup', 'getNetworkObjectGroupList', 'getNetworkObjectGroupByName', 'upsertNetworkObjectGroup', 'editNetworkObjectGroupByName', 'deleteNetworkObjectGroupByName']),
        register_as=dict(type='str'),

        description=dict(type='str'),
        filter=dict(type='str'),
        id=dict(type='str'),
        isSystemDefined=dict(type='bool'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        objects=dict(type='list'),
        offset=dict(type='int'),
        sort=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = NetworkObjectGroupResource(conn)

        resource_method_to_call = getattr(resource, params['operation'])
        response = resource_method_to_call(params)
        module.exit_json(changed=True, response=response, ansible_facts=construct_ansible_facts(response, params))
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
