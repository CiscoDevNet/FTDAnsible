#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_sub_interface
short_description: Manages SubInterface objects on Cisco FTD devices
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
      - An optional UTF-8 sting, from 0 to 200 characters. The string cannot include HTML tags, semi-colons(;), or carriage returns.<br>Field level constraints: length must be between 0 and 200 (inclusive), cannot have HTML, must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  enabled
    description:
      - A mandatory Boolean value, TRUE or FALSE (the default), specifies the administrative status of the Interface. The TRUE value enables the administrative status on the device. The value FALSE disables the administrative status on the device.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  gigabitInterface
    description:
      - An optional Boolean value, TRUE or FALSE (the default). The TRUE value indicates that the interface is a Gigabit Interface. The value FALSE indicates that the interface is not a Gigabit Interface.
  hardwareName
    description:
      - A mandatory UTF-8 string for the PhysicalInterfaces and SubInterfaces, which normally specifies the type of Interface along with the Interface number. The string cannot contain HTML tags.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  ipv4
    description:
      - An optional IPv4 object assigned to an interface in Firepower device manager. This object specifies Interface configuration for an IPv4 address.
  ipv6
    description:
      - An optional IPv6 object assigned to an interface in Firepower device manager. This object specifies Interface configuration for an IPv6 address.
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  linkState
    description:
      - An enum value that specifies whether the Physical Interface link state is UP or DOWN (the default). Link state of an interface is the operational status/running status of the interface. The values can be one of the following. <br> UP - Specifies whether the device is operationally UP. <br> DOWN - Specifies whether the device is operationally DOWN. 
  macAddress
    description:
      - An optional String value, to specify a virtual MAC address. The MAC address must be in the format H.H.H where each H is a 16-bit hexadecimal number. For example, 000C.F142.4CDE<br>Field level constraints: cannot have HTML, must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  managementInterface
    description:
      - An optional Boolean value, TRUE or FALSE (the default). The TRUE value indicates that the interface is a Management Interface. The value FALSE indicates that the interface is not a Management Interface.
  managementOnly
    description:
      - An optional Boolean value, TRUE or FALSE (default value). The TRUE value indicates that the interface is used for management only. FALSE indicates that interface is not used as a management purpose.
  monitorInterface
    description:
      - A mandatory boolean object which specifies if the Interface needs to be monitored or not.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  mtu
    description:
      - A mandatory Integer value, from 64 bytes to 9198 bytes, with a default value being set to 1500. Maximum Transfer Unit (MTU) is the size of the largest network layer protocol unit that can be communicated in a single network transaction.<br>Field level constraints: cannot be null, must be between 64 and 9198 (inclusive). (Note: Additional constraints might exist)
  name
    description:
      - An optional ASCII string, from 0 to 48 characters, representing the name of the interface. The string can only include lower case characters (a-z), numbers (0-9), underscore (_), dot (.), and plus/minus (+,-). The name can only start with an alpha numeric character.
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  sort
    description:
      - The field used to sort the requested object list
  standbyMacAddress
    description:
      - An optional String value, to specify a virtual Standby MAC address. The MAC address must be in the format H.H.H where each H is a 16-bit hexadecimal number.<br>Field level constraints: cannot have HTML, must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  subIntfId
    description:
      - A mandatory numeric value specifying the sub interface id, from 1 to 4294967295. The number of subinterfaces allowed depends on your platform. You cannnot change the ID after you create the subinterface.<br>Field level constraints: cannot be null, must be between 1 and 4294967295 (inclusive). (Note: Additional constraints might exist)
  tenGigabitInterface
    description:
      - An optional Boolean value, TRUE or FALSE (the default). The TRUE value indicates that the interface is a Ten Gigabit Interface. The value FALSE indicates that the interface is not a Ten Gigabit Interface.
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
  vlanId
    description:
      - An optional numeric value specifying the vlan id of the sub-interface, from 1 to 4094. This is used to tag the packets on a subinterface.<br>Field level constraints: must be between 1 and 4094 (inclusive). (Note: Additional constraints might exist)

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch SubInterface with a given name
  ftd_sub_interface:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getSubInterfaceByName"
    name: "Ansible SubInterface"

