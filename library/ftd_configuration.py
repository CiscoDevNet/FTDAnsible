#!/usr/bin/python

# Copyright (c) 2018 Cisco and/or its affiliates.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import, division, print_function


class _Operation:
    ADD = 'add'
    EDIT = 'edit'
    GET_ALL = 'get'


class _OperationNamePrefix:
    ADD = 'add'
    EDIT = 'edit'
    DELETE = 'delete'
    UPSERT = 'upsert'


__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_configuration
short_description: Manages configuration on Cisco FTD devices over REST API
description:
  - Manages configuration on Cisco FTD devices including creating, updating, removing configuration objects,
    scheduling and staring jobs, deploying pending changes, etc. All operation are performed over REST API.
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  operation:
    description:
      - The name of the operation to execute. Commonly, the operation starts with 'add', 'edit', 'get'
       or 'delete' verbs, but can have an arbitrary name too.
    required: true
  data:
    description:
      - Key-value pairs that should be sent as body parameters in a REST API call
  query_params:
    description:
      - Key-value pairs that should be sent as query parameters in a REST API call.
  path_params:
    description:
      - Key-value pairs that should be sent as path parameters in a REST API call.
  register_as:
    description:
      - Specifies Ansible fact name that is used to register received response from the FTD device.
  filters:
    description:
      - Key-value dict that represents equality filters. Every key is a property name and value is its desired value.
        If multiple filters are present, they are combined with logical operator AND.
"""

EXAMPLES = """
- name: Create a network object
  ftd_configuration:
    operation: "addNetworkObject"
    data:
      name: "Ansible-network-host"
      description: "From Ansible with love"
      subType: "HOST"
      value: "192.168.2.0"
      dnsResolution: "IPV4_AND_IPV6"
      type: "networkobject"
      isSystemDefined: false
    register_as: "hostNetwork"

- name: Delete the network object
  ftd_configuration:
    operation: "deleteNetworkObject"
    path_params:
      objId: "{{ hostNetwork['id'] }}"
"""

RETURN = """
response:
  description: HTTP response returned from the API call.
  returned: success
  type: dict
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection

try:
    from ansible.module_utils.configuration import BaseConfigurationResource
    from ansible.module_utils.fdm_swagger_client import OperationField, ValidationError
    from ansible.module_utils.common import HTTPMethod, construct_ansible_facts, FtdConfigurationError, \
        FtdServerError
except ImportError:
    from module_utils.configuration import BaseConfigurationResource
    from module_utils.fdm_swagger_client import OperationField, ValidationError
    from module_utils.common import HTTPMethod, construct_ansible_facts, FtdConfigurationError, \
        FtdServerError


def is_post_request(operation_spec):
    return operation_spec[OperationField.METHOD] == HTTPMethod.POST


def is_put_request(operation_spec):
    return operation_spec[OperationField.METHOD] == HTTPMethod.PUT


def is_add_operation(operation_name, operation_spec):
    # Some endpoints have non-CRUD operations, so checking operation name is required in addition to the HTTP method
    return operation_name.startswith(_OperationNamePrefix.ADD) and is_post_request(operation_spec)


def is_edit_operation(operation_name, operation_spec):
    # Some endpoints have non-CRUD operations, so checking operation name is required in addition to the HTTP method
    return operation_name.startswith(_OperationNamePrefix.EDIT) and is_put_request(operation_spec)


def is_delete_operation(operation_name, operation_spec):
    # Some endpoints have non-CRUD operations, so checking operation name is required in addition to the HTTP method
    return operation_name.startswith(_OperationNamePrefix.DELETE) and operation_spec[
        OperationField.METHOD] == HTTPMethod.DELETE


def is_upsert_operation(operation_name):
    return operation_name.startswith(_OperationNamePrefix.UPSERT)


def validate_params(connection, op_name, query_params, path_params, data, op_spec):
    report = {}

    def validate(validation_method, field_name, params):
        key = 'Invalid %s provided' % field_name
        try:
            is_valid, validation_report = validation_method(op_name, params)
            if not is_valid:
                report[key] = validation_report
        except Exception as e:
            report[key] = str(e)
        return report

    validate(connection.validate_query_params, 'query_params', query_params)
    validate(connection.validate_path_params, 'path_params', path_params)
    if is_post_request(op_spec):
        validate(connection.validate_data, 'data', data)

    if report:
        raise ValidationError(report)


def is_find_by_filter_operation(operation_name, operation_spec, filters):
    """
    Checks whether the called operation is 'find by filter'. This operation fetches all objects and finds
    the matching ones by the given filter. As filtering is done on the client side, this operation should be used
    only when selected filters are not implemented on the server side.

    :param operation_name: name of the operation being called by the user
    :type operation_name: str
    :param operation_spec: specification of the operation being called by the user
    :type operation_spec: dict
    :param filters: filters
    :return: True if called operation is find by filter, otherwise False
    :rtype: bool
    """
    is_find_all = is_find_all_operation(operation_name, operation_spec)
    return is_find_all and filters


def is_find_all_operation(operation_name, operation_spec):
    is_get_list_operation = operation_name.startswith('get') and operation_name.endswith('List')
    is_get_method = operation_spec[OperationField.METHOD] == HTTPMethod.GET
    return is_get_list_operation and is_get_method


def upsert_object(connection, upsert_operations, data, query_params, path_params=None):
    if path_params is None:
        path_params = {}
    try:
        return add_object(connection, data, path_params, query_params, upsert_operations)
    except FtdConfigurationError as e:
        object_id = e.objectId
        object_version = e.version
        if object_id:
            return edit_object(connection, data, object_id, object_version, path_params, query_params,
                               upsert_operations)
        else:
            raise e

    except Exception as e:
        raise e


