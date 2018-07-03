#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: fdm_user
short_description: Manages User objects on Cisco FTD devices with FDM
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
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
  identitySourceId
    description:
      - The ID of the IdentitySource the user is associated with.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A String representing the current user
  newPassword
    description:
      - The new password to use. It is only used when updating user password
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  password
    description:
      - The current password. It is only used when updating user password
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  userPreferences
    description:
      - An Object representing the timezone, UI theme selected by user
  userServiceTypes
    description:
      - Configure the level of access using the service-type. This is an enum value and api consumer can choose from MGMT and RA_VPN
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: fdm
"""

EXAMPLES = """
- name: Fetch User with a given name
  fdm_user:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getUserByName"
    name: "Ansible User"

- name: Create a User
  fdm_user:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addUser'

    name: "Ansible User"
    type: "user"
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
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class UserResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addUser(params):
        body_params = dict_subset(params, ['version', 'name', 'password', 'newPassword', 'userPreferences', 'identitySourceId', 'userServiceTypes', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/users')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteUser(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/users/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editUser(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['version', 'name', 'password', 'newPassword', 'userPreferences', 'identitySourceId', 'userServiceTypes', 'id', 'type'])

        url = construct_url(params['hostname'], '/object/users/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getUser(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/users/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getUserList(params):
        query_params = dict_subset(params, ['offset', 'limit', 'sort', 'filter'])

        url = construct_url(params['hostname'], '/object/users', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getUserByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(UserResource.getUserList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertUser(params):
        def is_duplicate_name_error(err):
            return err.code == 422 and "Validation failed due to a duplicate name" in str(err.read())

        try:
            return UserResource.addUser(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = UserResource.getUserByName(params)
                params = copy_identity_properties(existing_object, params)
                return UserResource.editUser(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editUserByName(params):
        existing_object = UserResource.getUserByName(params)
        params = copy_identity_properties(existing_object, params)
        return UserResource.editUser(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteUserByName(params):
        existing_object = UserResource.getUserByName(params)
        params = copy_identity_properties(existing_object, params)
        return UserResource.deleteUser(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(choices=['addUser', 'deleteUser', 'editUser', 'getUser', 'getUserList', 'getUserByName', 'upsertUser', 'editUserByName', 'deleteUserByName'], required=True),
        register_as=dict(type='str'),

        filter=dict(type='str'),
        id=dict(type='str'),
        identitySourceId=dict(type='str'),
        limit=dict(type='int'),
        name=dict(type='str'),
        newPassword=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        password=dict(type='str'),
        sort=dict(type='str'),
        type=dict(type='str'),
        userPreferences=dict(type='str'),
        userServiceTypes=dict(type='list'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(UserResource, params['operation'])
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
