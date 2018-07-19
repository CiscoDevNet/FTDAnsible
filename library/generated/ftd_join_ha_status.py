#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_join_ha_status
short_description: Manages JoinHAStatus jobs on Cisco FTD devices.
description:
  - Starts a new JoinHAStatus job and waits until it completes. The status of the job is checked every second.
    If the job is not completed within the defined timeout interval, the module execution fails.
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  timeout:
    description:
      - Specifies the maximum time period in seconds for the job to finish. If the job is not completed, the task fails.
    default: 600
"""

EXAMPLES = """
- name: Start JoinHAStatus job and wait for its completion
  ftd_join_ha_status:
    timeout: 900
"""

RETURN = """
status:
  description: The last successfully fetched status of the deployment job.
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

from ansible.module_utils.basic import AnsibleModule, to_text
from ansible.module_utils.connection import Connection
from ansible.module_utils.facts.timeout import TimeoutError
from ansible.module_utils.http import wait_for_job_completion, DEFAULT_TIMEOUT
from ansible.module_utils.six.moves.urllib.error import HTTPError


class JoinHAStatusResource(object):

    def __init__(self, conn):
        self._conn = conn

    def start_job(self):
        return self._conn.send_request(
            url_path='/devices/default/action/ha/join',
            http_method='POST',
        )['id']

    def fetch_job_status(self, job_id):
        return self._conn.send_request(
            url_path='/devices/default/action/ha/join/{objId}',
            http_method='GET',
            path_params={'objId': job_id}
        )


def main():
    fields = dict(
        timeout=dict(type='int', default=DEFAULT_TIMEOUT),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = JoinHAStatusResource(conn)

        job_id = resource.start_job()
        job_status = wait_for_job_completion(lambda: resource.fetch_job_status(job_id), params['timeout'])

        if job_status['state'] == 'DEPLOYED':
            module.exit_json(changed=True, status=job_status)
        else:
            module.fail_json(changed=False, msg="JoinHAStatus Failed", status=job_status)
    except TimeoutError:
        module.fail_json(changed=False, msg="JoinHAStatus Timeout. The job was not completed within the given time limits.")
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg), error_code=e.code)


if __name__ == '__main__':
    main()
