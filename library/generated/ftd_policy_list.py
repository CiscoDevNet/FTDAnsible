#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_policy_list
short_description: Manages PolicyList objects on Cisco FTD devices
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
      - <br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  asPathLists
    description:
      - <br>Allowed types are: [ASPathList]
  communityLists
    description:
      - <br>Allowed types are: [ExpandedCommunityList, StandardCommunityList]
  description
    description:
      - <br>Field level constraints: length must be between 0 and 200 (inclusive), cannot have HTML. (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  interfaces
    description:
      - <br>Allowed types are: [BridgeGroupInterface, PhysicalInterface, SubInterface]
  ipv4PrefixListAddresses
    description:
      - <br>Allowed types are: [IPV4PrefixList]
  ipv4PrefixListNextHops
    description:
      - <br>Allowed types are: [IPV4PrefixList]
  ipv4PrefixListRouteSources
    description:
      - <br>Allowed types are: [IPV4PrefixList]
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  matchCommunityExactly
    description:
      - <br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  metric
    description:
      - <br>Field level constraints: must be between 0 and 4294967295 (inclusive). (Note: Additional constraints might exist)
  name
    description:
      - A string that represents the name of the object
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  sort
    description:
      - The field used to sort the requested object list
  standardAccessListAddresses
    description:
      - <br>Allowed types are: [StandardAccessList]
  standardAccessListNextHops
    description:
      - <br>Allowed types are: [StandardAccessList]
  standardAccessListRouteSources
    description:
      - <br>Allowed types are: [StandardAccessList]
  tag
    description:
      - <br>Field level constraints: must be between 0 and 4294967295 (inclusive). (Note: Additional constraints might exist)
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch PolicyList with a given name
  ftd_policy_list:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getPolicyListByName"
    name: "Ansible PolicyList"

- name: Create a PolicyList
  ftd_policy_list:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addPolicyList'

    name: "Ansible PolicyList"
    description: "From Ansible with love"
    type: "policylist"
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


class PolicyListResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addPolicyList(params):
        body_params = dict_subset(params, ['version', 'name', 'description', 'action', 'interfaces', 'standardAccessListAddresses', 'ipv4PrefixListAddresses', 'standardAccessListNextHops', 'ipv4PrefixListNextHops', 'standardAccessListRouteSources', 'ipv4PrefixListRouteSources', 'asPathLists', 'communityLists', 'matchCommunityExactly', 'metric', 'tag', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/policylists')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deletePolicyList(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/policylists/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editPolicyList(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['version', 'name', 'description', 'action', 'interfaces', 'standardAccessListAddresses', 'ipv4PrefixListAddresses', 'standardAccessListNextHops', 'ipv4PrefixListNextHops', 'standardAccessListRouteSources', 'ipv4PrefixListRouteSources', 'asPathLists', 'communityLists', 'matchCommunityExactly', 'metric', 'tag', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/policylists/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getPolicyList(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/policylists/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getPolicyListList(params):
        query_params = dict_subset(params, ['offset', 'limit', 'sort', 'filter'])

        url = construct_url(params['hostname'], '/object/policylists', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getPolicyListByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(PolicyListResource.getPolicyListList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertPolicyList(params):
        def is_duplicate_name_error(err):
            return err.code == 422 and "Validation failed due to a duplicate name" in str(err.read())

        try:
            return PolicyListResource.addPolicyList(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = PolicyListResource.getPolicyListByName(params)
                params = copy_identity_properties(existing_object, params)
                return PolicyListResource.editPolicyList(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editPolicyListByName(params):
        existing_object = PolicyListResource.getPolicyListByName(params)
        params = copy_identity_properties(existing_object, params)
        return PolicyListResource.editPolicyList(params)

    @staticmethod
    @retry_on_token_expiration
    def deletePolicyListByName(params):
        existing_object = PolicyListResource.getPolicyListByName(params)
        params = copy_identity_properties(existing_object, params)
        return PolicyListResource.deletePolicyList(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', default='upsertPolicyList', choices=['addPolicyList', 'deletePolicyList', 'editPolicyList', 'getPolicyList', 'getPolicyListList', 'getPolicyListByName', 'upsertPolicyList', 'editPolicyListByName', 'deletePolicyListByName']),
        register_as=dict(type='str'),

        action=dict(type='str'),
        asPathLists=dict(type='list'),
        communityLists=dict(type='list'),
        description=dict(type='str'),
        filter=dict(type='str'),
        id=dict(type='str'),
        interfaces=dict(type='list'),
        ipv4PrefixListAddresses=dict(type='list'),
        ipv4PrefixListNextHops=dict(type='list'),
        ipv4PrefixListRouteSources=dict(type='list'),
        limit=dict(type='int'),
        matchCommunityExactly=dict(type='bool'),
        metric=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        sort=dict(type='str'),
        standardAccessListAddresses=dict(type='list'),
        standardAccessListNextHops=dict(type='list'),
        standardAccessListRouteSources=dict(type='list'),
        tag=dict(type='int'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(PolicyListResource, params['operation'])
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
