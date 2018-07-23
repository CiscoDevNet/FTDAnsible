#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_manual_nat_rule
short_description: Manages ManualNatRule objects on Cisco FTD devices
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
  description
    description:
      - An optional string that describes the rule<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  destinationInterface
    description:
      - <br>Allowed types are: [PhysicalInterface, SubInterface]
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  interfaceInOriginalDestination
    description:
      - A Boolean object which can be true if it's routed mode only, and translatedDestination must be null, and originalDestinationPort, translatedDestinationPort and sourceInterface fields must all not null.
  interfaceInTranslatedSource
    description:
      - For static NAT, this could be: <ul> <li>If routed mode, True with null in translatedSource, and not-null in originalSourcePort and translatedSourcePort, and destiantionInterface field cannot be null, OR, <li> <li>False with a NetworkObject or NetworkObjectGroup reference in translatedSource </ul> For dynamic NAT, the translatedSource field cannot be null, and to set this field to true, the firewall mode has to be routed and destinationInterface field cannot be null.
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A string containing the name of the ManualNatRule object
  natType
    description:
      - <br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  originalDestination
    description:
      - A NetworkObject or NetworkObjectGroup reference, or null for 'any' destination address.<br>Allowed types are: [NetworkObject, NetworkObjectGroup]
  originalDestinationPort
    description:
      - A reference to TCPPortObject or UDPPortObject that contains single port number. Use null for 'any' port. Note, if specified, all the four port fields should all be either UDP or TCP ports. Additionally, originalDestinationPort and translatedDestinationPort should be either both specified (not null), or both null<br>Allowed types are: [ICMPv4PortObject, ICMPv6PortObject, ProtocolObject, TCPPortObject, UDPPortObject]
  originalSource
    description:
      - A NetworkObject or NetworkObjectGroup reference, or null for 'any' source address.<br>Allowed types are: [NetworkObject, NetworkObjectGroup]
  originalSourcePort
    description:
      - A reference to TCPPortObject or UDPPortObject that contains single port number. Use null for 'any' port. Note, if specified, all the four port fields should all be either UDP or TCP ports. Additionally, originalSourcePort and translatedSourcePort should be either both specified (not null), or both null.<br>Allowed types are: [ICMPv4PortObject, ICMPv6PortObject, ProtocolObject, TCPPortObject, UDPPortObject]
  sort
    description:
      - The field used to sort the requested object list
  sourceInterface
    description:
      - <br>Allowed types are: [PhysicalInterface, SubInterface]
  translatedDestination
    description:
      - A NetworkObject or NetworkObjectGroup reference, note only 'host' or 'IP range' are allowed in the object(s), no 'network' sub-type is allowed.<br>Allowed types are: [NetworkObject, NetworkObjectGroup]
  translatedDestinationPort
    description:
      - A reference to TCPPortObject or UDPPortObject that contains single port number. Use null for 'any' port. Note, if specified, all the four port fields should all be either UDP or TCP ports. Additionally, originalDestinationPort and translatedDestinationPort should be either both specified (not null), or both null.<br>Allowed types are: [ICMPv4PortObject, ICMPv6PortObject, ProtocolObject, TCPPortObject, UDPPortObject]
  translatedSource
    description:
      - A NetworkObject or NetworkObjectGroup reference, note only 'host' or 'IP range' are allowed in the object(s), no 'network' sub-type is allowed.<br>Allowed types are: [NetworkObject, NetworkObjectGroup]
  translatedSourcePort
    description:
      - A reference to TCPPortObject or UDPPortObject that contains single port number. Use null for 'any' port. Note, if specified, all the four port fields should all be either UDP or TCP ports. Additionally, originalSourcePort and translatedSourcePort should be either both specified (not null), or both null.<br>Allowed types are: [ICMPv4PortObject, ICMPv6PortObject, ProtocolObject, TCPPortObject, UDPPortObject]
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  unidirectional
    description:
      - A Boolean object which can be true only for static NAT rule.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch ManualNatRule with a given name
  ftd_manual_nat_rule:
    operation: "getManualNatRuleByName"
    name: "Ansible ManualNatRule"

