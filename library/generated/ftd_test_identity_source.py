#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_test_identity_source
short_description: Manages TestIdentitySource objects on Cisco FTD devices
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
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  identitySource
    description:
      - The ID of a identity source object that defines the identity source to be tested with the specified credentials<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  password
    description:
      - The password for the specified username<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  statusCode
    description:
      - The status code is '200' only when the identity source responds with an access-accept message to the authentication request
  statusMessage
    description:
      - The status message is 'Successful' only when the identity source responds with an access-accept message to the authentication request
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  username
    description:
      - The username (present on the identity source) to be used in issuing an authentication request to the specified identity source<br>Field level constraints: cannot be null, length must be between 0 and 128 (inclusive), cannot have HTML. (Note: Additional constraints might exist)

extends_documentation_fragment: ftd
"""

EXAMPLES = """

- name: Create a TestIdentitySource
  ftd_test_identity_source:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addTestIdentitySource'

    type: "testidentitysource"
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


class TestIdentitySourceResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addTestIdentitySource(params):
        body_params = dict_subset(params, ['identitySource', 'username', 'password', 'statusCode', 'statusMessage', 'id', 'type'])

        url = construct_url(params['hostname'], '/action/testidentitysource')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(choices=['addTestIdentitySource'], required=True),
        register_as=dict(type='str'),

        id=dict(type='str'),
        identitySource=dict(type='str'),
        password=dict(type='str'),
        statusCode=dict(type='int'),
        statusMessage=dict(type='str'),
        type=dict(type='str'),
        username=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(TestIdentitySourceResource, params['operation'])
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
