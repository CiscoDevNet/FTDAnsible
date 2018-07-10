#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_port_object
short_description: Manages PortObject objects on Cisco FTD devices
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
  description
    description:
      - An optional unicode alphanumeric string containing a description of the Port Object, up to 200 characters. The string cannot include HTML tags<br>Field level constraints: length must be between 0 and 200 (inclusive), cannot have HTML. (Note: Additional constraints might exist)
  icmpv4Code
    description:
      - An enum value that specifies the ICMPv4 code.
  icmpv4Type
    description:
      - An enum value that specifies the ICMPv4 type.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  icmpv6Code
    description:
      - An enum value that specifies the ICMPv6 code.
  icmpv6Type
    description:
      - An enum value that specifies the ICMPv6 type.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  isSystemDefined
    description:
      - A Boolean value, TRUE or FALSE (the default). The TRUE value indicates that this object is a system defined object
  name
    description:
      - A mandatory unicode alphanumeric string containing a unique name for the Port Object, from 1 to 128 characters without spaces. The string cannot include HTML tag. The check for duplicates is performed with a case insensitive search.
  port
    description:
      - A mandatory string representing a port or a port range. Valid port numbers are 1 to 65535. To specify a port range, separate the numbers with a hyphen, for example, 22-45. The second port number must be larger than the first port number. The string can only include digits or the hyphen symbol.<br>Field level constraints: cannot be null, must be a valid port from 1 to 65535 or a valid port range, cannot have HTML. (Note: Additional constraints might exist)
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
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

from ansible.module_utils.authorization import retry_on_token_expiration
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.http import construct_url, base_headers, iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class PortObjectResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addICMPv4PortObject(params):
        body_params = dict_subset(params, ['version', 'name', 'description', 'isSystemDefined', 'icmpv4Type', 'icmpv4Code', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/icmpv4ports')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def addICMPv6PortObject(params):
        body_params = dict_subset(params, ['version', 'name', 'description', 'isSystemDefined', 'icmpv6Type', 'icmpv6Code', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/icmpv6ports')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def addTCPPortObject(params):
        body_params = dict_subset(params, ['version', 'name', 'description', 'isSystemDefined', 'port', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/tcpports')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def addUDPPortObject(params):
        body_params = dict_subset(params, ['version', 'name', 'description', 'isSystemDefined', 'port', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/udpports')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteICMPv4PortObject(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/icmpv4ports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteICMPv6PortObject(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/icmpv6ports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteTCPPortObject(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/tcpports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteUDPPortObject(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/udpports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editICMPv4PortObject(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['version', 'name', 'description', 'isSystemDefined', 'icmpv4Type', 'icmpv4Code', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/icmpv4ports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editICMPv6PortObject(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['version', 'name', 'description', 'isSystemDefined', 'icmpv6Type', 'icmpv6Code', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/icmpv6ports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editTCPPortObject(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['version', 'name', 'description', 'isSystemDefined', 'port', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/tcpports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editUDPPortObject(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['version', 'name', 'description', 'isSystemDefined', 'port', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/udpports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getICMPv4PortObject(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/icmpv4ports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getICMPv6PortObject(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/icmpv6ports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getTCPPortObject(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/tcpports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getUDPPortObject(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/udpports/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', choices=['addICMPv4PortObject', 'addICMPv6PortObject', 'addTCPPortObject', 'addUDPPortObject', 'deleteICMPv4PortObject', 'deleteICMPv6PortObject', 'deleteTCPPortObject', 'deleteUDPPortObject', 'editICMPv4PortObject', 'editICMPv6PortObject', 'editTCPPortObject', 'editUDPPortObject', 'getICMPv4PortObject', 'getICMPv6PortObject', 'getTCPPortObject', 'getUDPPortObject'], required=True),
        register_as=dict(type='str'),

        description=dict(type='str'),
        icmpv4Code=dict(type='str'),
        icmpv4Type=dict(type='str'),
        icmpv6Code=dict(type='str'),
        icmpv6Type=dict(type='str'),
        id=dict(type='str'),
        isSystemDefined=dict(type='bool'),
        name=dict(type='str'),
        objId=dict(type='str'),
        port=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(PortObjectResource, params['operation'])
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
