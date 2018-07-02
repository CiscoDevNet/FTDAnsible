#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: fdm_cloud_communication_settings
short_description: Manages CloudCommunicationSettings objects on Cisco FTD devices with FDM
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
  operation:
    description:
      - Specified the name of the operation to execute in the task.
    required: true
  register_as:
    description:
      - Specifies Ansible fact name that is used to register received response from the FTD device.
  defenseOrchestratorEnabled
    description:
      - A mandatory boolean value, TRUE or FALSE (default value). The value TRUE indicates that Cisco Defense Orchestrator can connect to the device and make REST calls. FALSE will prevent Cisco Defense Orchestrator from communicating with the device.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  sort
    description:
      - The field used to sort the requested object list
  telemetryEnabled
    description:
      - A mandatory boolean value, TRUE or FALSE (default value). The value TRUE enables Cisco Success Network which indicates that the telemetry data will be send to the cloud. FALSE will disable Cisco Success Network that prevents telemetry data from being forwarded. <br> <br> <b>Cisco Success Network enablement provides usage information and statistics to Cisco which are essential for Cisco to provide technical support. This information also allows Cisco to improve the product and to make you aware of unused available features so that you can maximize the value of the product in your network. Check out the Sample Data that will be sent to Cisco.</b><br>
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch CloudCommunicationSettings with a given name
  fdm_cloud_communication_settings:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getCloudCommunicationSettingsByName"
    name: "Ansible CloudCommunicationSettings"
"""

RETURN = """
response:
  description: HTTP response returned from the API call.
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
from ansible.module_utils.http import construct_url, base_headers, iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class CloudCommunicationSettingsResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def editCloudCommunicationSettings(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['version', 'telemetryEnabled', 'defenseOrchestratorEnabled', 'id', 'type'])

        url = construct_url(params['hostname'], '/devicesettings/default/cloudcommunicationsettings/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getCloudCommunicationSettings(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/devicesettings/default/cloudcommunicationsettings/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getCloudCommunicationSettingsList(params):
        query_params = dict_subset(params, ['offset', 'limit', 'sort', 'filter'])

        url = construct_url(params['hostname'], '/devicesettings/default/cloudcommunicationsettings', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getCloudCommunicationSettingsByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(CloudCommunicationSettingsResource.getCloudCommunicationSettingsList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def editCloudCommunicationSettingsByName(params):
        existing_object = CloudCommunicationSettingsResource.getCloudCommunicationSettingsByName(params)
        params = CloudCommunicationSettingsResource.copy_identity_params(existing_object, params)
        return CloudCommunicationSettingsResource.editCloudCommunicationSettings(params)

    @staticmethod
    def copy_identity_params(source_object, dest_params):
        dest_params['objId'] = source_object['id']
        dest_params['id'] = source_object['id']
        if 'version' in source_object:
            dest_params['version'] = source_object['version']
        return dest_params


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(choices=['editCloudCommunicationSettings', 'getCloudCommunicationSettings', 'getCloudCommunicationSettingsList', 'getCloudCommunicationSettingsByName', 'editCloudCommunicationSettingsByName'], required=True),
        register_as=dict(type='str'),

        defenseOrchestratorEnabled=dict(type='bool'),
        filter=dict(type='str'),
        id=dict(type='str'),
        limit=dict(type='int'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        sort=dict(type='str'),
        telemetryEnabled=dict(type='bool'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(CloudCommunicationSettingsResource, params['operation'])
        response = method_to_call(params)
        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = e.read()
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
