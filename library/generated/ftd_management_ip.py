#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_management_ip
short_description: Manages ManagementIP objects on Cisco FTD devices
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
  dhcpServerAddressPool
    description:
      - A string which specifies the range of IP addresses that DHCP server can use to assign ip addresses.<br>Field level constraints: must be a valid IP address or IP address range, cannot have HTML. (Note: Additional constraints might exist)
  dhcpServerEnabled
    description:
      - A boolean value, TRUE (the default) or FALSE. The value TRUE enables DHCP server on the Management Interface, so that directly connected clients can obtain their addresses from the DHCP pool. FALSE disables the DHCP server on Management Interface.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  ipv4Address
    description:
      - A mandatory string, if IPv6 is not provided, has 48 characters, specifies the IPv4 address for the Management Interface. The string cannot have HTML tags.<br>Field level constraints: must be a valid IP address, cannot have HTML. (Note: Additional constraints might exist)
  ipv4Gateway
    description:
      - A mandatory string, if IPv4 address is provided, specifies the IPv4 gateway for the Management Interface. The gateway determines how the system can reach the internet to obtain smart licenses, database updates and to reach the management DNS and NTP servers. The string cannot have HTML tags.<br>Field level constraints: must be a valid IP address, cannot have HTML. (Note: Additional constraints might exist)
  ipv4Mode
    description:
      - An enum value for IPv4 that specifies whether to obtain address through DHCP or Static (default value). Values can be one of the following.<br> Static - Manually configure the ip address.<br> DHCP - Obtain the ip address from a DHCP server.
  ipv4NetMask
    description:
      - A mandatory string, if IPv4 address is provided, specifies the IPv4 Netmask for Management Interface. This specifies the network part of the ipv4 address. The string cannot have HTML tags.<br>Field level constraints: must be a valid netmask, cannot have HTML. (Note: Additional constraints might exist)
  ipv6Address
    description:
      - An optional string, if IPv4 address is provided, up to 128 bits normally represented by groups of 16 bits, specifies the IPv6 address for the Management Interface. Another way of representing 128 bit address is to drop the first consecutive sequence of zero groups. The string cannot have HTML tags.<br>Field level constraints: must be a valid IP address, cannot have HTML. (Note: Additional constraints might exist)
  ipv6Gateway
    description:
      - A mandatory string, if IPv6 address is provided, specifies the IPv6 gateway for the Management Interface. The gateway determines how the system can reach the internet to obtain smart licenses, database updates and to reach the management DNS and NTP servers. The string cannot have HTML tags.<br>Field level constraints: must be a valid IP address, cannot have HTML. (Note: Additional constraints might exist)
  ipv6Mode
    description:
      - A mandatory enum value, if IPv6 address is provided, specifies whether to obtain address through DHCP or Static (default value). Values can be one of the following.<br> Static - Manually configure the ip address.<br> DHCP - Obtain the ip address from a DHCP server.
  ipv6Prefix
    description:
      - A mandatory integer object, if IPv6 address is provided, specifies the IPv6 prefix for Management Interface. This number specifies the length of the network part of the address.
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  linkState
    description:
      - An enum value that specifies whether the Physical Interface link state is UP or DOWN (the default). The values can be one of the following. <br> UP - Enables the Physical Interface Link state to UP. <br> DOWN - Enables the Physical interface Link state to DOWN. 
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  routeInternally
    description:
      - A mandatory boolean value, TRUE (the default) or FALSE. The value TRUE enables the management operations like system updates through data Interfaces. The value FALSE uses the management interface to get the updates and management activities on the Firepower device manager.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch ManagementIP with a given name
  ftd_management_ip:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getManagementIPByName"
    name: "Ansible ManagementIP"
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


class ManagementIPResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def editManagementIP(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['dhcpServerAddressPool', 'dhcpServerEnabled', 'id', 'ipv4Address', 'ipv4Gateway', 'ipv4Mode', 'ipv4NetMask', 'ipv6Address', 'ipv6Gateway', 'ipv6Mode', 'ipv6Prefix', 'linkState', 'routeInternally', 'type', 'version'])

        url = construct_url(params['hostname'], '/devicesettings/default/managementips/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getManagementIP(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/devicesettings/default/managementips/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getManagementIPList(params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        url = construct_url(params['hostname'], '/devicesettings/default/managementips', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getManagementIPByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(ManagementIPResource.getManagementIPList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def editManagementIPByName(params):
        existing_object = ManagementIPResource.getManagementIPByName(params)
        params = copy_identity_properties(existing_object, params)
        return ManagementIPResource.editManagementIP(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', choices=['editManagementIP', 'getManagementIP', 'getManagementIPList', 'getManagementIPByName', 'editManagementIPByName'], required=True),
        register_as=dict(type='str'),

        dhcpServerAddressPool=dict(type='str'),
        dhcpServerEnabled=dict(type='bool'),
        filter=dict(type='str'),
        id=dict(type='str'),
        ipv4Address=dict(type='str'),
        ipv4Gateway=dict(type='str'),
        ipv4Mode=dict(type='str'),
        ipv4NetMask=dict(type='str'),
        ipv6Address=dict(type='str'),
        ipv6Gateway=dict(type='str'),
        ipv6Mode=dict(type='str'),
        ipv6Prefix=dict(type='int'),
        limit=dict(type='int'),
        linkState=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        routeInternally=dict(type='bool'),
        sort=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(ManagementIPResource, params['operation'])
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
