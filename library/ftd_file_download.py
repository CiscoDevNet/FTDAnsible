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
  dest:
    description:
      - Absolute path of where to download the file to.
      - If dest is a directory, the module uses a filename from 'Content-Disposition' header specified by the server. 
    required: true
"""

EXAMPLES = """
- name: Download pending changes
  ftd_file_download:
    operation: 'getdownload'
    path_params:
      objId: 'default'
    dest: /tmp/
"""

RETURN = """
msg:
    description: the error message
    returned: error
    type: string
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection

# TODO: remove import workarounds when module_utils are moved to the Ansible core
try:
    from ansible.module_utils.fdm_swagger_client import OperationField, FILE_MODEL_NAME
    from ansible.module_utils.misc import FtdServerError
except ImportError:
    from module_utils.fdm_swagger_client import OperationField, FILE_MODEL_NAME
    from module_utils.misc import FtdServerError


def main():
    fields = dict(
        operation=dict(type='str', required=True),
        path_params=dict(type='dict'),
        dest=dict(type='path', required=True)
    )
    module = AnsibleModule(argument_spec=fields)
    params = module.params
    connection = Connection(module._socket_path)

    op_spec = connection.get_operation_spec(params['operation'])
    if op_spec is None:
        module.fail_json(msg='Operation with specified name is not found: %s' % params['operation'])
    if op_spec[OperationField.MODEL_NAME] != FILE_MODEL_NAME:
        module.fail_json(
            msg='Specified operation is not valid: %s. Selected operation must return a file.' % params['operation'])

    try:
        connection.download_file(op_spec[OperationField.URL], params['dest'], params['path_params'])
        module.exit_json(changed=False)
    except FtdServerError as e:
        module.fail_json(msg='Download request for %s operation failed. Status code: %s. '
                             'Server response: %s' % (params['operation'], e.code, e.response))


if __name__ == '__main__':
    main()
