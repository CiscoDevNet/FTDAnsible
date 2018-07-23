#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_static_route_entry
short_description: Manages StaticRouteEntry objects on Cisco FTD devices
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
  at
    description:
      - An integer representing where to add the new object in the ordered list. Use 0 to add it at the beginning of the list. If not specified, it will be added at the end of the list
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  gateway
    description:
      - The address of the next hop device. Traffic will be sent to this address.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)<br>Allowed types are: [NetworkObject]
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  iface
    description:
      - The device interface through which traffic will be routed. The gateway address must be accessible from this interface.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)<br>Allowed types are: [BridgeGroupInterface, PhysicalInterface, SubInterface]
  ipType
    description:
      - The IP type of the route<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  metricValue
    description:
      - A value between 1 and 254 that represents the administrative distance for this route.<br>Field level constraints: must be between 1 and 255 (inclusive). (Note: Additional constraints might exist)
  name
    description:
      - A string that represents the name of the object
  networks
    description:
      - A list of destination networks for this route.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)<br>Allowed types are: [NetworkObject]
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
- name: Fetch StaticRouteEntry with a given name
  ftd_static_route_entry:
    operation: "getStaticRouteEntryByName"
    name: "Ansible StaticRouteEntry"

- name: Create a StaticRouteEntry
  ftd_static_route_entry:
    operation: 'addStaticRouteEntry'
    name: "Ansible StaticRouteEntry"
    type: "staticrouteentry"
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


class StaticRouteEntryResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addStaticRouteEntry(self, params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['gateway', 'id', 'iface', 'ipType', 'metricValue', 'name', 'networks', 'type', 'version'])

        return self._conn.send_request(
            url_path='/devices/default/routing/{parentId}/staticrouteentries',
            http_method='POST',
            body_params=body_params,
            path_params=path_params,
            query_params=query_params,
        )

    def deleteStaticRouteEntry(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        return self._conn.send_request(
            url_path='/devices/default/routing/{parentId}/staticrouteentries/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editStaticRouteEntry(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['gateway', 'id', 'iface', 'ipType', 'metricValue', 'name', 'networks', 'type', 'version'])

        return self._conn.send_request(
            url_path='/devices/default/routing/{parentId}/staticrouteentries/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
            query_params=query_params,
        )

    def getStaticRouteEntry(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        return self._conn.send_request(
            url_path='/devices/default/routing/{parentId}/staticrouteentries/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getStaticRouteEntryList(self, params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/devices/default/routing/{parentId}/staticrouteentries',
            http_method='GET',
            path_params=path_params,
            query_params=query_params,
        )

    def getStaticRouteEntryByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getStaticRouteEntryList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertStaticRouteEntry(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addStaticRouteEntry(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getStaticRouteEntryByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editStaticRouteEntry(params)
            else:
                raise e

    def editStaticRouteEntryByName(self, params):
        existing_object = self.getStaticRouteEntryByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editStaticRouteEntry(params)

    def deleteStaticRouteEntryByName(self, params):
        existing_object = self.getStaticRouteEntryByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteStaticRouteEntry(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertStaticRouteEntry', choices=['addStaticRouteEntry', 'deleteStaticRouteEntry', 'editStaticRouteEntry', 'getStaticRouteEntry', 'getStaticRouteEntryList', 'getStaticRouteEntryByName', 'upsertStaticRouteEntry', 'editStaticRouteEntryByName', 'deleteStaticRouteEntryByName']),
        register_as=dict(type='str'),

        at=dict(type='int'),
        filter=dict(type='str'),
        gateway=dict(type='dict'),
        id=dict(type='str'),
        iface=dict(type='dict'),
        ipType=dict(type='str'),
        limit=dict(type='int'),
        metricValue=dict(type='int'),
        name=dict(type='str'),
        networks=dict(type='list'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        parentId=dict(type='str'),
        sort=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = StaticRouteEntryResource(conn)

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
