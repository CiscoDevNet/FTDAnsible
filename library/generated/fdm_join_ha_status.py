#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.authorization import retry_on_token_expiration
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.http import construct_url, base_headers, wait_for_job_completion, DEFAULT_TIMEOUT
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class JoinHAStatusResource(object):

    @staticmethod
    @retry_on_token_expiration
    def start_job(params):
        url = construct_url(params['hostname'], '/devices/default/action/ha/join')
        response = open_url(url, method='POST', headers=base_headers(params['access_token'])).read()
        return json.loads(response)['id']

    @staticmethod
    @retry_on_token_expiration
    def fetch_job_status(params, job_id):
        url = construct_url(params['hostname'], '/devices/default/action/ha/join/{objId}', path_params={'objId': job_id})
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
        job_id = JoinHAStatusResource.start_job(params)
        job_status = wait_for_job_completion(lambda: JoinHAStatusResource.fetch_job_status(params, job_id), params['timeout'])
        if job_status['state'] == 'DEPLOYED':
            module.exit_json(changed=True, status=job_status)
        else:
            module.fail_json(changed=False, msg="JoinHAStatus Failed", status=job_status)
    except TimeoutError:
        module.fail_json(changed=False, msg="JoinHAStatus Timeout. The job was not completed within the given time limits.")
    except HTTPError as e:
        module.fail_json(changed=False, msg=json.loads(e.read()), error_code=e.code)


if __name__ == '__main__':
    main()
