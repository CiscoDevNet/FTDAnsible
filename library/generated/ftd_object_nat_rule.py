#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_object_nat_rule
short_description: Manages ObjectNatRule objects on Cisco FTD devices
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
      - An optional string that describes this NAT rule<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  destinationInterface
    description:
      - The interface through which traffic exits the device<br>Allowed types are: [PhysicalInterface, SubInterface]
  dns
    description:
      - A Boolean value, TRUE or FALSE (the default). If TRUE, the system translates DNS replies based on this NAT rule, if DNS inspection is enabled
  enabled
    description:
      - A Boolean value, TRUE or FALSE (the default). The TRUE value indicates that it is enabled
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  interfaceIPv6
    description:
      - A Boolean value, TRUE or FALSE (the default). This option is not supported, please always set this field to FALSE
  interfaceInTranslatedNetwork
    description:
      - A Boolean value, TRUE or FALSE (the default). If TRUE, the system uses the IP address of destination interface as the translated address (interface PAT)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A mandatory string that defines the name of this NAT rule
  natType
    description:
      - An enum value that specifies the NAT rule type<br>STATIC - A static type.<br>DYNAMIC - A dynamic type<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  netToNet
    description:
      - A Boolean value, TRUE or FALSE (the default). This option is not supported, please always set this option to FALSE
  noProxyArp
    description:
      - A Boolean value, TRUE or FALSE (the default). If TRUE, the system disables proxy ARP for incoming packets to the mapped IP addresses
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  originalNetwork
    description:
      - The network object that contains the source addresses you are translating. This must be a network object (not a group)<br>Allowed types are: [NetworkObject]
  originalPort
    description:
      - An optional TCP or UDP port object that defines the original port, the one you are translating. Do not specify an object if the port does not matter in the translation<br>Allowed types are: [ICMPv4PortObject, ICMPv6PortObject, ProtocolObject, TCPPortObject, UDPPortObject]
  patOptions
    description:
      - Please ignore this field
  routeLookup
    description:
      - A Boolean value, TRUE or FALSE (the default). If TRUE, the system determines the egress interface using a route lookup instead of using the interface specified in the NAT rule
  sort
    description:
      - The field used to sort the requested object list
  sourceInterface
    description:
      - An object to represent the source Interface to filter out traffic that this Nat Rule will apply to<br>Allowed types are: [PhysicalInterface, SubInterface]
  translatedNetwork
    description:
      - The network object or group that contains the mapped address<br>Allowed types are: [NetworkObject, NetworkObjectGroup]
  translatedPort
    description:
      - An optional TCP or UDP port object that defines the translated port, the one you are using to replace the original port. You must use the same protocol type (TCP or UDP) as the object specified in the originalPort<br>Allowed types are: [ICMPv4PortObject, ICMPv6PortObject, ProtocolObject, TCPPortObject, UDPPortObject]
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch ObjectNatRule with a given name
  ftd_object_nat_rule:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getObjectNatRuleByName"
    name: "Ansible ObjectNatRule"

- name: Create a ObjectNatRule
  ftd_object_nat_rule:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addObjectNatRule'

    description: "From Ansible with love"
    name: "Ansible ObjectNatRule"
    type: "objectnatrule"
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
from ansible.module_utils.basic import AnsibleModule, to_text
from ansible.module_utils.http import construct_url, base_headers, iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class ObjectNatRuleResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addObjectNatRule(params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['description', 'destinationInterface', 'dns', 'enabled', 'id', 'interfaceInTranslatedNetwork', 'interfaceIPv6', 'name', 'natType', 'netToNet', 'noProxyArp', 'originalNetwork', 'originalPort', 'patOptions', 'routeLookup', 'sourceInterface', 'translatedNetwork', 'translatedPort', 'type', 'version'])

        url = construct_url(params['hostname'], '/policy/objectnatpolicies/{parentId}/objectnatrules', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteObjectNatRule(params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        url = construct_url(params['hostname'], '/policy/objectnatpolicies/{parentId}/objectnatrules/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editObjectNatRule(params):
        path_params = dict_subset(params, ['objId', 'parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['description', 'destinationInterface', 'dns', 'enabled', 'id', 'interfaceInTranslatedNetwork', 'interfaceIPv6', 'name', 'natType', 'netToNet', 'noProxyArp', 'originalNetwork', 'originalPort', 'patOptions', 'routeLookup', 'sourceInterface', 'translatedNetwork', 'translatedPort', 'type', 'version'])

        url = construct_url(params['hostname'], '/policy/objectnatpolicies/{parentId}/objectnatrules/{objId}', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getObjectNatRule(params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        url = construct_url(params['hostname'], '/policy/objectnatpolicies/{parentId}/objectnatrules/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getObjectNatRuleList(params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        url = construct_url(params['hostname'], '/policy/objectnatpolicies/{parentId}/objectnatrules', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getObjectNatRuleByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(ObjectNatRuleResource.getObjectNatRuleList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertObjectNatRule(params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return ObjectNatRuleResource.addObjectNatRule(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = ObjectNatRuleResource.getObjectNatRuleByName(params)
                params = copy_identity_properties(existing_object, params)
                return ObjectNatRuleResource.editObjectNatRule(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editObjectNatRuleByName(params):
        existing_object = ObjectNatRuleResource.getObjectNatRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return ObjectNatRuleResource.editObjectNatRule(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteObjectNatRuleByName(params):
        existing_object = ObjectNatRuleResource.getObjectNatRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return ObjectNatRuleResource.deleteObjectNatRule(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', default='upsertObjectNatRule', choices=['addObjectNatRule', 'deleteObjectNatRule', 'editObjectNatRule', 'getObjectNatRule', 'getObjectNatRuleList', 'getObjectNatRuleByName', 'upsertObjectNatRule', 'editObjectNatRuleByName', 'deleteObjectNatRuleByName']),
        register_as=dict(type='str'),

        at=dict(type='int'),
        description=dict(type='str'),
        destinationInterface=dict(type='dict'),
        dns=dict(type='bool'),
        enabled=dict(type='bool'),
        filter=dict(type='str'),
        id=dict(type='str'),
        interfaceIPv6=dict(type='bool'),
        interfaceInTranslatedNetwork=dict(type='bool'),
        limit=dict(type='int'),
        name=dict(type='str'),
        natType=dict(type='str'),
        netToNet=dict(type='bool'),
        noProxyArp=dict(type='bool'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        originalNetwork=dict(type='dict'),
        originalPort=dict(type='dict'),
        parentId=dict(type='str'),
        patOptions=dict(type='str'),
        routeLookup=dict(type='bool'),
        sort=dict(type='str'),
        sourceInterface=dict(type='dict'),
        translatedNetwork=dict(type='dict'),
        translatedPort=dict(type='dict'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(ObjectNatRuleResource, params['operation'])
        response = method_to_call(params)
        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
