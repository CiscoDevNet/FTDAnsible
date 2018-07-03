#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: fdm_deployment
short_description: Manages Deployment jobs on Cisco FTD devices with FDM.
description:
  - Starts a new Deployment job and waits until it completes. The status of the job is checked every second.
    If the job is not completed within the defined timeout interval, the module execution fails.
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  timeout:
    description:
      - Specifies the maximum time period in seconds for the job to finish. If the job is not completed, the task fails.
    default: 600

extends_documentation_fragment: fdm
"""

EXAMPLES = """
- name: Start Deployment job and wait for its completion
  fdm_deployment:
    hostname: "https://localhost:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
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

from ansible.module_utils.authorization import retry_on_token_expiration
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.http import construct_url, base_headers, wait_for_job_completion, DEFAULT_TIMEOUT
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class DeploymentResource(object):

    @staticmethod
    @retry_on_token_expiration
    def start_job(params):
        url = construct_url(params['hostname'], '/operational/deploy')
        response = open_url(url, method='POST', headers=base_headers(params['access_token'])).read()
        return json.loads(response)['id']

    @staticmethod
    @retry_on_token_expiration
    def fetch_job_status(params, job_id):
        url = construct_url(params['hostname'], '/operational/deploy/{objId}', path_params={'objId': job_id})
        response = open_url(url, method='GET', headers=base_headers(params['access_token'])).read()
        return json.loads(response)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),
        timeout=dict(type='int', default=DEFAULT_TIMEOUT),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        job_id = DeploymentResource.start_job(params)
        job_status = wait_for_job_completion(lambda: DeploymentResource.fetch_job_status(params, job_id), params['timeout'])
        if job_status['state'] == 'DEPLOYED':
            module.exit_json(changed=True, status=job_status)
        else:
            module.fail_json(changed=False, msg="Deployment Failed", status=job_status)
    except TimeoutError:
        module.fail_json(changed=False, msg="Deployment Timeout. The job was not completed within the given time limits.")
    except HTTPError as e:
        module.fail_json(changed=False, msg=json.loads(e.read()), error_code=e.code)


if __name__ == '__main__':
    main()
