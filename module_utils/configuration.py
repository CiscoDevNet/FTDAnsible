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

from functools import partial

from ansible.module_utils.six import iteritems
try:
    from ansible.module_utils.common import HTTPMethod, equal_objects, copy_identity_properties, FtdConfigurationError, \
        FtdServerError, ResponseParams
    from ansible.module_utils.fdm_swagger_client import OperationField, ValidationError
except ImportError:
    from module_utils.common import HTTPMethod, equal_objects, copy_identity_properties, FtdConfigurationError, \
        FtdServerError, ResponseParams
    from module_utils.fdm_swagger_client import OperationField, ValidationError

DEFAULT_PAGE_SIZE = 10
DEFAULT_OFFSET = 0

UNPROCESSABLE_ENTITY_STATUS = 422
INVALID_UUID_ERROR_MESSAGE = "Validation failed due to an invalid UUID"
DUPLICATE_NAME_ERROR_MESSAGE = "Validation failed due to a duplicate name"


class _OperationNamePrefix:
    ADD = 'add'
    EDIT = 'edit'
    GET = 'get'
    DELETE = 'delete'
    UPSERT = 'upsert'


class _UpsertSpec:
    OPERATION_NAME = 'operation_name'
    SPEC = 'spec'


class _Operation:
    ADD = 'add'
    EDIT = 'edit'
    GET_ALL = 'get'


class CheckModeException(Exception):
    pass


