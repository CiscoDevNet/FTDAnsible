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
"""

EXAMPLES = """
- name: Download pending changes
  ftd_download:
    object_type: 'pendingChanges'
    object_id: 'default'
    dest: /tmp/
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
from ansible.module_utils.six.moves.urllib.error import HTTPError

DOWNLOADABLE_RESOURCES = {
    'pendingChanges': '/action/pendingchanges/download/{objId}',
    'diskFile': '/action/downloaddiskfile/{objId}',
    'internalCertificate': '/action/downloadinternalcacertificate/{objId}',
    'troubleshoot': '/action/downloadtroubleshoot/{objId}',
    'backup': '/action/downloadbackup/{objId}'
}


def main():
    fields = dict(
        object_type=dict(choices=list(DOWNLOADABLE_RESOURCES.keys()), required=True),
        object_id=dict(type='str', required=True),
        dest=dict(type='path', required=True),
    )
    module = AnsibleModule(argument_spec=fields)
    params = module.params

    conn = Connection(module._socket_path)
    src_url = DOWNLOADABLE_RESOURCES[params['object_type']].format(objId=params['object_id'])
    try:
        conn.download_file(from_url=src_url, to_path=params['dest'])
        module.exit_json(changed=True)
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg="Download request failed. Error message: %s" % str(e))


if __name__ == '__main__':
    main()
