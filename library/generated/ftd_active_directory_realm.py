#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_active_directory_realm
short_description: Manages ActiveDirectoryRealm objects on Cisco FTD devices
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
  adPrimaryDomain
    description:
      - A mandatory Unicode alphanumeric string containing fully qualified Active Directory domain name that the device should join. For example, example.com<br>Field level constraints: cannot be null, must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  baseDN
    description:
      - A mandatory Unicode string containing the directory tree, common parent, for searching and querying user and group information. For example, cn=users,dc=example,dc=com<br>Field level constraints: cannot be null, must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  dirPassword
    description:
      - A mandatory password for a user with appropriate rights to retrieve directory user and group information.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  dirUsername
    description:
      - A mandatory Unicode string containing the distinguished username for a user with appropriate rights to retrieve directory user and group information.<br>Field level constraints: cannot be null, must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  directoryConfigurations
    description:
      - A list of directory server properties.
  enabled
    description:
      - A boolean value, TRUE or FALSE (the default). The TRUE value indicates the realm is available for the use by Identity. FALSE indicates the realm is not in use by Identity. Once set to TRUE, it can not be set to FALSE only if Identity feature is enabled.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A UTF string containing the name for the directory realm. The string can be up to 50 characters.
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  realmId
    description:
      - An integer realm ID to differentiate user-defined realm from the two special system defined realms. This must be set to 2.
  sort
    description:
      - The field used to sort the requested object list
  systemDefined
    description:
      - A read only boolean value, TRUE or FALSE (the default). The TRUE value indicates the realm is a special type of realm, created by system. FALSE indicates the realm is user-defined.
  type
    description:
      - identitysourcebase
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch ActiveDirectoryRealm with a given name
  ftd_active_directory_realm:
    operation: "getActiveDirectoryRealmByName"
    name: "Ansible ActiveDirectoryRealm"

- name: Create a ActiveDirectoryRealm
  ftd_active_directory_realm:
    operation: 'addActiveDirectoryRealm'
    name: "Ansible ActiveDirectoryRealm"
    type: "activedirectoryrealm"
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

from ansible.module_utils.basic import AnsibleModule, to_text
from ansible.module_utils.http import iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.connection import Connection


class ActiveDirectoryRealmResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addActiveDirectoryRealm(self, params):
        body_params = dict_subset(params, ['adPrimaryDomain', 'baseDN', 'directoryConfigurations', 'dirPassword', 'dirUsername', 'enabled', 'id', 'name', 'realmId', 'systemDefined', 'type', 'version'])

        return self._conn.send_request(
            url_path='/object/realms',
            http_method='POST',
            body_params=body_params,
        )

    def editActiveDirectoryRealm(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['adPrimaryDomain', 'baseDN', 'directoryConfigurations', 'dirPassword', 'dirUsername', 'enabled', 'id', 'name', 'realmId', 'systemDefined', 'type', 'version'])

        return self._conn.send_request(
            url_path='/object/realms/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getActiveDirectoryRealm(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/object/realms/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getActiveDirectoryRealmList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/object/realms',
            http_method='GET',
            query_params=query_params,
        )

    def getActiveDirectoryRealmByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getActiveDirectoryRealmList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertActiveDirectoryRealm(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addActiveDirectoryRealm(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getActiveDirectoryRealmByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editActiveDirectoryRealm(params)
            else:
                raise e

    def editActiveDirectoryRealmByName(self, params):
        existing_object = self.getActiveDirectoryRealmByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editActiveDirectoryRealm(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertActiveDirectoryRealm', choices=['addActiveDirectoryRealm', 'editActiveDirectoryRealm', 'getActiveDirectoryRealm', 'getActiveDirectoryRealmList', 'getActiveDirectoryRealmByName', 'upsertActiveDirectoryRealm', 'editActiveDirectoryRealmByName']),
        register_as=dict(type='str'),

        adPrimaryDomain=dict(type='str'),
        baseDN=dict(type='str'),
        dirPassword=dict(type='str'),
        dirUsername=dict(type='str'),
        directoryConfigurations=dict(type='list'),
        enabled=dict(type='bool'),
        filter=dict(type='str'),
        id=dict(type='str'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        realmId=dict(type='int'),
        sort=dict(type='str'),
        systemDefined=dict(type='bool'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = ActiveDirectoryRealmResource(conn)

        resource_method_to_call = getattr(resource, params['operation'])
        response = resource_method_to_call(params)

        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
