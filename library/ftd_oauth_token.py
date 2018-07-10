#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_auth_token
short_description: Manages token-based authentication on Cisco FTD devices.
description:
  - Receives an access token based on password credentials (username and password) and revokes an existing access token when it 
    is no longer needed. Received access and refreshed tokens are set as Ansible facts named 'access_token' and 'refresh_token'
    correspondingly.
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  operation:
    description:
      - Operation name to execute. Use 'request' to get a new access token and 'revoke' to nullify the existing one.
    required: true
  device_url:
    description:
      - Specifies the base URL of the FTD device.
    required: true
  username:
    description:
      - Username of the user performing the action.
  password:
    description:
      - Password of the user performing the action.
  access_token:
    description:
      - Specifies the token to access the FTD device.
"""

EXAMPLES = """
- name: Obtain access token
  ftd_oauth_token:
    device_url: "https://localhost:8585"
    username: 'USERNAME'
    password: 'PASSWORD'
    operation: 'request'
    
- name: Revoke access token
  ftd_oauth_token:
    device_url: "https://localhost:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'revoke'
"""

RETURN = """
"""
from ansible.module_utils.authorization import request_token, revoke_token
from ansible.module_utils.basic import *
from ansible.module_utils.six.moves.urllib.error import HTTPError


def main():
    fields = dict(
        operation=dict(choices=['request', 'revoke'], required=True),
        device_url=dict(type='str', required=True),
        username=dict(type='str'),
        password=dict(type='str', no_log=True),
        access_token=dict(type='str', no_log=True),
        refresh_token=dict(type='str', no_log=True)
    )

    module = AnsibleModule(argument_spec=fields)

    try:
        if module.params['operation'] == 'request':
            result = request_token(module.params['device_url'], module.params['username'], module.params['password'])
            module.exit_json(changed=True, ansible_facts={
                'access_token': result['access_token'],
                'refresh_token': result['refresh_token']
            })
        else:
            revoke_token(module.params['device_url'], module.params['access_token'], module.params['refresh_token'])
            module.exit_json(changed=True)
    except HTTPError as e:
        err_msg = e.read()
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)


if __name__ == '__main__':
    main()