def edit_object(connection, data, object_id, object_version, path_params, query_params, upsert_operations):
    resource = BaseConfigurationResource(connection)
    operation = upsert_operations[_Operation.EDIT]
    op_name = operation[_UpsertSpec.OPERATION_NAME]
    op_spec = operation[_UpsertSpec.SPEC]
    url = operation[_UpsertSpec.SPEC][OperationField.URL]
    path_params['objId'] = object_id
    data['version'] = object_version
    data['id'] = object_id
    validate_params(connection, op_name, query_params, path_params, data, op_spec)
    return resource.edit_object(url, data, path_params, query_params), resource


def add_object(connection, data, path_params, query_params, upsert_operations):
    resource = BaseConfigurationResource(connection)
    operation = upsert_operations[_Operation.ADD]
    op_name = operation[_UpsertSpec.OPERATION_NAME]
    op_spec = operation[_UpsertSpec.SPEC]
    url = operation[_UpsertSpec.SPEC][OperationField.URL]
    validate_params(connection, op_name, query_params, path_params, data, op_spec)
    return resource.add_object(url, data, path_params, query_params), resource


class _UpsertSpec:
    OPERATION_NAME = 'operation_name'
    SPEC = 'spec'


def get_operations_need_for_upsert_operation(operations):
    amount_operations_need_for_upsert_operation = 3
    upsert_operations = {}
    for operation_name in operations:
        operation_spec = operations[operation_name]
        operation_type = None
        if is_add_operation(operation_name, operation_spec):
            operation_type = _Operation.ADD
        elif is_edit_operation(operation_name, operation_spec):
            operation_type = _Operation.EDIT
        elif is_find_all_operation(operation_name, operation_spec):
            operation_type = _Operation.GET_ALL

        if operation_type:
            upsert_operations[operation_type] = {
                _UpsertSpec.OPERATION_NAME: operation_name,
                _UpsertSpec.SPEC: operation_spec
            }

    upsert_operation_is_supported = len(upsert_operations.keys()) == amount_operations_need_for_upsert_operation

    return upsert_operation_is_supported, upsert_operations


def module_fail_invalid_operation(module, op_name):
    module.fail_json(msg='Invalid operation name provided: %s' % op_name)


def get_base_operation_name_from_upsert(op_name):
    return _OperationNamePrefix.ADD + op_name[len(_OperationNamePrefix.UPSERT):]


def crud_operation(connection, data, filters, module, op_name, path_params, query_params):
    op_spec = connection.get_operation_spec(op_name)
    if op_spec is None:
        module_fail_invalid_operation(module, op_name)

    validate_params(connection, op_name, query_params, path_params, data, op_spec)

    if module.check_mode:
        module.exit_json(changed=False)

    resource = BaseConfigurationResource(connection)
    url = op_spec[OperationField.URL]

    if is_add_operation(op_name, op_spec):
        resp = resource.add_object(url, data, path_params, query_params)
    elif is_edit_operation(op_name, op_spec):
        resp = resource.edit_object(url, data, path_params, query_params)
    elif is_delete_operation(op_name, op_spec):
        resp = resource.delete_object(url, path_params)
    elif is_find_by_filter_operation(op_name, op_spec, filters):
        resp = resource.get_objects_by_filter(url, filters, path_params,
                                              query_params)
    else:
        resp = resource.send_request(url, op_spec[OperationField.METHOD], data,
                                     path_params,
                                     query_params)

    module.exit_json(changed=resource.config_changed, response=resp,
                     ansible_facts=construct_ansible_facts(resp, module.params))


def upsert_operation(connection, data, module, op_name, path_params, query_params):
    base_operation = get_base_operation_name_from_upsert(op_name)
    operations = connection.get_operations_spec(base_operation)
    upsert_operation_is_supported, upsert_operations = get_operations_need_for_upsert_operation(operations)
    if upsert_operation_is_supported:
        resp, resource = upsert_object(connection, upsert_operations, data, query_params, path_params)
        module.exit_json(changed=resource.config_changed, response=resp,
                         ansible_facts=construct_ansible_facts(resp, module.params))
    else:
        module_fail_invalid_operation(module, op_name)


def main():
    fields = dict(
        operation=dict(type='str', required=True),
        data=dict(type='dict'),
        query_params=dict(type='dict'),
        path_params=dict(type='dict'),
        register_as=dict(type='str'),
        filters=dict(type='dict')
    )
    module = AnsibleModule(argument_spec=fields,
                           supports_check_mode=True)
    params = module.params

    connection = Connection(module._socket_path)

    op_name = params['operation']
    data, query_params, path_params = params['data'], params['query_params'], params['path_params']
    try:
        if is_upsert_operation(op_name):
            upsert_operation(connection, data, module, op_name, path_params, query_params)
        else:
            filters = params['filters']
            crud_operation(connection, data, filters, module, op_name, path_params, query_params)

    except FtdConfigurationError as e:
        module.fail_json(msg='Failed to execute %s operation because of the configuration error: %s' % (op_name, e.msg))
    except FtdServerError as e:
        module.fail_json(msg='Server returned an error trying to execute %s operation. Status code: %s. '
                             'Server response: %s' % (op_name, e.code, e.response))
    except ValidationError as e:
        module.fail_json(msg=e.args[0])

if __name__ == '__main__':
    main()
