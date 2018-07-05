#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_download
short_description: Downloads files from Cisco FTD devices over HTTP(S).
description:
  - Downloads files from Cisco FTD devices including pending changes, disk files, certificates, 
    troubleshoot reports, and backups.
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  object_type:
    description:
      - Object type to download. Available options are 'pendingChanges', 'diskFile', 'internalCertificate', 
        'troubleshoot' or 'backup'.
    required: true
  object_id:
    description:
      - Identifier of the object to download.
    required: true
  dest:
    description:
      - Absolute path of where to download the file to.
      - If dest is a directory, the server provided filename from 'Content-Disposition' header is used. 
    required: true
      
extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Download pending changes
  ftd_download:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'

    object_type: 'pendingChanges'
    object_id: 'default'
    dest: /tmp/
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
import os
import re
import shutil

from ansible.module_utils.authorization import retry_on_token_expiration
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.http import construct_url, base_headers

DOWNLOADABLE_RESOURCES = {
    'pendingChanges': '/action/pendingchanges/download/{objId}',
    'diskFile': '/action/downloaddiskfile/{objId}',
    'internalCertificate': '/action/downloadinternalcacertificate/{objId}',
    'troubleshoot': '/action/downloadtroubleshoot/{objId}',
    'backup': '/action/downloadbackup/{objId}'
}


@retry_on_token_expiration
def url_get(params, module):
    url = construct_url(params['hostname'], DOWNLOADABLE_RESOURCES[params['object_type']],
                        path_params={'objId': params['object_id']})
    return fetch_url(module, url, headers=base_headers(params['access_token']), method='GET')


def get_file_path(params, response_info):
    def extract_filename_from_headers(headers):
        content_header_regex = r'attachment; ?filename="?([^"]+)'
        match = re.match(content_header_regex, headers['Content-Disposition'])
        if match:
            return match.group(1)
        else:
            raise ValueError("No appropriate Content-Disposition header is specified.")

    if os.path.isdir(params['dest']):
        filename = extract_filename_from_headers(response_info)
        return os.path.join(params['dest'], filename)
    else:
        return params['dest']


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        object_type=dict(choices=list(DOWNLOADABLE_RESOURCES.keys()), required=True),
        object_id=dict(type='str', required=True),
        dest=dict(type='path', required=True),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    response, response_info = url_get(params, module)
    if response_info['status'] != 200:
        module.fail_json(msg="Download request failed", status_code=response_info['status'], response=response_info['body'])
    else:
        with open(get_file_path(params, response_info), "wb") as output_file:
            shutil.copyfileobj(response, output_file)
        module.exit_json(changed=True)


if __name__ == '__main__':
    main()
