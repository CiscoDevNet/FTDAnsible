#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_test_identity_services_engine_connectivity
short_description: Manages TestIdentityServicesEngineConnectivity objects on Cisco FTD devices
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
  ftdCertificateUUID
    description:
      - The internal certificate that the system must provide to Identity Services Engine (ISE) when connecting to ISE or when performing bulk downloads<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  iseLogMessage
    description:
      - The detailed log message returned by the ADI process
  mntCertificateUUID
    description:
      - The trusted CA certificate for the MNT server in the Identity Services Engine (ISE) deployment. If your deployment includes a primary and a secondary MNT node, the CA certificates for both nodes must be signed by the same certificate authority<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  primaryIseServer
    description:
      - The address of the primary Identity Services Engine (ISE) server
  pxGridCertificateUUID
    description:
      - The trusted CA certificate for the pxGrid framework. If your deployment includes a primary and a secondary pxGrid node, the CA certificates for both nodes must be signed by the same certificate authority<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  secondaryIseServer
    description:
      - The address of the optional secondary Identity Services Engine (ISE) server
  secondaryStatusCode
    description:
      - The ISE connection test error or success code returned by the ADI process for the secondary ISE server
  secondaryStatusMessage
    description:
      - The ISE connection test error or success message returned by the ADI process for the secondary ISE server
  statusCode
    description:
      - The ISE connection test error or success code returned by the ADI process
  statusMessage
    description:
      - The ISE connection test error or success message returned by the ADI process
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.

extends_documentation_fragment: ftd
"""

EXAMPLES = """

- name: Create a TestIdentityServicesEngineConnectivity
  ftd_test_identity_services_engine_connectivity:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addTestIdentityServicesEngineConnectivity'

    type: "testidentityservicesengineconnectivity"
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


class TestIdentityServicesEngineConnectivityResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addTestIdentityServicesEngineConnectivity(params):
        body_params = dict_subset(params, ['ftdCertificateUUID', 'id', 'iseLogMessage', 'mntCertificateUUID', 'primaryIseServer', 'pxGridCertificateUUID', 'secondaryIseServer', 'secondaryStatusCode', 'secondaryStatusMessage', 'statusCode', 'statusMessage', 'type'])

        url = construct_url(params['hostname'], '/action/testidentityservicesengineconnectivity')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', choices=['addTestIdentityServicesEngineConnectivity'], required=True),
        register_as=dict(type='str'),

        ftdCertificateUUID=dict(type='str'),
        id=dict(type='str'),
        iseLogMessage=dict(type='str'),
        mntCertificateUUID=dict(type='str'),
        primaryIseServer=dict(type='str'),
        pxGridCertificateUUID=dict(type='str'),
        secondaryIseServer=dict(type='str'),
        secondaryStatusCode=dict(type='str'),
        secondaryStatusMessage=dict(type='str'),
        statusCode=dict(type='str'),
        statusMessage=dict(type='str'),
        type=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(TestIdentityServicesEngineConnectivityResource, params['operation'])
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
