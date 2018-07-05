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
      - An optional string that describes the rule<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  destinationInterface
    description:
      - An InterfaceBase object that is considered as the destination interface. Also known as the 'translated interface' or the 'mapped interface'<br>Allowed types are: [PhysicalInterface, SubInterface]
  dns
    description:
      - A Boolean object that represents an advanced flag that is common to both Manual and Object NAT rules.
  enabled
    description:
      - A Boolean object that represents if Manual or Object NAT rule is active(enabled) or not.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  interfaceIPv6
    description:
      - A Boolean object that represents an advanced flag that is common to both Manual and Object NAT rules.
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
      - A NatType enum object. The possible values for this object are: <br>STATIC <br>DYNAMIC<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  netToNet
    description:
      - A Boolean object that represents an advanced flag that is common to both Manual and Object NAT rules.
  noProxyArp
    description:
      - A Boolean object that represents an advanced flag that is common to both Manual and Object NAT rules.
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
  patOptions
    description:
      - A PatOptions object which is a nested entity for PAT-pool settings. This object must be null if natType is STATIC. For DYNAMIC NAT, null patOptions means no pat-pool option.
  routeLookup
    description:
      - A Boolean object that represents an advanced flag that is common to both Manual and Object NAT rules.
  sort
    description:
      - The field used to sort the requested object list
  sourceInterface
    description:
      - An InterfaceBase object that is considered as the source interface. Also known as the 'original interface' or the 'real interface'<br>Allowed types are: [PhysicalInterface, SubInterface]
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

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch ManualNatRule with a given name
  ftd_manual_nat_rule:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getManualNatRuleByName"
    name: "Ansible ManualNatRule"

- name: Create a ManualNatRule
  ftd_manual_nat_rule:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addManualNatRule'

    name: "Ansible ManualNatRule"
    description: "From Ansible with love"
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

from ansible.module_utils.authorization import retry_on_token_expiration
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.http import construct_url, base_headers, iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class ManualNatRuleResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addManualNatRule(params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['version', 'name', 'description', 'sourceInterface', 'destinationInterface', 'natType', 'patOptions', 'netToNet', 'noProxyArp', 'dns', 'interfaceIPv6', 'routeLookup', 'enabled', 'interfaceInOriginalDestination', 'interfaceInTranslatedSource', 'originalSource', 'originalDestination', 'originalSourcePort', 'originalDestinationPort', 'translatedSource', 'translatedDestination', 'translatedSourcePort', 'translatedDestinationPort', 'unidirectional', 'id', 'type'])

        url = construct_url(params['hostname'], '/policy/manualnatpolicies/{parentId}/manualnatrules', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteManualNatRule(params):
        path_params = dict_subset(params, ['parentId', 'objId'])

        url = construct_url(params['hostname'], '/policy/manualnatpolicies/{parentId}/manualnatrules/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editManualNatRule(params):
        path_params = dict_subset(params, ['parentId', 'objId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['version', 'name', 'description', 'sourceInterface', 'destinationInterface', 'natType', 'patOptions', 'netToNet', 'noProxyArp', 'dns', 'interfaceIPv6', 'routeLookup', 'enabled', 'interfaceInOriginalDestination', 'interfaceInTranslatedSource', 'originalSource', 'originalDestination', 'originalSourcePort', 'originalDestinationPort', 'translatedSource', 'translatedDestination', 'translatedSourcePort', 'translatedDestinationPort', 'unidirectional', 'id', 'type'])

        url = construct_url(params['hostname'], '/policy/manualnatpolicies/{parentId}/manualnatrules/{objId}', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getManualNatRule(params):
        path_params = dict_subset(params, ['parentId', 'objId'])

        url = construct_url(params['hostname'], '/policy/manualnatpolicies/{parentId}/manualnatrules/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getManualNatRuleList(params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['offset', 'limit', 'sort', 'filter'])

        url = construct_url(params['hostname'], '/policy/manualnatpolicies/{parentId}/manualnatrules', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getManualNatRuleByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(ManualNatRuleResource.getManualNatRuleList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertManualNatRule(params):
        def is_duplicate_name_error(err):
            return err.code == 422 and "Validation failed due to a duplicate name" in str(err.read())

        try:
            return ManualNatRuleResource.addManualNatRule(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = ManualNatRuleResource.getManualNatRuleByName(params)
                params = copy_identity_properties(existing_object, params)
                return ManualNatRuleResource.editManualNatRule(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editManualNatRuleByName(params):
        existing_object = ManualNatRuleResource.getManualNatRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return ManualNatRuleResource.editManualNatRule(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteManualNatRuleByName(params):
        existing_object = ManualNatRuleResource.getManualNatRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return ManualNatRuleResource.deleteManualNatRule(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(choices=['addManualNatRule', 'deleteManualNatRule', 'editManualNatRule', 'getManualNatRule', 'getManualNatRuleList', 'getManualNatRuleByName', 'upsertManualNatRule', 'editManualNatRuleByName', 'deleteManualNatRuleByName'], required=True),
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
        method_to_call = getattr(ManualNatRuleResource, params['operation'])
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
