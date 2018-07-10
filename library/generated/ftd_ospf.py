#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_ospf
short_description: Manages OSPF objects on Cisco FTD devices
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
  areas
    description:
      - Represents the areas to be configured for this process
  description
    description:
      - <br>Field level constraints: length must be between 0 and 200 (inclusive), cannot have HTML. (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  filterRules
    description:
      - Represents the configuration of filtering incoming or outgoing routes using access control lists
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  logAdjacencyChanges
    description:
      - Represents the way adjacency changes must be logged. If null, disables logging for this process
  name
    description:
      - A string that represents the name of the object
  neighbors
    description:
      - Represents the neighbors to be configured for this process
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  processConfiguration
    description:
      - Represents the advanced configuration for this process
  processId
    description:
      - An identifier for the OSPF Process. Must be in the range 1 - 65535 inclusive.<br>Field level constraints: cannot be null, cannot have HTML, must match pattern \d|[1-9]\d+, must be between 1 and 65535 (inclusive). (Note: Additional constraints might exist)
  redistributeProtocols
    description:
      - Represents the configuration of a list of protocols whose routes are redistributed into this process
  sort
    description:
      - The field used to sort the requested object list
  summaryAddresses
    description:
      - Represents the summary addresses configured for route summarization when redistributing routes into this process. Each object represents the configuration of the advertisement on one summary route for all redistributed routes included for a network address and mask. Use AreaRange under Area to configure route summarization between OSPF areas
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch OSPF with a given name
  ftd_ospf:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getOSPFByName"
    name: "Ansible OSPF"

- name: Create a OSPF
  ftd_ospf:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addOSPF'

    name: "Ansible OSPF"
    description: "From Ansible with love"
    type: "ospf"
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


class OSPFResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addOSPF(params):
        body_params = dict_subset(params, ['version', 'name', 'description', 'processId', 'logAdjacencyChanges', 'processConfiguration', 'areas', 'neighbors', 'summaryAddresses', 'filterRules', 'redistributeProtocols', 'id', 'type'])

        url = construct_url(params['hostname'], '/devices/default/routing/virtualrouters/default/ospf')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteOSPF(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/devices/default/routing/virtualrouters/default/ospf/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editOSPF(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['version', 'name', 'description', 'processId', 'logAdjacencyChanges', 'processConfiguration', 'areas', 'neighbors', 'summaryAddresses', 'filterRules', 'redistributeProtocols', 'id', 'type'])

        url = construct_url(params['hostname'], '/devices/default/routing/virtualrouters/default/ospf/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getOSPF(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/devices/default/routing/virtualrouters/default/ospf/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getOSPFList(params):
        query_params = dict_subset(params, ['offset', 'limit', 'sort', 'filter'])

        url = construct_url(params['hostname'], '/devices/default/routing/virtualrouters/default/ospf', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getOSPFByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(OSPFResource.getOSPFList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertOSPF(params):
        def is_duplicate_name_error(err):
            return err.code == 422 and "Validation failed due to a duplicate name" in str(err.read())

        try:
            return OSPFResource.addOSPF(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = OSPFResource.getOSPFByName(params)
                params = copy_identity_properties(existing_object, params)
                return OSPFResource.editOSPF(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editOSPFByName(params):
        existing_object = OSPFResource.getOSPFByName(params)
        params = copy_identity_properties(existing_object, params)
        return OSPFResource.editOSPF(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteOSPFByName(params):
        existing_object = OSPFResource.getOSPFByName(params)
        params = copy_identity_properties(existing_object, params)
        return OSPFResource.deleteOSPF(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', default='upsertOSPF', choices=['addOSPF', 'deleteOSPF', 'editOSPF', 'getOSPF', 'getOSPFList', 'getOSPFByName', 'upsertOSPF', 'editOSPFByName', 'deleteOSPFByName']),
        register_as=dict(type='str'),

        areas=dict(type='list'),
        description=dict(type='str'),
        filter=dict(type='str'),
        filterRules=dict(type='list'),
        id=dict(type='str'),
        limit=dict(type='int'),
        logAdjacencyChanges=dict(type='str'),
        name=dict(type='str'),
        neighbors=dict(type='list'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        processConfiguration=dict(type='str'),
        processId=dict(type='str'),
        redistributeProtocols=dict(type='list'),
        sort=dict(type='str'),
        summaryAddresses=dict(type='list'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(OSPFResource, params['operation'])
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