class BaseConfigurationResource(object):
    def __init__(self, conn, check_mode=False):
        self._conn = conn
        self.config_changed = False
        self._operation_spec_cache = {}
        self._operations_spec_cache = {}
        self._check_mode = check_mode

    def get_operation_spec(self, operation_name):
        if operation_name not in self._operation_spec_cache:
            self._operation_spec_cache[operation_name] = self._conn.get_operation_spec(operation_name)

        return self._operation_spec_cache[operation_name]

    def get_operation_specs_by_model_name(self, operation_name):
        if operation_name not in self._operation_spec_cache:
            self._operations_spec_cache[operation_name] = self._conn.get_operation_specs_by_model_name(operation_name)

        return self._operations_spec_cache[operation_name]

    def get_object_by_name(self, url_path, name, path_params=None):
        item_generator = iterate_over_pageable_resource(
            partial(self._send_request, url_path=url_path, http_method=HTTPMethod.GET, path_params=path_params),
            {'filter': 'name:%s' % name}
        )
        # not all endpoints support filtering so checking name explicitly
        return next((item for item in item_generator if item['name'] == name), None)

    def get_objects_by_filter(self, operation_name, params):
        self.validate_params(operation_name, params)
        self.stop_if_check_mode()

        filters = params.get('filters', {})

        data, query_params, path_params = _get_user_params(params)
        op_spec = self.get_operation_spec(operation_name)
        url, method = _get_request_params_from_spec(op_spec)

        def match_filters(obj):
            for k, v in iteritems(filters):
                if k not in obj or obj[k] != v:
                    return False
            return True

        item_generator = iterate_over_pageable_resource(
            partial(self._send_request, url_path=url, http_method=method, path_params=path_params),
            query_params
        )
        return [i for i in item_generator if match_filters(i)]

    def add_object(self, operation_name, params):
        self.validate_params(operation_name, params)
        self.stop_if_check_mode()

        data, query_params, path_params = _get_user_params(params)
        op_spec = self.get_operation_spec(operation_name)
        url, method = _get_request_params_from_spec(op_spec)

        def is_duplicate_name_error(err):
            return err.code == UNPROCESSABLE_ENTITY_STATUS and DUPLICATE_NAME_ERROR_MESSAGE in str(err)

        try:
            return self._send_request(url_path=url, http_method=method, body_params=data,
                                     path_params=path_params, query_params=query_params)
        except FtdServerError as e:
            if is_duplicate_name_error(e):
                existing_obj = self.get_object_by_name(url, data['name'], path_params)

                if existing_obj is not None:
                    if equal_objects(existing_obj, data):
                        return existing_obj
                    else:
                        raise FtdConfigurationError(
                            'Cannot add new object. '
                            'An object with the same name but different parameters already exists.',
                            existing_obj)
                else:
                    raise e
            else:
                raise e

    def delete_object(self, operation_name, params):
        self.validate_params(operation_name, params)
        self.stop_if_check_mode()

        _, query_params, path_params = _get_user_params(params)
        op_spec = self.get_operation_spec(operation_name)
        url, method = _get_request_params_from_spec(op_spec)

        def is_invalid_uuid_error(err):
            return err.code == UNPROCESSABLE_ENTITY_STATUS and INVALID_UUID_ERROR_MESSAGE in str(err)

        try:
            return self._send_request(url_path=url, http_method=method, path_params=path_params)
        except FtdServerError as e:
            if is_invalid_uuid_error(e):
                return {'status': 'Referenced object does not exist'}
            else:
                raise e

    def edit_object(self, operation_name, params):
        self.validate_params(operation_name, params)
        self.stop_if_check_mode()

        data, query_params, path_params = _get_user_params(params)
        op_spec = self.get_operation_spec(operation_name)
        url, method = _get_request_params_from_spec(op_spec)

        existing_object = self._send_request(url_path=url, http_method=HTTPMethod.GET, path_params=path_params)

        if not existing_object:
            raise FtdConfigurationError('Referenced object does not exist')
        elif equal_objects(existing_object, data):
            return existing_object
        else:
            return self._send_request(url_path=url, http_method=method, body_params=data,
                                     path_params=path_params, query_params=query_params)

    def send_general_request(self, operation_name, params):
        self.validate_params(operation_name, params)
        self.stop_if_check_mode()

        data, query_params, path_params = _get_user_params(params)
        op_spec = self.get_operation_spec(operation_name)
        url, method = _get_request_params_from_spec(op_spec)

        return self._send_request(url, method, data,
                                 path_params,
                                 query_params)

    def _send_request(self, url_path, http_method, body_params=None, path_params=None, query_params=None):
        def raise_for_failure(resp):
            if not resp[ResponseParams.SUCCESS]:
                raise FtdServerError(resp[ResponseParams.RESPONSE], resp[ResponseParams.STATUS_CODE])

        response = self._conn.send_request(url_path=url_path, http_method=http_method, body_params=body_params,
                                           path_params=path_params, query_params=query_params)
        raise_for_failure(response)
        if http_method != HTTPMethod.GET:
            self.config_changed = True
        return response[ResponseParams.RESPONSE]

    def is_add_operation(self, operation_name):
        operation_spec = self.get_operation_spec(operation_name)
        # Some endpoints have non-CRUD operations, so checking operation name is required in addition to the HTTP method
        return operation_name.startswith(_OperationNamePrefix.ADD) and is_post_request(operation_spec)

    def is_edit_operation(self, operation_name):
        operation_spec = self.get_operation_spec(operation_name)
        # Some endpoints have non-CRUD operations, so checking operation name is required in addition to the HTTP method
        return operation_name.startswith(_OperationNamePrefix.EDIT) and is_put_request(operation_spec)

    def is_delete_operation(self, operation_name):
        operation_spec = self.get_operation_spec(operation_name)
        # Some endpoints have non-CRUD operations, so checking operation name is required in addition to the HTTP method
        return operation_name.startswith(_OperationNamePrefix.DELETE) and operation_spec[
            OperationField.METHOD] == HTTPMethod.DELETE

    def is_find_all_operation(self, operation_name):
        operation_spec = self.get_operation_spec(operation_name)
        is_get_list_operation = operation_name.startswith(_OperationNamePrefix.GET) and operation_name.endswith('List')
        is_get_method = operation_spec[OperationField.METHOD] == HTTPMethod.GET
        return is_get_list_operation and is_get_method

    @staticmethod
    def is_upsert_operation(operation_name):
        return operation_name.startswith(_OperationNamePrefix.UPSERT)

    def is_find_by_filter_operation(self, operation_name, params):
        """
        Checks whether the called operation is 'find by filter'. This operation fetches all objects and finds
        the matching ones by the given filter. As filtering is done on the client side, this operation should be used
        only when selected filters are not implemented on the server side.

        :param operation_name: name of the operation being called by the user
        :type operation_name: str
        :param operation_spec: specification of the operation being called by the user
        :type operation_spec: dict
        :param params: params - params should contain 'filters'
        :return: True if called operation is find by filter, otherwise False
        :rtype: bool
        """
        filters = params['filters']
        is_find_all = self.is_find_all_operation(operation_name)
        return is_find_all and filters

    def validate_params(self, operation_name, params):
        report = {}
        op_spec = self.get_operation_spec(operation_name)
        data, query_params, path_params = _get_user_params(params)

        def validate(validation_method, field_name, user_params):
            key = 'Invalid %s provided' % field_name
            try:
                is_valid, validation_report = validation_method(operation_name, user_params)
                if not is_valid:
                    report[key] = validation_report
            except Exception as e:
                report[key] = str(e)
            return report

        validate(self._conn.validate_query_params, 'query_params', query_params)
        validate(self._conn.validate_path_params, 'path_params', path_params)
        if is_post_request(op_spec):
            validate(self._conn.validate_data, 'data', data)

        if report:
            raise ValidationError(report)

    def stop_if_check_mode(self):
        if self._check_mode:
            raise CheckModeException()

    def upsert_operation_is_supported(self, op_name):
        base_operation = _get_base_operation_name_from_upsert(op_name)
        operations = self.get_operation_specs_by_model_name(base_operation)
        amount_operations_need_for_upsert_operation = 3
        amount_supported_operations = 0
        for operation_name in operations:
            if self.is_add_operation(operation_name) \
                    or self.is_edit_operation(operation_name) \
                    or self.is_find_all_operation(operation_name):
                amount_supported_operations += 1

        return amount_supported_operations == amount_operations_need_for_upsert_operation

    def upsert_object(self, op_name, params):

        base_operation = _get_base_operation_name_from_upsert(op_name)
        upsert_operations = self.get_operation_specs_by_model_name(base_operation)

        def get_operation_name(checker):
            for operation_name in upsert_operations:
                operation_spec = upsert_operations[operation_name]
                if checker(operation_spec):
                    return operation_name
            raise FtdConfigurationError("Don't support upsert operation")

        def edit_object(existing_object):
            edit_op_name = get_operation_name(is_put_request)
            _set_default(params, 'path_params', {})
            _set_default(params, 'data', {})

            params['path_params']['objId'] = existing_object['id']
            copy_identity_properties(existing_object, params['data'])
            return self.edit_object(edit_op_name, params)

        def add_object():
            add_op_name = get_operation_name(is_post_request)
            return self.add_object(add_op_name, params)

        try:
            return add_object()
        except FtdConfigurationError as e:
            if e.obj:
                return edit_object(e.obj)
            else:
                raise e
        except Exception as e:
            raise e


