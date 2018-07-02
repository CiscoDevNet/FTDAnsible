#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: fdm_test_directory
short_description: Manages TestDirectory objects on Cisco FTD devices with FDM
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
  baseDN
    description:
      - A mandatory Unicode string containing the directory tree, common parent, for searching and querying user and group information. For example, cn=users,dc=example,dc=com<br>Field level constraints: cannot be null, cannot have HTML, must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  directoryPassword
    description:
      - A mandatory password for a user with appropriate rights to retrieve directory user and group information.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  directoryUsername
    description:
      - A mandatory Unicode string containing the distinguished username for a user with appropriate rights to retrieve directory user and group information.<br>Field level constraints: cannot be null, cannot have HTML, must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  hostname
    description:
      - A mandatory Unicode string containing the hostname or IP address of the directory server.<br>Field level constraints: cannot be null, must be a valid host (FQDN or IP) or a list of valid hosts, cannot have HTML. (Note: Additional constraints might exist)
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  linaStatusCode
    description:
      - The authentication connection test error or success code returned by the configuration CLI.
  linaStatusMessage
    description:
      - The authentication connection test error or success message returned by the configuration CLI.
  port
    description:
      - The port number used for communications with the server. The default is 389. Use port 636 if you select LDAPS as the encryption method.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  protocol
    description:
      - An enum value that specifies the encryption protocol used to connect and download users and group information. Values can be one of the following. <br>NONE - Do not use encryption, users and group information will be downloaded in clear text. <br>STARTTLS - Use the strongest encryption method supported by the directory server. This option is not supported when using relam for remote access VPN. <br>LDAPS - Use LDAP over SSL.<br>
  realmUUID
    description:
      - A unique string identifier assigned to the realm object by the system when the object is created. This ID is required to retrieve directory password when test connections is triggered from an edit view.
  sslCertString
    description:
      - For Internal use.
  sslCertUUID
    description:
      - UUID of an external certificate, Certificate Authority (CA) certificate required to enable a trusted connection between the system and the directory server.
  statusCode
    description:
      - The authentication connection test error or success code returned by the ADI process.
  statusMessage
    description:
      - The authentication connection test error or success message returned by the ADI process.
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
"""

EXAMPLES = """

- name: Create a TestDirectory
  fdm_test_directory:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addTestDirectory'

    type: "testdirectory"
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


class TestDirectoryResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addTestDirectory(params):
        body_params = dict_subset(params, ['realmUUID', 'hostname', 'directoryUsername', 'directoryPassword', 'port', 'protocol', 'sslCertUUID', 'sslCertString', 'baseDN', 'statusCode', 'statusMessage', 'linaStatusMessage', 'linaStatusCode', 'id', 'type'])

        url = construct_url(params['hostname'], '/action/testrealm')
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

        operation=dict(choices=['addTestDirectory'], required=True),
        register_as=dict(type='str'),

        baseDN=dict(type='str'),
        directoryPassword=dict(type='str'),
        directoryUsername=dict(type='str'),
        hostname=dict(type='str'),
        id=dict(type='str'),
        linaStatusCode=dict(type='int'),
        linaStatusMessage=dict(type='str'),
        port=dict(type='int'),
        protocol=dict(type='str'),
        realmUUID=dict(type='str'),
        sslCertString=dict(type='str'),
        sslCertUUID=dict(type='str'),
        statusCode=dict(type='str'),
        statusMessage=dict(type='str'),
        type=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(TestDirectoryResource, params['operation'])
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
