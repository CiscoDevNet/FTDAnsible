#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_radius_identity_source_group
short_description: Manages RadiusIdentitySourceGroup objects on Cisco FTD devices
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
  activeDirectoryRealm
    description:
      - The Active directory realm which will be used by the radius group for resolving identity<br>Allowed types are: [ActiveDirectoryRealm]
  deadTime
    description:
      - (Optional.) If a server in the group fails, the depletion reactivation mode reactivates failed servers only after all of the servers in the group are inactive. The dead time is the amount of time, between 0 and 1440 minutes, that elapses between the disabling of the last server in the group and the subsequent re-enabling of all servers. The default is 10 minutes.<br>Field level constraints: must be between 0 and 1440 (inclusive). (Note: Additional constraints might exist)
  description
    description:
      - Description of the RADIUS Identity Source group object<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - The ID of the RadiusIdentitySourceGroup<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  maxFailedAttempts
    description:
      - (Optional.) The maximum number of requests sent to a RADIUS server in the group before trying the next server, from 1 to 5. The default is 3.<br>Field level constraints: must be between 1 and 5 (inclusive). (Note: Additional constraints might exist)
  name
    description:
      - The name of the RADIUS Identity Source group object
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  radiusIdentitySources
    description:
      - A comma-delimited list of the names of RadiusIdentitySource objects that are part of this group. A maximum of 15 servers are allowed<br>Allowed types are: [RadiusIdentitySource]
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - radiusidentitysourcegroup
  version
    description:
      - The version of the RadiusIdentitySourceGroup
"""

EXAMPLES = """
- name: Fetch RadiusIdentitySourceGroup with a given name
  ftd_radius_identity_source_group:
    operation: "getRadiusIdentitySourceGroupByName"
    name: "Ansible RadiusIdentitySourceGroup"

- name: Create a RadiusIdentitySourceGroup
  ftd_radius_identity_source_group:
    operation: 'addRadiusIdentitySourceGroup'
    description: "From Ansible with love"
    name: "Ansible RadiusIdentitySourceGroup"
    type: "radiusidentitysourcegroup"
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


class RadiusIdentitySourceGroupResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addRadiusIdentitySourceGroup(self, params):
        body_params = dict_subset(params, ['activeDirectoryRealm', 'deadTime', 'description', 'id', 'maxFailedAttempts', 'name', 'radiusIdentitySources', 'type', 'version'])

        return self._conn.send_request(
            url_path='/object/radiusidentitysourcegroups',
            http_method='POST',
            body_params=body_params,
        )

    def deleteRadiusIdentitySourceGroup(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/object/radiusidentitysourcegroups/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editRadiusIdentitySourceGroup(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['activeDirectoryRealm', 'deadTime', 'description', 'id', 'maxFailedAttempts', 'name', 'radiusIdentitySources', 'type', 'version'])

        return self._conn.send_request(
            url_path='/object/radiusidentitysourcegroups/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getRadiusIdentitySourceGroup(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/object/radiusidentitysourcegroups/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getRadiusIdentitySourceGroupList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/object/radiusidentitysourcegroups',
            http_method='GET',
            query_params=query_params,
        )

    def getRadiusIdentitySourceGroupByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getRadiusIdentitySourceGroupList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertRadiusIdentitySourceGroup(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addRadiusIdentitySourceGroup(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getRadiusIdentitySourceGroupByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editRadiusIdentitySourceGroup(params)
            else:
                raise e

    def editRadiusIdentitySourceGroupByName(self, params):
        existing_object = self.getRadiusIdentitySourceGroupByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editRadiusIdentitySourceGroup(params)

    def deleteRadiusIdentitySourceGroupByName(self, params):
        existing_object = self.getRadiusIdentitySourceGroupByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteRadiusIdentitySourceGroup(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertRadiusIdentitySourceGroup', choices=['addRadiusIdentitySourceGroup', 'deleteRadiusIdentitySourceGroup', 'editRadiusIdentitySourceGroup', 'getRadiusIdentitySourceGroup', 'getRadiusIdentitySourceGroupList', 'getRadiusIdentitySourceGroupByName', 'upsertRadiusIdentitySourceGroup', 'editRadiusIdentitySourceGroupByName', 'deleteRadiusIdentitySourceGroupByName']),
        register_as=dict(type='str'),

        activeDirectoryRealm=dict(type='dict'),
        deadTime=dict(type='int'),
        description=dict(type='str'),
        filter=dict(type='str'),
        id=dict(type='str'),
        limit=dict(type='int'),
        maxFailedAttempts=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        radiusIdentitySources=dict(type='list'),
        sort=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = RadiusIdentitySourceGroupResource(conn)

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