- name: Create a ManualNatRule
  ftd_manual_nat_rule:
    operation: 'addManualNatRule'
    description: "From Ansible with love"
    name: "Ansible ManualNatRule"
    type: "manualnatrule"
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


class ManualNatRuleResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addManualNatRule(self, params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['description', 'destinationInterface', 'dns', 'enabled', 'id', 'interfaceInOriginalDestination', 'interfaceInTranslatedSource', 'interfaceIPv6', 'name', 'natType', 'netToNet', 'noProxyArp', 'originalDestination', 'originalDestinationPort', 'originalSource', 'originalSourcePort', 'patOptions', 'routeLookup', 'sourceInterface', 'translatedDestination', 'translatedDestinationPort', 'translatedSource', 'translatedSourcePort', 'type', 'unidirectional', 'version'])

        return self._conn.send_request(
            url_path='/policy/manualnatpolicies/{parentId}/manualnatrules',
            http_method='POST',
            body_params=body_params,
            path_params=path_params,
            query_params=query_params,
        )

    def deleteManualNatRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        return self._conn.send_request(
            url_path='/policy/manualnatpolicies/{parentId}/manualnatrules/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editManualNatRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['description', 'destinationInterface', 'dns', 'enabled', 'id', 'interfaceInOriginalDestination', 'interfaceInTranslatedSource', 'interfaceIPv6', 'name', 'natType', 'netToNet', 'noProxyArp', 'originalDestination', 'originalDestinationPort', 'originalSource', 'originalSourcePort', 'patOptions', 'routeLookup', 'sourceInterface', 'translatedDestination', 'translatedDestinationPort', 'translatedSource', 'translatedSourcePort', 'type', 'unidirectional', 'version'])

        return self._conn.send_request(
            url_path='/policy/manualnatpolicies/{parentId}/manualnatrules/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
            query_params=query_params,
        )

    def getManualNatRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        return self._conn.send_request(
            url_path='/policy/manualnatpolicies/{parentId}/manualnatrules/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getManualNatRuleList(self, params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/policy/manualnatpolicies/{parentId}/manualnatrules',
            http_method='GET',
            path_params=path_params,
            query_params=query_params,
        )

    def getManualNatRuleByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getManualNatRuleList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertManualNatRule(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addManualNatRule(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getManualNatRuleByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editManualNatRule(params)
            else:
                raise e

    def editManualNatRuleByName(self, params):
        existing_object = self.getManualNatRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editManualNatRule(params)

    def deleteManualNatRuleByName(self, params):
        existing_object = self.getManualNatRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteManualNatRule(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertManualNatRule', choices=['addManualNatRule', 'deleteManualNatRule', 'editManualNatRule', 'getManualNatRule', 'getManualNatRuleList', 'getManualNatRuleByName', 'upsertManualNatRule', 'editManualNatRuleByName', 'deleteManualNatRuleByName']),
        register_as=dict(type='str'),

        at=dict(type='int'),
        description=dict(type='str'),
        destinationInterface=dict(type='dict'),
        dns=dict(type='bool'),
        enabled=dict(type='bool'),
        filter=dict(type='str'),
        id=dict(type='str'),
        interfaceIPv6=dict(type='bool'),
        interfaceInOriginalDestination=dict(type='bool'),
        interfaceInTranslatedSource=dict(type='bool'),
        limit=dict(type='int'),
        name=dict(type='str'),
        natType=dict(type='str'),
        netToNet=dict(type='bool'),
        noProxyArp=dict(type='bool'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        originalDestination=dict(type='dict'),
        originalDestinationPort=dict(type='dict'),
        originalSource=dict(type='dict'),
        originalSourcePort=dict(type='dict'),
        parentId=dict(type='str'),
        patOptions=dict(type='str'),
        routeLookup=dict(type='bool'),
        sort=dict(type='str'),
        sourceInterface=dict(type='dict'),
        translatedDestination=dict(type='dict'),
        translatedDestinationPort=dict(type='dict'),
        translatedSource=dict(type='dict'),
        translatedSourcePort=dict(type='dict'),
        type=dict(type='str'),
        unidirectional=dict(type='bool'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = ManualNatRuleResource(conn)

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