def _set_default(params, field_name, value):
    if field_name not in params or params[field_name] is None:
        params[field_name] = value


def is_post_request(operation_spec):
    return operation_spec[OperationField.METHOD] == HTTPMethod.POST


def is_put_request(operation_spec):
    return operation_spec[OperationField.METHOD] == HTTPMethod.PUT


def _get_base_operation_name_from_upsert(op_name):
    return _OperationNamePrefix.ADD + op_name[len(_OperationNamePrefix.UPSERT):]


def _get_user_params(params):
    return params.get('data', {}), params.get('query_params', {}), params.get('path_params', {})


def _get_request_params_from_spec(operation_spec):
    return operation_spec[OperationField.URL], operation_spec[OperationField.METHOD]


def iterate_over_pageable_resource(resource_func, query_params=None):
    """
    A generator function that iterates over a resource that supports pagination and lazily returns present items
    one by one.

    :param resource_func: function that receives `query_params` named argument and returns a page of objects
    :type resource_func: callable
    :param query_params: initial dictionary of query parameters that will be passed to the resource_func
    :type query_params: dict
    :return: an iterator containing returned items
    :rtype: iterator of dict
    """
    query_params = {} if query_params is None else dict(query_params)
    query_params.setdefault('limit', DEFAULT_PAGE_SIZE)
    query_params.setdefault('offset', DEFAULT_OFFSET)

    result = resource_func(query_params=query_params)
    while result['items']:
        for item in result['items']:
            yield item
        # creating a copy not to mutate existing dict
        query_params = dict(query_params)
        query_params['offset'] = int(query_params['offset']) + int(query_params['limit'])
        result = resource_func(query_params=query_params)
