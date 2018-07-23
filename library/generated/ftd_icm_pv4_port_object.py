#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_icm_pv4_port_object
short_description: Manages ICMPv4PortObject objects on Cisco FTD devices
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
      - An optional unicode alphanumeric string containing a description of the Port Object, up to 200 characters. The string cannot include HTML tags<br>Field level constraints: length must be between 0 and 200 (inclusive). (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  icmpv4Code
    description:
      - An enum value that specifies the ICMPv4 code.
  icmpv4Type
    description:
      - An enum value that specifies the ICMPv4 type.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  isSystemDefined
    description:
      - A Boolean value, TRUE or FALSE (the default). The TRUE value indicates that this object is a system defined object
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A mandatory unicode alphanumeric string containing a unique name for the Port Object, from 1 to 128 characters without spaces. The string cannot include HTML tag. The check for duplicates is performed with a case insensitive search.
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
- name: Fetch ICMPv4PortObject with a given name
  ftd_icm_pv4_port_object:
    operation: "getICMPv4PortObjectByName"
    name: "Ansible ICMPv4PortObject"

- name: Create a ICMPv4PortObject
  ftd_icm_pv4_port_object:
    operation: 'addICMPv4PortObject'
    description: "From Ansible with love"
    name: "Ansible ICMPv4PortObject"
    type: "icmpv4portobject"
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


class ICMPv4PortObjectResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addICMPv4PortObject(self, params):
        body_params = dict_subset(params, ['description', 'icmpv4Code', 'icmpv4Type', 'id', 'isSystemDefined', 'name', 'type', 'version'])

        return self._conn.send_request(
            url_path='/object/icmpv4ports',
            http_method='POST',
            body_params=body_params,
        )

    def deleteICMPv4PortObject(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/object/icmpv4ports/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editICMPv4PortObject(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['description', 'icmpv4Code', 'icmpv4Type', 'id', 'isSystemDefined', 'name', 'type', 'version'])

        return self._conn.send_request(
            url_path='/object/icmpv4ports/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getICMPv4PortObject(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/object/icmpv4ports/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getICMPv4PortObjectList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/object/icmpv4ports',
            http_method='GET',
            query_params=query_params,
        )

    def getICMPv4PortObjectByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getICMPv4PortObjectList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertICMPv4PortObject(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addICMPv4PortObject(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getICMPv4PortObjectByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editICMPv4PortObject(params)
            else:
                raise e

    def editICMPv4PortObjectByName(self, params):
        existing_object = self.getICMPv4PortObjectByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editICMPv4PortObject(params)

    def deleteICMPv4PortObjectByName(self, params):
        existing_object = self.getICMPv4PortObjectByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteICMPv4PortObject(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertICMPv4PortObject', choices=['addICMPv4PortObject', 'deleteICMPv4PortObject', 'editICMPv4PortObject', 'getICMPv4PortObject', 'getICMPv4PortObjectList', 'getICMPv4PortObjectByName', 'upsertICMPv4PortObject', 'editICMPv4PortObjectByName', 'deleteICMPv4PortObjectByName']),
        register_as=dict(type='str'),

        description=dict(type='str'),
        filter=dict(type='str'),
        icmpv4Code=dict(type='str'),
        icmpv4Type=dict(type='str'),
        id=dict(type='str'),
        isSystemDefined=dict(type='bool'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        sort=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = ICMPv4PortObjectResource(conn)

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
