#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: fdm_deploy
short_description: Manages deployments on Cisco FTD devices with FDM.
description:
  - Starts a new deployment job and waits until it completes. The status of the job is checked every second. If the job is not
    completed within the defined timeout interval, the module execution fails.
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  hostname:
    description:
      - Specifies the hostname of the FTD device.
    required: true
  access_token:
    description:
      - Specifies the token to access the FTD device.
    required: true
  refresh_token:
    description:
      - Specifies the token to refresh the access token when the current one expires.
    required: true
  timeout:
    description:
      - Specifies the maximum time period in seconds for the job to finish. If the job is not completed, the task fails.
    default: 600      
"""

EXAMPLES = """
- name: Deploy changes
  fdm_deploy:
    hostname: "https://localhost:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
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
import time

from ansible.module_utils.authorization import retry_on_token_expiration
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.http import construct_url, base_headers
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url

DEFAULT_DEPLOYMENT_TIMEOUT = 60 * 10  # 10 minutes
API_DEPLOYMENT_PREFIX = "/operational/deploy"


class DeploymentResource(object):

    @staticmethod
    @retry_on_token_expiration
    def start_deployment(params):
        deployment_url = construct_url(params['hostname'], API_DEPLOYMENT_PREFIX)
        request = open_url(deployment_url, method='POST', headers=base_headers(params['access_token']))
        return json.loads(request.read())['id']

    @staticmethod
    @retry_on_token_expiration
    def fetch_deployment_status(params, job_id):
        deployment_job_url = construct_url(params['hostname'], "%s/%s" % (API_DEPLOYMENT_PREFIX, job_id))
        request = open_url(deployment_job_url, method='GET', headers=base_headers(params['access_token']))
        response = json.loads(request.read())
        return response


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),
        timeout=dict(type='int', default=DEFAULT_DEPLOYMENT_TIMEOUT)
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        job_id = DeploymentResource.start_deployment(params)
        is_job_completed = False
        start = time.time()

        while not is_job_completed:
            time.sleep(1)

            if time.time() > start + params['timeout']:
                module.fail_json(changed=False, msg="Deployment Timeout. The job was not completed within the given time limits.")
                return

            deployment_status = DeploymentResource.fetch_deployment_status(params, job_id)
            is_job_completed = deployment_status['endTime'] != -1

        success = deployment_status['state'] == 'DEPLOYED'
        if success:
            module.exit_json(changed=True, status=deployment_status)
        else:
            module.fail_json(changed=False, msg="Deployment Failed", status=deployment_status)
    except HTTPError as e:
        module.fail_json(changed=False, msg=json.loads(e.read()), error_code=e.code)


if __name__ == '__main__':
    main()