- name: Create a SubInterface
  ftd_sub_interface:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addSubInterface'

    name: "Ansible SubInterface"
    description: "From Ansible with love"
    type: "subinterface"
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


class SubInterfaceResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addSubInterface(params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['version', 'name', 'description', 'hardwareName', 'monitorInterface', 'ipv4', 'ipv6', 'managementOnly', 'linkState', 'mtu', 'enabled', 'macAddress', 'standbyMacAddress', 'managementInterface', 'tenGigabitInterface', 'gigabitInterface', 'id', 'subIntfId', 'vlanId', 'type'])

        url = construct_url(params['hostname'], '/devices/default/interfaces/{parentId}/subinterfaces', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteSubInterface(params):
        path_params = dict_subset(params, ['parentId', 'objId'])

        url = construct_url(params['hostname'], '/devices/default/interfaces/{parentId}/subinterfaces/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editSubInterface(params):
        path_params = dict_subset(params, ['parentId', 'objId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['version', 'name', 'description', 'hardwareName', 'monitorInterface', 'ipv4', 'ipv6', 'managementOnly', 'linkState', 'mtu', 'enabled', 'macAddress', 'standbyMacAddress', 'managementInterface', 'tenGigabitInterface', 'gigabitInterface', 'id', 'subIntfId', 'vlanId', 'type'])

        url = construct_url(params['hostname'], '/devices/default/interfaces/{parentId}/subinterfaces/{objId}', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getSubInterface(params):
        path_params = dict_subset(params, ['parentId', 'objId'])

        url = construct_url(params['hostname'], '/devices/default/interfaces/{parentId}/subinterfaces/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getSubInterfaceList(params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['offset', 'limit', 'sort', 'filter'])

        url = construct_url(params['hostname'], '/devices/default/interfaces/{parentId}/subinterfaces', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getSubInterfaceByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(SubInterfaceResource.getSubInterfaceList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertSubInterface(params):
        def is_duplicate_name_error(err):
            return err.code == 422 and "Validation failed due to a duplicate name" in str(err.read())

        try:
            return SubInterfaceResource.addSubInterface(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = SubInterfaceResource.getSubInterfaceByName(params)
                params = copy_identity_properties(existing_object, params)
                return SubInterfaceResource.editSubInterface(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editSubInterfaceByName(params):
        existing_object = SubInterfaceResource.getSubInterfaceByName(params)
        params = copy_identity_properties(existing_object, params)
        return SubInterfaceResource.editSubInterface(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteSubInterfaceByName(params):
        existing_object = SubInterfaceResource.getSubInterfaceByName(params)
        params = copy_identity_properties(existing_object, params)
        return SubInterfaceResource.deleteSubInterface(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', default='upsertSubInterface', choices=['addSubInterface', 'deleteSubInterface', 'editSubInterface', 'getSubInterface', 'getSubInterfaceList', 'getSubInterfaceByName', 'upsertSubInterface', 'editSubInterfaceByName', 'deleteSubInterfaceByName']),
        register_as=dict(type='str'),

        at=dict(type='int'),
        description=dict(type='str'),
        enabled=dict(type='bool'),
        filter=dict(type='str'),
        gigabitInterface=dict(type='bool'),
        hardwareName=dict(type='str'),
        id=dict(type='str'),
        ipv4=dict(type='str'),
        ipv6=dict(type='str'),
        limit=dict(type='int'),
        linkState=dict(type='str'),
        macAddress=dict(type='str'),
        managementInterface=dict(type='bool'),
        managementOnly=dict(type='bool'),
        monitorInterface=dict(type='bool'),
        mtu=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        parentId=dict(type='str'),
        sort=dict(type='str'),
        standbyMacAddress=dict(type='str'),
        subIntfId=dict(type='int'),
        tenGigabitInterface=dict(type='bool'),
        type=dict(type='str'),
        version=dict(type='str'),
        vlanId=dict(type='int'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(SubInterfaceResource, params['operation'])
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
