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
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
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

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch IdentityRule with a given name
  ftd_identity_rule:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getIdentityRuleByName"
    name: "Ansible IdentityRule"

- name: Create a IdentityRule
  ftd_identity_rule:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
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

from ansible.module_utils.authorization import retry_on_token_expiration
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.http import construct_url, base_headers, iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class IdentityRuleResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addIdentityRule(params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['version', 'name', 'ruleId', 'sourceZones', 'destinationZones', 'sourceNetworks', 'destinationNetworks', 'sourcePorts', 'destinationPorts', 'realm', 'guestAccessFallback', 'authType', 'action', 'enabled', 'id', 'type'])

        url = construct_url(params['hostname'], '/policy/identitypolicies/{parentId}/identityrules', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteIdentityRule(params):
        path_params = dict_subset(params, ['parentId', 'objId'])

        url = construct_url(params['hostname'], '/policy/identitypolicies/{parentId}/identityrules/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editIdentityRule(params):
        path_params = dict_subset(params, ['parentId', 'objId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['version', 'name', 'ruleId', 'sourceZones', 'destinationZones', 'sourceNetworks', 'destinationNetworks', 'sourcePorts', 'destinationPorts', 'realm', 'guestAccessFallback', 'authType', 'action', 'enabled', 'id', 'type'])

        url = construct_url(params['hostname'], '/policy/identitypolicies/{parentId}/identityrules/{objId}', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIdentityRule(params):
        path_params = dict_subset(params, ['parentId', 'objId'])

        url = construct_url(params['hostname'], '/policy/identitypolicies/{parentId}/identityrules/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIdentityRuleList(params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['offset', 'limit', 'sort', 'filter'])

        url = construct_url(params['hostname'], '/policy/identitypolicies/{parentId}/identityrules', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIdentityRuleByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(IdentityRuleResource.getIdentityRuleList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertIdentityRule(params):
        def is_duplicate_name_error(err):
            return err.code == 422 and "Validation failed due to a duplicate name" in str(err.read())

        try:
            return IdentityRuleResource.addIdentityRule(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = IdentityRuleResource.getIdentityRuleByName(params)
                params = copy_identity_properties(existing_object, params)
                return IdentityRuleResource.editIdentityRule(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editIdentityRuleByName(params):
        existing_object = IdentityRuleResource.getIdentityRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return IdentityRuleResource.editIdentityRule(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteIdentityRuleByName(params):
        existing_object = IdentityRuleResource.getIdentityRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return IdentityRuleResource.deleteIdentityRule(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(choices=['addIdentityRule', 'deleteIdentityRule', 'editIdentityRule', 'getIdentityRule', 'getIdentityRuleList', 'getIdentityRuleByName', 'upsertIdentityRule', 'editIdentityRuleByName', 'deleteIdentityRuleByName'], required=True),
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
        method_to_call = getattr(IdentityRuleResource, params['operation'])
        response = method_to_call(params)
        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = e.read()
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
