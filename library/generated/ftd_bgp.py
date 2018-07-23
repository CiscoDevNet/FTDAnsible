#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_bgp
short_description: Manages BGP objects on Cisco FTD devices
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
  addressFamilyIPv4
    description:
      - An instance of type AFIPv4 that represents the address family configuration to configure a routing session using standard IPv4 address prefixes
  addressFamilyIPv6
    description:
      - An instance of type AFIPv6 that represents the address family configuration to configure a routing session using standard IPv6 address prefixes
  asNumber
    description:
      - Unique Autonomous number that enables bgp process. Valid values for autonomous number are from 1-4294967295 and 1.0-XX.YY.<br>Field level constraints: cannot be null, must match pattern [1-9]\d{0,8}|[1-3]\d{9}|4[0-2]\d[0-4]\d[0-6][0-7][0-2]\d[0-5]|(?:(?:[1-9]\d{0,3}|[1-5]\d{4}|6[0-5][0-5][0-3][0-5])\.(?:0|[1-9]\d{0,3}|[1-5]\d{4}|6[0-5][0-5][0-3][0-5])). (Note: Additional constraints might exist)
  asnotationDot
    description:
      - Change the default display and regular expression match format of BGP 4-byte autonomous system numbers from asplain (decimal values) to dot notation. Default value is false.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  bgpBestPath
    description:
      - An instance of type BGPBestPath that represents comparision between similar routes received from external BGP (eBGP) peers during the best path selection process and switch the best path to the route with the lowest router ID.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  bgpGracefulRestart
    description:
      - An instance of type BGPGracefulRestart that enable or disable the BGP graceful restart capability for a BGP neighbor.
  bgpTimers
    description:
      - An instance of type BGPTimers that represents the configuration of timer values for this process.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  description
    description:
      - User defined description for this object.<br>Field level constraints: length must be between 0 and 200 (inclusive). (Note: Additional constraints might exist)
  enforceFirstAs
    description:
      - Allow a BGP routing process to discard updates received from an external BGP (eBGP) peers that do not list their autonomous system (AS) number as the first AS path segment in the AS_PATH attribute of the incoming route. Default value is true.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  fastExternalFallOver
    description:
      - Enable BGP to terminate external BGP sessions of any directly adjacent peer if the link used to reach the peer goes down; without waiting for the hold-down timer to expire. Default value is true.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  logNeighborChanges
    description:
      - Logs the neighbor status. If true, enables the logging of neighbor change messages. Default value is true.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  maxasLimit
    description:
      - Specifies the maximum number of Autonomous system segments allowed. Valid value is from 1 to 254.<br>Field level constraints: must be between 1 and 254 (inclusive). (Note: Additional constraints might exist)
  name
    description:
      - A string that represents the name of the object
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  routerId
    description:
      - Represents a fixed router ID for the local BGP routing process.<br>Field level constraints: must be a valid IP address, must match pattern (?:(?:\d|[1-9]\d{1,2}|2[0-4]\d|25[0-5])\.){3}(?:\d|[1-9]\d{1,2}|2[0-4]\d|25[0-5]). (Note: Additional constraints might exist)
  sort
    description:
      - The field used to sort the requested object list
  transportPathMtuDiscovery
    description:
      - If true, enables BGP to automatically discover the best TCP path MTU for each BGP session. Default value is true.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch BGP with a given name
  ftd_bgp:
    operation: "getBGPByName"
    name: "Ansible BGP"

- name: Create a BGP
  ftd_bgp:
    operation: 'addBGP'
    description: "From Ansible with love"
    name: "Ansible BGP"
    type: "bgp"
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


class BGPResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addBGP(self, params):
        body_params = dict_subset(params, ['addressFamilyIPv4', 'addressFamilyIPv6', 'asnotationDot', 'asNumber', 'bgpBestPath', 'bgpGracefulRestart', 'bgpTimers', 'description', 'enforceFirstAs', 'fastExternalFallOver', 'id', 'logNeighborChanges', 'maxasLimit', 'name', 'routerId', 'transportPathMtuDiscovery', 'type', 'version'])

        return self._conn.send_request(
            url_path='/devices/default/routing/virtualrouters/default/bgp',
            http_method='POST',
            body_params=body_params,
        )

    def deleteBGP(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/devices/default/routing/virtualrouters/default/bgp/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editBGP(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['addressFamilyIPv4', 'addressFamilyIPv6', 'asnotationDot', 'asNumber', 'bgpBestPath', 'bgpGracefulRestart', 'bgpTimers', 'description', 'enforceFirstAs', 'fastExternalFallOver', 'id', 'logNeighborChanges', 'maxasLimit', 'name', 'routerId', 'transportPathMtuDiscovery', 'type', 'version'])

        return self._conn.send_request(
            url_path='/devices/default/routing/virtualrouters/default/bgp/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getBGP(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/devices/default/routing/virtualrouters/default/bgp/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getBGPList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/devices/default/routing/virtualrouters/default/bgp',
            http_method='GET',
            query_params=query_params,
        )

    def getBGPByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getBGPList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertBGP(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addBGP(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getBGPByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editBGP(params)
            else:
                raise e

    def editBGPByName(self, params):
        existing_object = self.getBGPByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editBGP(params)

    def deleteBGPByName(self, params):
        existing_object = self.getBGPByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteBGP(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertBGP', choices=['addBGP', 'deleteBGP', 'editBGP', 'getBGP', 'getBGPList', 'getBGPByName', 'upsertBGP', 'editBGPByName', 'deleteBGPByName']),
        register_as=dict(type='str'),

        addressFamilyIPv4=dict(type='str'),
        addressFamilyIPv6=dict(type='str'),
        asNumber=dict(type='str'),
        asnotationDot=dict(type='bool'),
        bgpBestPath=dict(type='str'),
        bgpGracefulRestart=dict(type='str'),
        bgpTimers=dict(type='str'),
        description=dict(type='str'),
        enforceFirstAs=dict(type='bool'),
        fastExternalFallOver=dict(type='bool'),
        filter=dict(type='str'),
        id=dict(type='str'),
        limit=dict(type='int'),
        logNeighborChanges=dict(type='bool'),
        maxasLimit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        routerId=dict(type='str'),
        sort=dict(type='str'),
        transportPathMtuDiscovery=dict(type='bool'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = BGPResource(conn)

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
