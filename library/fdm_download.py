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
    response, info = fetch_url(module, url, headers=base_headers(params['access_token']), method='GET')
    return response, info


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        object_type=dict(choices=list(DOWNLOADABLE_RESOURCES.keys()), required=True),
        object_id=dict(type='str', required=True),
        dest_file=dict(type='str', required=True),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    response, info = url_get(params, module)
    if info['status'] != 200:
        module.fail_json(msg="Download request failed", status_code=info['status'], response=info['msg'])
    else:
        with open(params['dest_file'], "wb") as output_file:
            shutil.copyfileobj(response, output_file)
        module.exit_json(changed=True)


if __name__ == '__main__':
    main()
