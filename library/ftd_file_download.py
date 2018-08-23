#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_file_download
short_description: Downloads files from Cisco FTD devices over HTTP(S).
description:
  - Downloads files from Cisco FTD devices including pending changes, disk files, certificates, 
    troubleshoot reports, and backups.
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  operation:
    description:
      - The name of the operation to execute. 
      - Only operations that return a file can be used in this module.
    required: true
  path_params:
    description:
      - Key-value pairs that should be sent as path parameters in a REST API call.
  destination:
    description:
      - Absolute path of where to download the file to.
      - If destination is a directory, the module uses a filename from 'Content-Disposition' header specified by the server. 
    required: true
"""

EXAMPLES = """
- name: Download pending changes
  ftd_file_download:
    operation: 'getdownload'
    path_params:
      objId: 'default'
    destination: /tmp/
"""

RETURN = """
msg:
    description: the error message describing why the module failed
    returned: error
    type: string
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection

try:
    from ansible.module_utils.fdm_swagger_client import OperationField, ValidationError, FILE_MODEL_NAME
    from ansible.module_utils.misc import FtdServerError
    from ansible.module_utils.http import HTTPMethod
except ImportError:
    from module_utils.fdm_swagger_client import OperationField, ValidationError, FILE_MODEL_NAME
    from module_utils.misc import FtdServerError
    from module_utils.http import HTTPMethod


def is_download_operation(op_spec):
    return op_spec[OperationField.METHOD] == HTTPMethod.GET and op_spec[OperationField.MODEL_NAME] == FILE_MODEL_NAME


def main():
    fields = dict(
        operation=dict(type='str', required=True),
        path_params=dict(type='dict'),
        destination=dict(type='path', required=True)
    )
    module = AnsibleModule(argument_spec=fields,
                           supports_check_mode=True)
    params = module.params
    connection = Connection(module._socket_path)

    op_name = params['operation']
    op_spec = connection.get_operation_spec(op_name)
    if op_spec is None:
        module.fail_json(msg='Operation with specified name is not found: %s' % op_name)
    if not is_download_operation(op_spec):
        module.fail_json(
            msg='Invalid download operation: %s. The operation must make GET request and return a file.' %
                op_name)

    try:
        path_params = params['path_params']
        validate_params(connection, op_name, path_params)
        if module.check_mode:
            module.exit_json()
        connection.download_file(op_spec[OperationField.URL], params['destination'], path_params)
        module.exit_json(changed=False)
    except FtdServerError as e:
        module.fail_json(msg='Download request for %s operation failed. Status code: %s. '
                             'Server response: %s' % (op_name, e.code, e.response))
    except ValidationError as e:
        module.fail_json(msg=e.args[0])


def validate(validation_method, field_name, params, op_name, report):
    try:
        is_valid, validation_report = validation_method(op_name, params)
        if not is_valid:
            report[field_name] = validation_report
    except Exception as e:
        report[field_name] = str(e)
    return report


def validate_params(connection, op_name, path_params):
    report = {}

    validate(connection.validate_path_params, 'Invalid path_params provided', path_params, op_name, report)

    if report:
        raise ValidationError(report)


if __name__ == '__main__':
    main()
