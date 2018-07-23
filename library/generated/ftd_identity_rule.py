#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_identity_rule
short_description: Manages IdentityRule objects on Cisco FTD devices
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
  action
    description:
      - An enum value that specifies authentication action for directory servers. <br> Values can be one of the following. <br> ACTIVE - Use active authenticate to determine user identity and is applied to HTTP traffic only. <br> PASSIVE - Use passive authentication to determine user identity. <br> NO_AUTH - Do not obtain user identity. Identity-based access rules will not be applied to this traffic. These users are marked as No Authentication Required. <br>
  at
    description:
      - An integer representing where to add the new object in the ordered list. Use 0 to add it at the beginning of the list. If not specified, it will be added at the end of the list
  authType
    description:
      - An enum value that specifies active authentication method (type) supported by the directory server. <br> Values can be one of the following. <br> HTTP Basic - Authenticate users using an unencrypted HTTP Basic Authentication (BA) connection. This is the default. Users log in to the network using their browser's default authentication popup window. <br> NTLM - Authenticate users using an NT LAN Manager (NTLM) connection. This setting is available only with AD realm. Users log in to the network using their browser's default authentication popup window, although you can configure IE and Firefox browsers to transparently authenticate using their Windows domain login. <br> HTTP Negotiate - Allow the device to negotiate the method between the user agent (the application the user is using to initiate the traffic flow) and the Active Directory server. Negotiation results in the strongest commonly supported method being used, in order, NTLM, then basic. Users log in to the network using their browser's default authentication popup window. <br> HTTP Response Page - Prompt users to authenticate using a system-provided web page. This is a form of HTTP Basic authentication. <br>
  destinationNetworks
    description:
      - An optional list of network objects or geographical locations that defines the network addresses or locations to match through which the traffic is leaving the device from.<br>Allowed types are: [Continent, Country, GeoLocation, NetworkObject, NetworkObjectGroup]
  destinationPorts
    description:
      - An optional list of port objects that defines the protocols used to match through which the traffic is leaving the device from.<br>Allowed types are: [ICMPv4PortObject, ICMPv6PortObject, ProtocolObject, TCPPortObject, UDPPortObject, PortObjectGroup]
  destinationZones
    description:
      - An optional list of security zones objects containing interfaces to match through which the traffic is leaving the device from.<br>Allowed types are: [SecurityZone, TunnelZone]
  enabled
    description:
      - A Boolean value, TRUE (the default) or FALSE. The TRUE value indicates that the rule is active. FALSE indicates the rule is not active and in use.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  guestAccessFallback
    description:
      - A Boolean value, TRUE or FALSE. The TRUE value indicates to mark the users who fail authentication as Guest users. FALSE indicates the users failing authentication will be marked as Failed Authentication.
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A UTF string containing the name for the identity rule. The string can be up to 120 characters.
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  realm
    description:
      - The directory realm and server that contains the user accounts for the network.<br>Allowed types are: [LDAPRealm, ActiveDirectoryRealm, SpecialRealm]
  ruleId
    description:
      - A unique ID across all Identity rules on a single device.
  sort
    description:
      - The field used to sort the requested object list
  sourceNetworks
    description:
      - An optional list of network objects or geographical locations that defines the network addresses or location to match through which the traffic is entering the device.<br>Allowed types are: [Continent, Country, GeoLocation, NetworkObject, NetworkObjectGroup]
  sourcePorts
    description:
      - An optional list of port objects that defines the protocols used to match through which the traffic is entering the device.<br>Allowed types are: [ICMPv4PortObject, ICMPv6PortObject, ProtocolObject, TCPPortObject, UDPPortObject, PortObjectGroup]
  sourceZones
    description:
      - An optional list of security zones object containing interfaces to match through which the traffic is entering the device.<br>Allowed types are: [SecurityZone, TunnelZone]
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch IdentityRule with a given name
  ftd_identity_rule:
    operation: "getIdentityRuleByName"
    name: "Ansible IdentityRule"

- name: Create a IdentityRule
  ftd_identity_rule:
    operation: 'addIdentityRule'
    name: "Ansible IdentityRule"
    type: "identityrule"
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


class IdentityRuleResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addIdentityRule(self, params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['action', 'authType', 'destinationNetworks', 'destinationPorts', 'destinationZones', 'enabled', 'guestAccessFallback', 'id', 'name', 'realm', 'ruleId', 'sourceNetworks', 'sourcePorts', 'sourceZones', 'type', 'version'])

        return self._conn.send_request(
            url_path='/policy/identitypolicies/{parentId}/identityrules',
            http_method='POST',
            body_params=body_params,
            path_params=path_params,
            query_params=query_params,
        )

    def deleteIdentityRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        return self._conn.send_request(
            url_path='/policy/identitypolicies/{parentId}/identityrules/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editIdentityRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['action', 'authType', 'destinationNetworks', 'destinationPorts', 'destinationZones', 'enabled', 'guestAccessFallback', 'id', 'name', 'realm', 'ruleId', 'sourceNetworks', 'sourcePorts', 'sourceZones', 'type', 'version'])

        return self._conn.send_request(
            url_path='/policy/identitypolicies/{parentId}/identityrules/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
            query_params=query_params,
        )

    def getIdentityRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        return self._conn.send_request(
            url_path='/policy/identitypolicies/{parentId}/identityrules/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getIdentityRuleList(self, params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/policy/identitypolicies/{parentId}/identityrules',
            http_method='GET',
            path_params=path_params,
            query_params=query_params,
        )

    def getIdentityRuleByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getIdentityRuleList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertIdentityRule(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addIdentityRule(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getIdentityRuleByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editIdentityRule(params)
            else:
                raise e

    def editIdentityRuleByName(self, params):
        existing_object = self.getIdentityRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editIdentityRule(params)

    def deleteIdentityRuleByName(self, params):
        existing_object = self.getIdentityRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteIdentityRule(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertIdentityRule', choices=['addIdentityRule', 'deleteIdentityRule', 'editIdentityRule', 'getIdentityRule', 'getIdentityRuleList', 'getIdentityRuleByName', 'upsertIdentityRule', 'editIdentityRuleByName', 'deleteIdentityRuleByName']),
        register_as=dict(type='str'),

        action=dict(type='str'),
        at=dict(type='int'),
        authType=dict(type='str'),
        destinationNetworks=dict(type='list'),
        destinationPorts=dict(type='list'),
        destinationZones=dict(type='list'),
        enabled=dict(type='bool'),
        filter=dict(type='str'),
        guestAccessFallback=dict(type='bool'),
        id=dict(type='str'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        parentId=dict(type='str'),
        realm=dict(type='dict'),
        ruleId=dict(type='int'),
        sort=dict(type='str'),
        sourceNetworks=dict(type='list'),
        sourcePorts=dict(type='list'),
        sourceZones=dict(type='list'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = IdentityRuleResource(conn)

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
