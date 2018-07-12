#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_geolocation_update_schedule
short_description: Manages GeolocationUpdateSchedule objects on Cisco FTD devices
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
  description
    description:
      - An optional String value containing description about the Geolocaiton update activity.<br>Field level constraints: length must be between 0 and 200 (inclusive), cannot have HTML. (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  forceOperation
    description:
      - For Internal use.
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  jobHistoryUuid
    description:
      - For Internal use.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  jobName
    description:
      - See derived class.
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A String containing the user provided identifier associated with a scheduled activity.<br>Field level constraints: length must be between 0 and 32 (inclusive), must match pattern ^[a-zA-Z0-9][a-zA-Z0-9_+-]*$, cannot have HTML. (Note: Additional constraints might exist)
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  runTimes
    description:
      - A mandatory UTF8 string containing a cron specification (following the Java(tm)/Spring(tm) conventions).<p>The string must contain six space-separated fields representing the seconds, minutes, hours, dayOfTheMonth, month, dayOfTheWeek, year (time is in UTC). Depending on the scheduleType some values are not allowed. For the SINGLE schedule type the following constraints apply:seconds = 0; minutes: 0-59, hours: 0-23, dayOfTheMonth:1-31, month: 1-12, dayOfTheWeek: ?, year: 2017-2099. If the date/time is in the past (with respect to the time when the request is processed), the job is not scheduled.<br>For the DAILY schedule type the following constraints apply: seconds = 0; minutes: 0-59, hours: 0-23, dayOfTheMonth: *, month: *, dayOfTheWeek: *, year: .<br>For the WEEKLY schedule type the following constraints apply: seconds = 0; minutes: 0-59, hours: 0-23, dayOfTheMonth: *, month: *, dayOfTheWeek: 1-7, year: .<br>For the MONTHLY schedule type the following constraints apply: seconds = 0; minutes: 0-59, hours: 0-23, dayOfTheMonth: 1-31, month: *, dayOfTheWeek: ?, year: .<p>Examples:<br>'0 0 12 * * ? ' - schedule  at 12:00 PM (noon) every day.<p>'0 15 10 15 * ? ' - schedule at 10:15 AM on the 15th day of every month.<br>'0 59 23 31 1 ? 2018' schedule at 11:59 PM on Jan/31 2018.<br>Field level constraints: length must be between 0 and 200 (inclusive), must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  scheduleType
    description:
      - A mandatory enum value that specifies the type of job schedule. Only allowed values are:<p>SINGLE - the job will be posted at the given date and time;<p>DAILY - the job will be posted daily at the given time;<p>WEEKLY - the job will be posted weekly at the given day of the week and given time;<p>MONTHLY - the job will be posted monthly at the given day of the month and given time. Note that the job will be posted -according to the system rules- if the day of the month exceeds the number of days in the current month.<p>Note that the job will be posted in the queue at the given time (or immediately), but the actual execution can be delayed if other jobs were scheduled for execution at the same time or are being currently processed. After a system restart, scheduled job will be reposted. if the system is restarted before a scheduled job is executed, the job will not be recovered if the given date/time is in the past.
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  user
    description:
      - System provided ID of the user who scheduled the job.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch GeolocationUpdateSchedule with a given name
  ftd_geolocation_update_schedule:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getGeolocationUpdateScheduleByName"
    name: "Ansible GeolocationUpdateSchedule"

- name: Create a GeolocationUpdateSchedule
  ftd_geolocation_update_schedule:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addGeolocationUpdateSchedule'

    description: "From Ansible with love"
    name: "Ansible GeolocationUpdateSchedule"
    type: "geolocationupdateschedule"
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
from ansible.module_utils.basic import AnsibleModule, to_text
from ansible.module_utils.http import construct_url, base_headers, iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class GeolocationUpdateScheduleResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addGeolocationUpdateSchedule(params):
        body_params = dict_subset(params, ['description', 'forceOperation', 'id', 'jobHistoryUuid', 'jobName', 'name', 'runTimes', 'scheduleType', 'type', 'user', 'version'])

        url = construct_url(params['hostname'], '/managedentity/geolocationupdateschedules')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteGeolocationUpdateSchedule(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/managedentity/geolocationupdateschedules/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editGeolocationUpdateSchedule(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['description', 'forceOperation', 'id', 'jobHistoryUuid', 'jobName', 'name', 'runTimes', 'scheduleType', 'type', 'user', 'version'])

        url = construct_url(params['hostname'], '/managedentity/geolocationupdateschedules/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getGeolocationUpdateSchedule(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/managedentity/geolocationupdateschedules/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getGeolocationUpdateScheduleList(params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        url = construct_url(params['hostname'], '/managedentity/geolocationupdateschedules', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getGeolocationUpdateScheduleByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(GeolocationUpdateScheduleResource.getGeolocationUpdateScheduleList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertGeolocationUpdateSchedule(params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return GeolocationUpdateScheduleResource.addGeolocationUpdateSchedule(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = GeolocationUpdateScheduleResource.getGeolocationUpdateScheduleByName(params)
                params = copy_identity_properties(existing_object, params)
                return GeolocationUpdateScheduleResource.editGeolocationUpdateSchedule(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editGeolocationUpdateScheduleByName(params):
        existing_object = GeolocationUpdateScheduleResource.getGeolocationUpdateScheduleByName(params)
        params = copy_identity_properties(existing_object, params)
        return GeolocationUpdateScheduleResource.editGeolocationUpdateSchedule(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteGeolocationUpdateScheduleByName(params):
        existing_object = GeolocationUpdateScheduleResource.getGeolocationUpdateScheduleByName(params)
        params = copy_identity_properties(existing_object, params)
        return GeolocationUpdateScheduleResource.deleteGeolocationUpdateSchedule(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', default='upsertGeolocationUpdateSchedule', choices=['addGeolocationUpdateSchedule', 'deleteGeolocationUpdateSchedule', 'editGeolocationUpdateSchedule', 'getGeolocationUpdateSchedule', 'getGeolocationUpdateScheduleList', 'getGeolocationUpdateScheduleByName', 'upsertGeolocationUpdateSchedule', 'editGeolocationUpdateScheduleByName', 'deleteGeolocationUpdateScheduleByName']),
        register_as=dict(type='str'),

        description=dict(type='str'),
        filter=dict(type='str'),
        forceOperation=dict(type='bool'),
        id=dict(type='str'),
        jobHistoryUuid=dict(type='str'),
        jobName=dict(type='str'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        runTimes=dict(type='str'),
        scheduleType=dict(type='str'),
        sort=dict(type='str'),
        type=dict(type='str'),
        user=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(GeolocationUpdateScheduleResource, params['operation'])
        response = method_to_call(params)
        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
