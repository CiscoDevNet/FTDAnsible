#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_network_object
short_description: Manages NetworkObject objects on Cisco FTD devices
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
  dnsResolution
    description:
      - DNS Resolution type can be IPV4_ONLY, IPV6_ONLY or IPV4_AND_IPV6
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name", "subtype".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  isSystemDefined
    description:
      - A Boolean value, TRUE or FALSE(the default). The TRUE value indicates that this Network object is a system defined object
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A string that is the name of the network object.
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  sort
    description:
      - The field used to sort the requested object list
  subType
    description:
      - An enum value that specifies the network object type<br>HOST - A host type.<br>NETWORK - A network type.<br>FQDN - A FQDN type.<br>(Note that IPRANGE is not supported)<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  value
    description:
      - A string that defines the address content for the object. For HOST objects, this is a single IPv4 or IPv6 address without netmask or prefix. For NETWORK objects, this is an IPv4 or IPv6 network address with netmask (in CIDR notation) or prefix. For FQDN objects, this is a Fully qualified domain name.<br>Field level constraints: cannot be null, must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch NetworkObject with a given name
  ftd_network_object:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getNetworkObjectByName"
    name: "Ansible NetworkObject"

- name: Create a NetworkObject
  ftd_network_object:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addNetworkObject'

    description: "From Ansible with love"
    dnsResolution: "IPV4_AND_IPV6"
    name: "Ansible NetworkObject"
    subType: "NETWORK"
    type: "networkobject"
    value: "192.168.2.0/24"
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
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.connection import Connection


class NetworkObjectResource(object):

    def __init__(self, conn):
        self._conn = conn
    
    def addNetworkObject(self, params):
        body_params = dict_subset(params, ['description', 'dnsResolution', 'id', 'isSystemDefined', 'name', 'subType', 'type', 'value', 'version'])

        return self._conn.send_request(
            url_path='/object/networks',
            http_method='POST',
            body_params=body_params,
        )

    def deleteNetworkObject(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/object/networks/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editNetworkObject(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['description', 'dnsResolution', 'id', 'isSystemDefined', 'name', 'subType', 'type', 'value', 'version'])

        return self._conn.send_request(
            url_path='/object/networks/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getNetworkObject(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/object/networks/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getNetworkObjectList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/object/networks',
            http_method='GET',
            query_params=query_params,
        )

    def getNetworkObjectByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getNetworkObjectList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertNetworkObject(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addNetworkObject(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getNetworkObjectByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editNetworkObject(params)
            else:
                raise e

    def editNetworkObjectByName(self, params):
        existing_object = self.getNetworkObjectByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editNetworkObject(params)

    def deleteNetworkObjectByName(self, params):
        existing_object = self.getNetworkObjectByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteNetworkObject(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertNetworkObject', choices=['addNetworkObject', 'deleteNetworkObject', 'editNetworkObject', 'getNetworkObject', 'getNetworkObjectList', 'getNetworkObjectByName', 'upsertNetworkObject', 'editNetworkObjectByName', 'deleteNetworkObjectByName']),
        register_as=dict(type='str'),

        description=dict(type='str'),
        dnsResolution=dict(type='str'),
        filter=dict(type='str'),
        id=dict(type='str'),
        isSystemDefined=dict(type='bool'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        sort=dict(type='str'),
        subType=dict(type='str'),
        type=dict(type='str'),
        value=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = NetworkObjectResource(conn)

        resource_method_to_call = getattr(resource, params['operation'])
        response = resource_method_to_call(params)

        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
