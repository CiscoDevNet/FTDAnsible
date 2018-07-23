#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_intrusion_policy_rule_update
short_description: Manages IntrusionPolicyRuleUpdate objects on Cisco FTD devices
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
      - The UUID of the IntrusionPolicy to be updated.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  name
    description:
      - A string that represents the name of the object
  ruleConfigs
    description:
      - A set of RuleConfigs representing the IntrusionRule and IntrusionRuleState to be updated.<br>Allowed types are: [IntrusionRuleConfig]
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - The version of the IntrusionPolicy to be updated.
"""

EXAMPLES = """
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

from ansible.module_utils.basic import AnsibleModule, to_text
from ansible.module_utils.http import iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.connection import Connection


class IntrusionPolicyRuleUpdateResource(object):

    def __init__(self, conn):
        self._conn = conn

    def editIntrusionPolicyRuleUpdate(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['id', 'name', 'ruleConfigs', 'type', 'version'])

        return self._conn.send_request(
            url_path='/policy/intrusionpolicies/{objId}/ruleupdates',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )


def main():
    fields = dict(
        operation=dict(type='str', choices=['editIntrusionPolicyRuleUpdate'], required=True),
        register_as=dict(type='str'),

        id=dict(type='str'),
        name=dict(type='str'),
        objId=dict(type='str'),
        ruleConfigs=dict(type='list'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = IntrusionPolicyRuleUpdateResource(conn)

        resource_method_to_call = getattr(resource, params['operation'])
        response = resource_method_to_call(params)

        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
