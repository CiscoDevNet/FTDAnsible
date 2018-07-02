#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: fdm_system_feed_object
short_description: Manages SystemFeedObject objects on Cisco FTD devices with FDM
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
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  lastUpdate
    description:
      - An ISO8601 string representing the last update time of the feed. The string cannot have space or HTML tags.<br>Field level constraints: must match pattern (^[a-zA-Z0-9_]$)|(^[a-zA-Z0-9_][ a-zA-Z0-9_\.+-]*[a-zA-Z0-9_\.+-]$), cannot have HTML. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A mandatory string representing the Feed Name. The string cannot have spaces or HTML tags.
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  updateFrequency
    description:
      - An enum value that specifies the feed update frequency, set to THIRTY_MINS by default . The values can be one of the following. <br> DISABLED - Disable the update frequency. <br> THRITY_MINS - Update the feeds every 30 mins. <br> ONE_HOUR - Update the feeds every 1 hour. <br> TWO_HOURS - Update the feeds every 2 hours. <br> FOUR_HOURS - Update the feeds every 4 hours. <br> SIX_HOURS - Update the feeds every 6 hours. <br> EIGHT_HOURS - Update the feeds every 8 hours. <br> TWELVE_HOURS - Update the feeds every 12 hours. <br> ONE_DAY - Update the feeds every day.<br> TWO_DAYS - Update the feeds every two days. <br> ONE_WEEK - Update the feeds every one week. 
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch SystemFeedObject with a given name
  fdm_system_feed_object:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getSystemFeedObjectByName"
    name: "Ansible SystemFeedObject"
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


class SystemFeedObjectResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def editSystemFeedObject(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['version', 'name', 'lastUpdate', 'updateFrequency', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/systemfeedobjects/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getSystemFeedObject(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/systemfeedobjects/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getSystemFeedObjectList(params):
        query_params = dict_subset(params, ['offset', 'limit', 'sort', 'filter'])

        url = construct_url(params['hostname'], '/object/systemfeedobjects', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getSystemFeedObjectByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(SystemFeedObjectResource.getSystemFeedObjectList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def editSystemFeedObjectByName(params):
        existing_object = SystemFeedObjectResource.getSystemFeedObjectByName(params)
        params = SystemFeedObjectResource.copy_identity_params(existing_object, params)
        return SystemFeedObjectResource.editSystemFeedObject(params)

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

        operation=dict(choices=['editSystemFeedObject', 'getSystemFeedObject', 'getSystemFeedObjectList', 'getSystemFeedObjectByName', 'editSystemFeedObjectByName'], required=True),
        register_as=dict(type='str'),

        filter=dict(type='str'),
        id=dict(type='str'),
        lastUpdate=dict(type='str'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        sort=dict(type='str'),
        type=dict(type='str'),
        updateFrequency=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(SystemFeedObjectResource, params['operation'])
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
