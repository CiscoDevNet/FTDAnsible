#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_backup_immediate
short_description: Manages BackupImmediate objects on Cisco FTD devices
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
  backupLocation
    description:
      - The location of the Backup.
  description
    description:
      - An optional Unicode string, from 0 to 200 characters. The string cannot include HTML tags.<br>Field level constraints: length must be between 0 and 200 (inclusive). (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  forceOperation
    description:
      - For Internal use.
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  ipAddress
    description:
      - IP address of actor who initiated a job execution<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  jobHistoryUuid
    description:
      - For Internal use.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  jobName
    description:
      - See derived class.
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - An optional UTF8 string representing the backup name, from 0 to 32 characters. The string cannot include the dot (.) character or HTML tags.<br>Field level constraints: length must be between 0 and 32 (inclusive), must match pattern ^[a-zA-Z0-9][a-zA-Z0-9_+-]*$. (Note: Additional constraints might exist)
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  scheduleType
    description:
      - A mandatory enum value that specifies the type of job schedule. Only allowed value is:<p>IMMEDIATE - the job will be posted when the request is received. <p>Note that the job will be posted in the queue when it is received, but the actual execution can be delayed if other jobs were scheduled for execution at the same time or are being currently processed. After a system restart the job will not be recovered.
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  user
    description:
      - System provided ID of the user who scheduled the job.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch BackupImmediate with a given name
  ftd_backup_immediate:
    operation: "getBackupImmediateByName"
    name: "Ansible BackupImmediate"

- name: Create a BackupImmediate
  ftd_backup_immediate:
    operation: 'addBackupImmediate'
    description: "From Ansible with love"
    name: "Ansible BackupImmediate"
    type: "backupimmediate"
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


class BackupImmediateResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addBackupImmediate(self, params):
        body_params = dict_subset(params, ['backupLocation', 'description', 'forceOperation', 'id', 'ipAddress', 'jobHistoryUuid', 'jobName', 'name', 'scheduleType', 'type', 'user', 'version'])

        return self._conn.send_request(
            url_path='/action/backup',
            http_method='POST',
            body_params=body_params,
        )

    def deleteBackupImmediate(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/action/backup/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editBackupImmediate(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['backupLocation', 'description', 'forceOperation', 'id', 'ipAddress', 'jobHistoryUuid', 'jobName', 'name', 'scheduleType', 'type', 'user', 'version'])

        return self._conn.send_request(
            url_path='/action/backup/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getBackupImmediate(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/action/backup/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getBackupImmediateList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/action/backup',
            http_method='GET',
            query_params=query_params,
        )

    def getBackupImmediateByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getBackupImmediateList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertBackupImmediate(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addBackupImmediate(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getBackupImmediateByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editBackupImmediate(params)
            else:
                raise e

    def editBackupImmediateByName(self, params):
        existing_object = self.getBackupImmediateByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editBackupImmediate(params)

    def deleteBackupImmediateByName(self, params):
        existing_object = self.getBackupImmediateByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteBackupImmediate(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertBackupImmediate', choices=['addBackupImmediate', 'deleteBackupImmediate', 'editBackupImmediate', 'getBackupImmediate', 'getBackupImmediateList', 'getBackupImmediateByName', 'upsertBackupImmediate', 'editBackupImmediateByName', 'deleteBackupImmediateByName']),
        register_as=dict(type='str'),

        backupLocation=dict(type='str'),
        description=dict(type='str'),
        filter=dict(type='str'),
        forceOperation=dict(type='bool'),
        id=dict(type='str'),
        ipAddress=dict(type='str'),
        jobHistoryUuid=dict(type='str'),
        jobName=dict(type='str'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        scheduleType=dict(type='str'),
        sort=dict(type='str'),
        type=dict(type='str'),
        user=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = BackupImmediateResource(conn)

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
