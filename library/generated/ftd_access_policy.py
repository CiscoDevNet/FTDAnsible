#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_access_policy
short_description: Manages AccessPolicy objects on Cisco FTD devices
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
  defaultAction
    description:
      - An optional AccessDefaultAction. Provide an AccessDefaultAction object to set a default action to AccessPolicy.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  identityPolicySetting
    description:
      - An optional IdentityPolicy object. Provide an IdentityPolicy object to associate with the given AccessPolicy.<br>Allowed types are: [IdentityPolicy]
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A string containing the name of the Access Policy. The string should not contain HTML content.
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  securityIntelligence
    description:
      - An optional SecurityIntelligencePolicy. Provide a SecurityIntelligencePolicy object to associate with the given AccessPolicy<br>Field level constraints: requires threat license. (Note: Additional constraints might exist)<br>Allowed types are: [SecurityIntelligencePolicy]
  sort
    description:
      - The field used to sort the requested object list
  sslPolicy
    description:
      - An optional SSLPolicy object. Provide a SSLPolicy object to associate with the given AccessPolicy<br>Allowed types are: [SSLPolicy]
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch AccessPolicy with a given name
  ftd_access_policy:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getAccessPolicyByName"
    name: "Ansible AccessPolicy"
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


class AccessPolicyResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def editAccessPolicy(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['defaultAction', 'id', 'identityPolicySetting', 'name', 'securityIntelligence', 'sslPolicy', 'type', 'version'])

        url = construct_url(params['hostname'], '/policy/accesspolicies/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getAccessPolicy(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/policy/accesspolicies/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getAccessPolicyList(params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        url = construct_url(params['hostname'], '/policy/accesspolicies', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getAccessPolicyByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(AccessPolicyResource.getAccessPolicyList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def editAccessPolicyByName(params):
        existing_object = AccessPolicyResource.getAccessPolicyByName(params)
        params = copy_identity_properties(existing_object, params)
        return AccessPolicyResource.editAccessPolicy(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', choices=['editAccessPolicy', 'getAccessPolicy', 'getAccessPolicyList', 'getAccessPolicyByName', 'editAccessPolicyByName'], required=True),
        register_as=dict(type='str'),

        defaultAction=dict(type='str'),
        filter=dict(type='str'),
        id=dict(type='str'),
        identityPolicySetting=dict(type='dict'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        securityIntelligence=dict(type='dict'),
        sort=dict(type='str'),
        sslPolicy=dict(type='dict'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(AccessPolicyResource, params['operation'])
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
