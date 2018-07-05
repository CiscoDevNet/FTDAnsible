#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_dns_server_group
short_description: Manages DNSServerGroup objects on Cisco FTD devices
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
  dnsServers
    description:
      - A list of the names of DNSServer objects that belong to this group.<br>Field level constraints: cannot be null, size must be between 1 and 6 (inclusive), must be a valid IP address. (Note: Additional constraints might exist)
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
      - A unique name to identify this group.
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  retries
    description:
      - The number of times, from 0 to 10, to retry the list of DNS servers when the system does not receive a response. The default is 2 retries.<br>Field level constraints: must be between 1 and 10 (inclusive). (Note: Additional constraints might exist)
  searchDomain
    description:
      - The search domain for this group.<br>Field level constraints: length must be between 0 and 255 (inclusive), cannot have HTML, must match pattern ^((([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([a-zA-Z0-9]|[a-zA-Z0-9][A-Za-z0-9\-]*[A-Za-z0-9])|)$. (Note: Additional constraints might exist)
  sort
    description:
      - The field used to sort the requested object list
  systemDefined
    description:
      - A Boolean value, TRUE or FALSE (the default). The TRUE value indicates that this object is a system defined object.
  timeout
    description:
      - The number of seconds, from 1 to 30, to wait before trying the next DNS server. The default is 2 seconds. Each time the system retries the list of servers, this timeout doubles.<br>Field level constraints: must be between 1 and 30 (inclusive). (Note: Additional constraints might exist)
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch DNSServerGroup with a given name
  ftd_dns_server_group:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getDNSServerGroupByName"
    name: "Ansible DNSServerGroup"

- name: Create a DNSServerGroup
  ftd_dns_server_group:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addDNSServerGroup'

    name: "Ansible DNSServerGroup"
    type: "dnsservergroup"
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


class DNSServerGroupResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addDNSServerGroup(params):
        body_params = dict_subset(params, ['version', 'name', 'dnsServers', 'timeout', 'retries', 'searchDomain', 'systemDefined', 'id', 'type'])

        url = construct_url(params['hostname'], '/devicesettings/default/dnsservergroups')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteDNSServerGroup(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/devicesettings/default/dnsservergroups/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editDNSServerGroup(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['version', 'name', 'dnsServers', 'timeout', 'retries', 'searchDomain', 'systemDefined', 'id', 'type'])

        url = construct_url(params['hostname'], '/devicesettings/default/dnsservergroups/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getDNSServerGroup(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/devicesettings/default/dnsservergroups/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getDNSServerGroupList(params):
        query_params = dict_subset(params, ['offset', 'limit', 'sort', 'filter'])

        url = construct_url(params['hostname'], '/devicesettings/default/dnsservergroups', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getDNSServerGroupByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(DNSServerGroupResource.getDNSServerGroupList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertDNSServerGroup(params):
        def is_duplicate_name_error(err):
            return err.code == 422 and "Validation failed due to a duplicate name" in str(err.read())

        try:
            return DNSServerGroupResource.addDNSServerGroup(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = DNSServerGroupResource.getDNSServerGroupByName(params)
                params = copy_identity_properties(existing_object, params)
                return DNSServerGroupResource.editDNSServerGroup(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editDNSServerGroupByName(params):
        existing_object = DNSServerGroupResource.getDNSServerGroupByName(params)
        params = copy_identity_properties(existing_object, params)
        return DNSServerGroupResource.editDNSServerGroup(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteDNSServerGroupByName(params):
        existing_object = DNSServerGroupResource.getDNSServerGroupByName(params)
        params = copy_identity_properties(existing_object, params)
        return DNSServerGroupResource.deleteDNSServerGroup(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(choices=['addDNSServerGroup', 'deleteDNSServerGroup', 'editDNSServerGroup', 'getDNSServerGroup', 'getDNSServerGroupList', 'getDNSServerGroupByName', 'upsertDNSServerGroup', 'editDNSServerGroupByName', 'deleteDNSServerGroupByName'], required=True),
        register_as=dict(type='str'),

        dnsServers=dict(type='list'),
        filter=dict(type='str'),
        id=dict(type='str'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        retries=dict(type='int'),
        searchDomain=dict(type='str'),
        sort=dict(type='str'),
        systemDefined=dict(type='bool'),
        timeout=dict(type='int'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(DNSServerGroupResource, params['operation'])
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
