#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_upload
short_description: Uploads files to Cisco FTD devices over HTTP(S).
description:
  - Uploads files to Cisco FTD devices including disk files, backups, and upgrades.
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  object_type:
    description:
      - Object type to upload. Available options are 'diskFile', 'backup' or 'upgrade'.
    required: true
  src:
    description:
      - Absolute path to the file that should be uploaded.
    required: true
  register_as:
    description:
      - Specifies Ansible fact name that is used to register received response from the FTD device.
"""

EXAMPLES = """
- name: Upload disk file
  ftd_upload:
    object_type: 'diskFile'
    src: /tmp/test.txt
"""

RETURN = """
error_code:
    description: the HTTP status code from the request that failed
    returned: error
    type: int
    sample: 500
msg:
    description: the HTTP message from the request that failed
    returned: error
    type: string
"""
import json

from ansible.module_utils.basic import AnsibleModule, to_text
from ansible.module_utils.connection import Connection
from ansible.module_utils.misc import construct_module_result
from ansible.module_utils.six.moves.urllib.error import HTTPError

UPLOADABLE_RESOURCES = {
    'diskFile': '/action/uploaddiskfile',
    'backup': '/action/uploadbackup',
    'upgrade': '/action/uploadupgrade'
}


def main():
    fields = dict(
        object_type=dict(choices=list(UPLOADABLE_RESOURCES.keys()), required=True),
        src=dict(type='path', required=True),
        register_as=dict(type='str'),
    )
    module = AnsibleModule(argument_spec=fields)
    params = module.params
    conn = Connection(module._socket_path)

    try:
        response = conn.upload_file(from_path=params['src'], to_url=UPLOADABLE_RESOURCES[params['object_type']])
        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg="Upload request failed. Error message: %s" % str(e))


if __name__ == '__main__':
    main()
