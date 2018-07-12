#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_ha_configuration
short_description: Manages HAConfiguration objects on Cisco FTD devices
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
  failoverInterface
    description:
      - A dedicated link between two units used for syncing in case of failover. Must be a physical interface<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)<br>Allowed types are: [PhysicalInterface, SubInterface]
  failoverName
    description:
      - A logical name for the failover interface<br>Field level constraints: cannot be null, must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - The name of HA, configured for modeling purpose and cannot be null
  nodeRole
    description:
      - The role of the unit in HA, can be primary or secondary<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  primaryFailoverIPv4
    description:
      - IPv4 address of the primary failover interface<br>Field level constraints: must be a valid IP address. (Note: Additional constraints might exist)
  primaryFailoverIPv6
    description:
      - IPv6 address of the primary failover interface<br>Field level constraints: must be a valid IP address. (Note: Additional constraints might exist)
  primaryStatefulFailoverIPv4
    description:
      - IPv4 address of the primary statefulFailover interface<br>Field level constraints: must be a valid IP address. (Note: Additional constraints might exist)
  primaryStatefulFailoverIPv6
    description:
      - IPv6 address of the primary statefulFailover interface<br>Field level constraints: must be a valid IP address. (Note: Additional constraints might exist)
  secondaryFailoverIPv4
    description:
      - IPv4 address of the secondary failover interface<br>Field level constraints: must be a valid IP address. (Note: Additional constraints might exist)
  secondaryFailoverIPv6
    description:
      - IPv6 address of the secondary failover interface<br>Field level constraints: must be a valid IP address. (Note: Additional constraints might exist)
  secondaryStatefulFailoverIPv4
    description:
      - IPv4 address of the secondary statefulFailover interface<br>Field level constraints: must be a valid IP address. (Note: Additional constraints might exist)
  secondaryStatefulFailoverIPv6
    description:
      - IPv6 address of the secondary statefulFailover interface<br>Field level constraints: must be a valid IP address. (Note: Additional constraints might exist)
  sharedKey
    description:
      - Encrypted shared key used for encryption between the failover interfaces
  sort
    description:
      - The field used to sort the requested object list
  statefulFailoverInterface
    description:
      - A dedicated interface used to pass the connection state information during a failover<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)<br>Allowed types are: [PhysicalInterface, SubInterface]
  statefulFailoverName
    description:
      - A logical name for the statefulFailover interface<br>Field level constraints: cannot be null, must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch HAConfiguration with a given name
  ftd_ha_configuration:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getHAConfigurationByName"
    name: "Ansible HAConfiguration"
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


class HAConfigurationResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def editHAConfiguration(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['failoverInterface', 'failoverName', 'id', 'name', 'nodeRole', 'primaryFailoverIPv4', 'primaryFailoverIPv6', 'primaryStatefulFailoverIPv4', 'primaryStatefulFailoverIPv6', 'secondaryFailoverIPv4', 'secondaryFailoverIPv6', 'secondaryStatefulFailoverIPv4', 'secondaryStatefulFailoverIPv6', 'sharedKey', 'statefulFailoverInterface', 'statefulFailoverName', 'type', 'version'])

        url = construct_url(params['hostname'], '/devices/default/ha/configurations/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getHAConfiguration(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/devices/default/ha/configurations/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getHAConfigurationList(params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        url = construct_url(params['hostname'], '/devices/default/ha/configurations', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getHAConfigurationByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(HAConfigurationResource.getHAConfigurationList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def editHAConfigurationByName(params):
        existing_object = HAConfigurationResource.getHAConfigurationByName(params)
        params = copy_identity_properties(existing_object, params)
        return HAConfigurationResource.editHAConfiguration(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', choices=['editHAConfiguration', 'getHAConfiguration', 'getHAConfigurationList', 'getHAConfigurationByName', 'editHAConfigurationByName'], required=True),
        register_as=dict(type='str'),

        failoverInterface=dict(type='dict'),
        failoverName=dict(type='str'),
        filter=dict(type='str'),
        id=dict(type='str'),
        limit=dict(type='int'),
        name=dict(type='str'),
        nodeRole=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        primaryFailoverIPv4=dict(type='str'),
        primaryFailoverIPv6=dict(type='str'),
        primaryStatefulFailoverIPv4=dict(type='str'),
        primaryStatefulFailoverIPv6=dict(type='str'),
        secondaryFailoverIPv4=dict(type='str'),
        secondaryFailoverIPv6=dict(type='str'),
        secondaryStatefulFailoverIPv4=dict(type='str'),
        secondaryStatefulFailoverIPv6=dict(type='str'),
        sharedKey=dict(type='str'),
        sort=dict(type='str'),
        statefulFailoverInterface=dict(type='dict'),
        statefulFailoverName=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(HAConfigurationResource, params['operation'])
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
