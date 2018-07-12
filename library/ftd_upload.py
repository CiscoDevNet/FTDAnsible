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
      
extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Upload disk file
  ftd_upload:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'

    object_type: 'diskFile'
    src: /tmp/test.txt
"""

RETURN = """
status:
    description: the HTTP status code from the request that failed
    returned: error
    type: int
    sample: 500
response:
    description: the HTTP message from the request that failed
    returned: error
    type: string
"""
import json

from ansible.module_utils.authorization import retry_on_token_expiration
from ansible.module_utils.basic import AnsibleModule, to_text
from ansible.module_utils.http import construct_url
from ansible.module_utils.misc import construct_module_result
from ansible.module_utils.urls import fetch_url
from urllib3 import encode_multipart_formdata
from urllib3.fields import RequestField

UPLOADABLE_RESOURCES = {
    'diskFile': '/action/uploaddiskfile',
    'backup': '/action/uploadbackup',
    'upgrade': '/action/uploadupgrade'
}


@retry_on_token_expiration
def post_file(params, module, file):
    url = construct_url(params['hostname'], UPLOADABLE_RESOURCES[params['object_type']])

    rf = RequestField('fileToUpload', file.read(), 'test.txt')
    rf.make_multipart()
    body, content_type = encode_multipart_formdata([rf])

    headers = {
        'Authorization': 'Bearer %s' % params['access_token'],
        'Content-Type': content_type,
        'Content-Length': len(body)
    }
    return fetch_url(module, url, data=body, headers=headers, method='POST')


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        object_type=dict(choices=list(UPLOADABLE_RESOURCES.keys()), required=True),
        src=dict(type='path', required=True),
        register_as=dict(type='str'),
    )
    module = AnsibleModule(argument_spec=fields)
    params = module.params

    with open(params['src'], 'rb') as src_file:
        response, response_info = post_file(params, module, src_file)
        if response_info['status'] != 200:
            module.fail_json(msg="Upload request failed", status_code=response_info['status'], response=response_info['body'])
        else:
            content = to_text(response.read())
            result = construct_module_result(json.loads(content), params)
            module.exit_json(**result)


if __name__ == '__main__':
    main()
