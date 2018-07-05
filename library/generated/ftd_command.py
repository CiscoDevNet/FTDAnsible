#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_command
short_description: Manages Command objects on Cisco FTD devices
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
  commandInput
    description:
      - A mandatory utf-8 string, maximum of 1024 characters, specifying the input command that needs to be executed on the device.<br>Field level constraints: cannot be blank or empty, cannot have HTML, length must be between 0 and 1024 (inclusive). (Note: Additional constraints might exist)
  commandOutput
    description:
      - A utf-8 string specifying the output of the command executed.
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  timeOut
    description:
      - An optional long numeric value specifying the time in milliseconds. It specifies the maximum time within which the command executes.
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.

extends_documentation_fragment: ftd
"""

EXAMPLES = """

- name: Create a Command
  ftd_command:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addCommand'

    type: "command"
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


class CommandResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addCommand(params):
        body_params = dict_subset(params, ['commandInput', 'commandOutput', 'timeOut', 'id', 'type'])

        url = construct_url(params['hostname'], '/action/command')
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

        operation=dict(choices=['addCommand'], required=True),
        register_as=dict(type='str'),

        commandInput=dict(type='str'),
        commandOutput=dict(type='str'),
        id=dict(type='str'),
        timeOut=dict(type='int'),
        type=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(CommandResource, params['operation'])
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
