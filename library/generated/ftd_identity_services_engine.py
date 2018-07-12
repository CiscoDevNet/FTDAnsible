#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_identity_services_engine
short_description: Manages IdentityServicesEngine objects on Cisco FTD devices
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
      - A small description of the Identity Service Engine configuration<br>Field level constraints: length must be between 0 and 200 (inclusive), cannot have HTML, must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  enabled
    description:
      - A boolean that specifies whether the Identity Services Engine (ISE) configuration is enabled. Values are true(enabled) or false(disabled)<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  ftdCertificate
    description:
      - The internal certificate that the system must provide to Identity Services Engine (ISE) when connecting to ISE or when performing bulk downloads<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)<br>Allowed types are: [InternalCertificate]
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  iseNetworkFilters
    description:
      - An optional list of network objects. If you define a network filter, Identity Services Engine (ISE) reports user activity on the specified networks only. The system receives no information from ISE for any other networks<br>Allowed types are: [NetworkObject, NetworkObjectGroup]
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  mntCertificate
    description:
      - The trusted CA certificate for the MNT server in the Identity Services Engine (ISE) deployment. If your deployment includes a primary and a secondary MNT node, the CA certificates for both nodes must be signed by the same certificate authority<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)<br>Allowed types are: [ExternalCACertificate]
  name
    description:
      - Name of the Identity Services Engine (ISE) configuration
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  primaryIseServer
    description:
      - The address of the primary Identity Services Engine (ISE) server
  pxGridCertificate
    description:
      - The trusted CA certificate for the pxGrid framework. If your deployment includes a primary and a secondary pxGrid node, the CA certificates for both nodes must be signed by the same certificate authority<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)<br>Allowed types are: [ExternalCACertificate]
  secondaryIseServer
    description:
      - If you are using a high availability (HA) configuration for the primary Identity Services Engine (ISE) server, the address of the secondary Identity Services Engine (ISE) server
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - identityservicesengine
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch IdentityServicesEngine with a given name
  ftd_identity_services_engine:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getIdentityServicesEngineByName"
    name: "Ansible IdentityServicesEngine"

- name: Create a IdentityServicesEngine
  ftd_identity_services_engine:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addIdentityServicesEngine'

    description: "From Ansible with love"
    name: "Ansible IdentityServicesEngine"
    type: "identityservicesengine"
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


class IdentityServicesEngineResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addIdentityServicesEngine(params):
        body_params = dict_subset(params, ['description', 'enabled', 'ftdCertificate', 'id', 'iseNetworkFilters', 'mntCertificate', 'name', 'primaryIseServer', 'pxGridCertificate', 'secondaryIseServer', 'type', 'version'])

        url = construct_url(params['hostname'], '/integration/identityservicesengine')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteIdentityServicesEngine(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/integration/identityservicesengine/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editIdentityServicesEngine(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['description', 'enabled', 'ftdCertificate', 'id', 'iseNetworkFilters', 'mntCertificate', 'name', 'primaryIseServer', 'pxGridCertificate', 'secondaryIseServer', 'type', 'version'])

        url = construct_url(params['hostname'], '/integration/identityservicesengine/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIdentityServicesEngine(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/integration/identityservicesengine/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIdentityServicesEngineList(params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        url = construct_url(params['hostname'], '/integration/identityservicesengine', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIdentityServicesEngineByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(IdentityServicesEngineResource.getIdentityServicesEngineList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertIdentityServicesEngine(params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return IdentityServicesEngineResource.addIdentityServicesEngine(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = IdentityServicesEngineResource.getIdentityServicesEngineByName(params)
                params = copy_identity_properties(existing_object, params)
                return IdentityServicesEngineResource.editIdentityServicesEngine(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editIdentityServicesEngineByName(params):
        existing_object = IdentityServicesEngineResource.getIdentityServicesEngineByName(params)
        params = copy_identity_properties(existing_object, params)
        return IdentityServicesEngineResource.editIdentityServicesEngine(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteIdentityServicesEngineByName(params):
        existing_object = IdentityServicesEngineResource.getIdentityServicesEngineByName(params)
        params = copy_identity_properties(existing_object, params)
        return IdentityServicesEngineResource.deleteIdentityServicesEngine(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', default='upsertIdentityServicesEngine', choices=['addIdentityServicesEngine', 'deleteIdentityServicesEngine', 'editIdentityServicesEngine', 'getIdentityServicesEngine', 'getIdentityServicesEngineList', 'getIdentityServicesEngineByName', 'upsertIdentityServicesEngine', 'editIdentityServicesEngineByName', 'deleteIdentityServicesEngineByName']),
        register_as=dict(type='str'),

        description=dict(type='str'),
        enabled=dict(type='bool'),
        filter=dict(type='str'),
        ftdCertificate=dict(type='dict'),
        id=dict(type='str'),
        iseNetworkFilters=dict(type='list'),
        limit=dict(type='int'),
        mntCertificate=dict(type='dict'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        primaryIseServer=dict(type='str'),
        pxGridCertificate=dict(type='dict'),
        secondaryIseServer=dict(type='str'),
        sort=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(IdentityServicesEngineResource, params['operation'])
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
