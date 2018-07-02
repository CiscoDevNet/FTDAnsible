#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: fdm_policy
short_description: Manages Policy objects on Cisco FTD devices with FDM
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  hostname:
    description:
      - Specifies the hostname of the FTD device.
    required: true
  access_token:
    description:
      - Specifies the token to access the FTD device.
    required: true
  refresh_token:
    description:
      - Specifies the token to refresh the access token when the current one expires.
    required: true
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
  matchCommunityExactly
    description:
      - <br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  metric
    description:
      - <br>Field level constraints: must be between 0 and 4294967295 (inclusive). (Note: Additional constraints might exist)
  name
    description:
      - A string that represents the name of the object
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
"""

EXAMPLES = """
- name: Fetch Policy with a given name
  fdm_policy:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getPolicyByName"
    name: "Ansible Policy"
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
from ansible.module_utils.misc import dict_subset, construct_module_result
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class PolicyResource(object):
    
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
    def getPolicyByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(PolicyResource.getPolicyList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(choices=['addPolicyList', 'deletePolicyList', 'editPolicyList', 'getPolicyList', 'getPolicyByName'], required=True),
        register_as=dict(type='str'),

        action=dict(type='str'),
        asPathLists=dict(type='list'),
        communityLists=dict(type='list'),
        description=dict(type='str'),
        id=dict(type='str'),
        interfaces=dict(type='list'),
        ipv4PrefixListAddresses=dict(type='list'),
        ipv4PrefixListNextHops=dict(type='list'),
        ipv4PrefixListRouteSources=dict(type='list'),
        matchCommunityExactly=dict(type='bool'),
        metric=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
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
        method_to_call = getattr(PolicyResource, params['operation'])
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
