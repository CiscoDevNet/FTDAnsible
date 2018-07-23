#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_any_connect_packages
short_description: Manages AnyConnectPackages objects on Cisco FTD devices
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
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A string that represents the name of the object
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  packageFiles
    description:
      - A mandatory list of AnyConnectPackageFile objects. The list must specify at least one package. You can specify at most one package per platform type (LINUX, WINDOWS, MACOS) as defined in the AnyConnectPackageFile object.<br>Allowed types are: [AnyConnectPackageFile]
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch AnyConnectPackages with a given name
  ftd_any_connect_packages:
    operation: "getAnyConnectPackagesByName"
    name: "Ansible AnyConnectPackages"

- name: Create a AnyConnectPackages
  ftd_any_connect_packages:
    operation: 'addAnyConnectPackages'
    name: "Ansible AnyConnectPackages"
    type: "anyconnectpackages"
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


class AnyConnectPackagesResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addAnyConnectPackages(self, params):
        body_params = dict_subset(params, ['id', 'name', 'packageFiles', 'type', 'version'])

        return self._conn.send_request(
            url_path='/devices/default/anyconnectpackages',
            http_method='POST',
            body_params=body_params,
        )

    def deleteAnyConnectPackages(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/devices/default/anyconnectpackages/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editAnyConnectPackages(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['id', 'name', 'packageFiles', 'type', 'version'])

        return self._conn.send_request(
            url_path='/devices/default/anyconnectpackages/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getAnyConnectPackages(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/devices/default/anyconnectpackages/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getAnyConnectPackagesList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/devices/default/anyconnectpackages',
            http_method='GET',
            query_params=query_params,
        )

    def getAnyConnectPackagesByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getAnyConnectPackagesList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertAnyConnectPackages(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addAnyConnectPackages(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getAnyConnectPackagesByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editAnyConnectPackages(params)
            else:
                raise e

    def editAnyConnectPackagesByName(self, params):
        existing_object = self.getAnyConnectPackagesByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editAnyConnectPackages(params)

    def deleteAnyConnectPackagesByName(self, params):
        existing_object = self.getAnyConnectPackagesByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteAnyConnectPackages(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertAnyConnectPackages', choices=['addAnyConnectPackages', 'deleteAnyConnectPackages', 'editAnyConnectPackages', 'getAnyConnectPackages', 'getAnyConnectPackagesList', 'getAnyConnectPackagesByName', 'upsertAnyConnectPackages', 'editAnyConnectPackagesByName', 'deleteAnyConnectPackagesByName']),
        register_as=dict(type='str'),

        filter=dict(type='str'),
        id=dict(type='str'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        packageFiles=dict(type='list'),
        sort=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = AnyConnectPackagesResource(conn)

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
