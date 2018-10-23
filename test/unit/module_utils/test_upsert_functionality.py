from __future__ import absolute_import

import pytest
import json
import copy


import unittest

from ansible.compat.tests import mock
from ansible.module_utils import basic
from units.modules.utils import set_module_args, exit_json, fail_json, AnsibleFailJson, AnsibleExitJson

from library import ftd_configuration

try:
    from ansible.module_utils.common import FtdServerError, HTTPMethod, ResponseParams, FtdConfigurationError
    from ansible.module_utils.configuration import DUPLICATE_NAME_ERROR_MESSAGE, UNPROCESSABLE_ENTITY_STATUS, \
        MULTIPLE_DUPLICATES_FOUND_ERROR, BaseConfigurationResource, FtdInvalidOperationNameError, QueryParams
except ImportError:
    from module_utils.common import FtdServerError, HTTPMethod, ResponseParams, FtdConfigurationError
    from module_utils.configuration import DUPLICATE_NAME_ERROR_MESSAGE, UNPROCESSABLE_ENTITY_STATUS, \
        MULTIPLE_DUPLICATES_FOUND_ERROR, BaseConfigurationResource, FtdInvalidOperationNameError, QueryParams


ADD_RESPONSE = {'status': 'Object added'}
EDIT_RESPONSE = {'status': 'Object edited'}
DELETE_RESPONSE = {'status': 'Object deleted'}
GET_BY_FILTER_RESPONSE = [{'name': 'foo', 'description': 'bar'}]
ARBITRARY_RESPONSE = {'status': 'Arbitrary request sent'}


class TestUpsertOperationUnitTests(unittest.TestCase):
    def setUp(self):
        conn = mock.MagicMock()
        self._resource = BaseConfigurationResource(conn)

    def test_get_operation_name(self):
        operation_a = mock.MagicMock()
        operation_b = mock.MagicMock()
        checker = mock.MagicMock()

        operations = {
            operation_a: "spec",
            operation_b: "spec"
        }

        checker.side_effect = [1,
                               0, 1,
                               0, 0]
        assert operation_a == self._resource._get_operation_name(checker, operations)
        assert operation_b == self._resource._get_operation_name(checker, operations)

        self.assertRaises(
            FtdConfigurationError,
            self._resource._get_operation_name, checker, operations
        )

    @mock.patch.object(BaseConfigurationResource, "_get_operation_name")
    @mock.patch.object(BaseConfigurationResource, "add_object")
    def test_add_upserted_object(self, add_object_mock, get_operation_mock):
        model_operations = mock.MagicMock()
        params = mock.MagicMock()
        add_op_name = get_operation_mock.return_value

        assert add_object_mock.return_value == self._resource._add_upserted_object(model_operations, params)

        get_operation_mock.assert_called_once_with(
            self._resource._operation_checker.is_add_operation,
            model_operations)
        add_object_mock.assert_called_once_with(add_op_name, params)

    @mock.patch.object(BaseConfigurationResource, "_get_operation_name")
    @mock.patch.object(BaseConfigurationResource, "edit_object")
    @mock.patch("module_utils.configuration.copy_identity_properties")
    @mock.patch("module_utils.configuration._set_default")
    def test_edit_upserted_object(self, _set_default_mock, copy_properties_mock, edit_object_mock, get_operation_mock):
        model_operations = mock.MagicMock()
        existing_object = mock.MagicMock()
        params = {
            'path_params': {},
            'data': {}
        }

        result = self._resource._edit_upserted_object(model_operations, existing_object, params)

        assert result == edit_object_mock.return_value

        _set_default_mock.assert_has_calls([
            mock.call(params, 'path_params', {}),
            mock.call(params, 'data', {})
        ])
        get_operation_mock.assert_called_once_with(
            self._resource._operation_checker.is_edit_operation,
            model_operations
        )
        copy_properties_mock.assert_called_once_with(
            existing_object,
            params['data']
        )
        edit_object_mock.assert_called_once_with(
            get_operation_mock.return_value,
            params
        )

    @mock.patch.object(BaseConfigurationResource, "get_operation_specs_by_model_name")
    @mock.patch("module_utils.configuration.OperationChecker.is_upsert_operation_supported")
    @mock.patch("module_utils.configuration._extract_model_from_upsert_operation")
    def test_is_upsert_operation_supported(self, extract_model_mock, is_upsert_supported_mock, get_operation_spec_mock):
        op_name = mock.MagicMock()

        result = self._resource.is_upsert_operation_supported(op_name)

        assert result == is_upsert_supported_mock.return_value
        extract_model_mock.assert_called_once_with(op_name)
        get_operation_spec_mock.assert_called_once_with(extract_model_mock.return_value)
        is_upsert_supported_mock.assert_called_once_with(get_operation_spec_mock.return_value)

    @mock.patch.object(BaseConfigurationResource, "is_upsert_operation_supported")
    @mock.patch.object(BaseConfigurationResource, "get_operation_specs_by_model_name")
    @mock.patch.object(BaseConfigurationResource, "_add_upserted_object")
    @mock.patch.object(BaseConfigurationResource, "_edit_upserted_object")
    @mock.patch("module_utils.configuration._extract_model_from_upsert_operation")
    def test_upsert_object_succesfully_added(self, extract_model_mock, edit_mock, add_mock, get_operation_mock,
                                             is_upsert_supported_mock):
        op_name = mock.MagicMock()
        params = mock.MagicMock()

        is_upsert_supported_mock.return_value = True

        result = self._resource.upsert_object(op_name, params)

        assert result == add_mock.return_value
        is_upsert_supported_mock.assert_called_once_with(op_name)
        extract_model_mock.assert_called_once_with(op_name)
        get_operation_mock.assert_called_once_with(extract_model_mock.return_value)
        add_mock.assert_called_once_with(get_operation_mock.return_value, params)
        edit_mock.assert_not_called()

    @mock.patch.object(BaseConfigurationResource, "is_upsert_operation_supported")
    @mock.patch.object(BaseConfigurationResource, "get_operation_specs_by_model_name")
    @mock.patch.object(BaseConfigurationResource, "_add_upserted_object")
    @mock.patch.object(BaseConfigurationResource, "_edit_upserted_object")
    @mock.patch("module_utils.configuration._extract_model_from_upsert_operation")
    def test_upsert_object_succesfully_edited(self, extract_model_mock, edit_mock, add_mock, get_operation_mock,
                                             is_upsert_supported_mock):
        op_name = mock.MagicMock()
        params = mock.MagicMock()

        is_upsert_supported_mock.return_value = True
        error = FtdConfigurationError("Obj duplication error")
        error.obj = mock.MagicMock()

        add_mock.side_effect = error

        result = self._resource.upsert_object(op_name, params)

        assert result == edit_mock.return_value
        is_upsert_supported_mock.assert_called_once_with(op_name)
        extract_model_mock.assert_called_once_with(op_name)
        get_operation_mock.assert_called_once_with(extract_model_mock.return_value)
        add_mock.assert_called_once_with(get_operation_mock.return_value, params)
        edit_mock.assert_called_once_with(get_operation_mock.return_value, error.obj,  params)

    @mock.patch.object(BaseConfigurationResource, "is_upsert_operation_supported")
    @mock.patch.object(BaseConfigurationResource, "get_operation_specs_by_model_name")
    @mock.patch.object(BaseConfigurationResource, "_add_upserted_object")
    @mock.patch.object(BaseConfigurationResource, "_edit_upserted_object")
    @mock.patch("module_utils.configuration._extract_model_from_upsert_operation")
    def test_upsert_object_not_supported(self, extract_model_mock, edit_mock, add_mock, get_operation_mock,
                                              is_upsert_supported_mock):
        op_name = mock.MagicMock()
        params = mock.MagicMock()

        is_upsert_supported_mock.return_value = False

        self.assertRaises(
            FtdInvalidOperationNameError,
            self._resource.upsert_object, op_name, params
        )

        is_upsert_supported_mock.assert_called_once_with(op_name)
        extract_model_mock.assert_not_called()
        get_operation_mock.assert_not_called()
        add_mock.assert_not_called()
        edit_mock.assert_not_called()

    @mock.patch.object(BaseConfigurationResource, "is_upsert_operation_supported")
    @mock.patch.object(BaseConfigurationResource, "get_operation_specs_by_model_name")
    @mock.patch.object(BaseConfigurationResource, "_add_upserted_object")
    @mock.patch.object(BaseConfigurationResource, "_edit_upserted_object")
    @mock.patch("module_utils.configuration._extract_model_from_upsert_operation")
    def test_upsert_object_neither_added_nor_edited(self, extract_model_mock, edit_mock, add_mock, get_operation_mock,
                                              is_upsert_supported_mock):
        op_name = mock.MagicMock()
        params = mock.MagicMock()

        is_upsert_supported_mock.return_value = True
        error = FtdConfigurationError("Obj duplication error")
        error.obj = mock.MagicMock()

        add_mock.side_effect = error
        edit_mock.side_effect = FtdConfigurationError("Some object edit error")

        self.assertRaises(
            FtdConfigurationError,
            self._resource.upsert_object, op_name, params
        )

        is_upsert_supported_mock.assert_called_once_with(op_name)
        extract_model_mock.assert_called_once_with(op_name)
        get_operation_mock.assert_called_once_with(extract_model_mock.return_value)
        add_mock.assert_called_once_with(get_operation_mock.return_value, params)
        edit_mock.assert_called_once_with(get_operation_mock.return_value, error.obj, params)

    @mock.patch.object(BaseConfigurationResource, "is_upsert_operation_supported")
    @mock.patch.object(BaseConfigurationResource, "get_operation_specs_by_model_name")
    @mock.patch.object(BaseConfigurationResource, "_add_upserted_object")
    @mock.patch.object(BaseConfigurationResource, "_edit_upserted_object")
    @mock.patch("module_utils.configuration._extract_model_from_upsert_operation")
    def test_upsert_object_with_fatal_error_during_add(self, extract_model_mock, edit_mock, add_mock,
                                                    get_operation_mock,
                                                    is_upsert_supported_mock):
        op_name = mock.MagicMock()
        params = mock.MagicMock()

        is_upsert_supported_mock.return_value = True

        error = FtdConfigurationError("Obj duplication error")
        add_mock.side_effect = error

        self.assertRaises(
            FtdConfigurationError,
            self._resource.upsert_object, op_name, params
        )

        is_upsert_supported_mock.assert_called_once_with(op_name)
        extract_model_mock.assert_called_once_with(op_name)
        get_operation_mock.assert_called_once_with(extract_model_mock.return_value)
        add_mock.assert_called_once_with(get_operation_mock.return_value, params)
        edit_mock.assert_not_called()


# functional tests below
class TestUpsertOperationFunctionalTests(object):
    module = ftd_configuration

    @pytest.fixture(autouse=True)
    def module_mock(self, mocker):
        return mocker.patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)

    @pytest.fixture(autouse=True)
    def connection_mock(self, mocker):
        connection_class_mock = mocker.patch('library.ftd_configuration.Connection')
        connection_instance = connection_class_mock.return_value
        connection_instance.validate_data.return_value = True, None
        connection_instance.validate_query_params.return_value = True, None
        connection_instance.validate_path_params.return_value = True, None
        return connection_instance

    @pytest.fixture
    def resource_mock(self, mocker):
        resource_class_mock = mocker.patch('library.ftd_configuration.BaseConfigurationResource')
        resource_instance = resource_class_mock.return_value
        resource_instance.is_upsert_operation.return_value = False
        return resource_instance.crud_operation

    def test_module_should_create_object_when_upsert_operation_and_object_does_not_exist(self, connection_mock):
        url = '/test'

        operations = {
            'getObjectList': {
                'method': HTTPMethod.GET,
                'url': url,
                'modelName': 'Object',
                'returnMultipleItems': True},
            'addObject': {
                'method': HTTPMethod.POST,
                'modelName': 'Object',
                'url': url},
            'editObject': {
                'method': HTTPMethod.PUT,
                'modelName': 'Object',
                'url': '/test/{objId}'},
            'otherObjectOperation': {
                'method': HTTPMethod.GET,
                'modelName': 'Object',
                'url': '/test/{objId}',
                'returnMultipleItems': False
        }}

        def get_operation_spec(name):
            return operations[name]

        connection_mock.get_operation_spec = get_operation_spec

        connection_mock.get_operation_specs_by_model_name.return_value = operations
        connection_mock.send_request.return_value = {
            ResponseParams.SUCCESS: True,
            ResponseParams.RESPONSE: ADD_RESPONSE
        }
        params = {
            'operation': 'upsertObject',
            'data': {'id': '123', 'name': 'testObject', 'type': 'object'},
            'path_params': {'objId': '123'},
            'register_as': 'test_var'
        }
        result = self._run_module(params)
        connection_mock.send_request.assert_called_once_with(url_path=url,
                                                             http_method=HTTPMethod.POST,
                                                             path_params=params['path_params'],
                                                             query_params={},
                                                             body_params=params['data'])
        assert ADD_RESPONSE == result['response']

    # test when object exists but with different fields(except id)
    def test_module_should_update_object_when_upsert_operation_and_object_exists(self, connection_mock):
        url = '/test'
        obj_id = '456'
        version = 'test_version'
        url_with_id_templ = '{0}/{1}'.format(url, '{objId}')

        new_value = '0000'
        old_value = '1111'
        params = {
            'operation': 'upsertObject',
            'data': {'name': 'testObject', 'value': new_value, 'type': 'object'},
            'register_as': 'test_var'
        }

        def request_handler(url_path=None, http_method=None, body_params=None, path_params=None, query_params=None):
            if http_method == HTTPMethod.POST:
                assert url_path == url
                assert body_params == params['data']
                assert query_params == {}
                assert path_params == {}
                return {
                    ResponseParams.SUCCESS: False,
                    ResponseParams.RESPONSE: DUPLICATE_NAME_ERROR_MESSAGE,
                    ResponseParams.STATUS_CODE: UNPROCESSABLE_ENTITY_STATUS
                }
            elif http_method == HTTPMethod.GET:
                is_get_list_req = url_path == url
                is_get_req = url_path == url_with_id_templ
                assert is_get_req or is_get_list_req

                if is_get_list_req:
                    assert body_params == {}
                    # FIXME(119vik): this check added due to issue with iterate_over_pageable_resource function
                    assert (
                            query_params == {QueryParams.FILTER: 'name:testObject', 'limit': 10, 'offset': 0} or
                            query_params == {QueryParams.FILTER: 'name:testObject', 'limit': 10, 'offset': 10})
                    assert path_params == {}
                elif is_get_req:
                    assert body_params == {}
                    assert query_params == {}
                    assert path_params == {'objId': obj_id}

                #FIXME(119vik): this part added to prevent client from fetching new records
                if query_params and query_params['offset'] > 0:
                    return {
                        ResponseParams.SUCCESS: True,
                        ResponseParams.RESPONSE: {
                            'items': []
                        }
                    }

                return {
                    ResponseParams.SUCCESS: True,
                    ResponseParams.RESPONSE: {
                        'items': [
                            {'name': 'testObject', 'value': old_value, 'type': 'object', 'id': obj_id,
                             'version': version}
                        ]
                    }
                }
            elif http_method == HTTPMethod.PUT:
                assert url_path == url_with_id_templ
                return {
                    ResponseParams.SUCCESS: True,
                    ResponseParams.RESPONSE: body_params
                }
            else:
                assert False

        operations = {
            'getObjectList': {'method': HTTPMethod.GET, 'url': url, 'modelName': 'Object', 'returnMultipleItems': True},
            'addObject': {'method': HTTPMethod.POST, 'modelName': 'Object', 'url': url},
            'editObject': {'method': HTTPMethod.PUT, 'modelName': 'Object', 'url': url_with_id_templ},
            'otherObjectOperation': {
                'method': HTTPMethod.GET,
                'modelName': 'Object',
                'url': url_with_id_templ,
                'returnMultipleItems': False}
        }

        def get_operation_spec(name):
            return operations[name]

        connection_mock.get_operation_spec = get_operation_spec
        connection_mock.get_operation_specs_by_model_name.return_value = operations

        connection_mock.send_request = request_handler
        result = self._run_module(params)

        expected_val = {'name': 'testObject', 'value': new_value, 'type': 'object', 'id': obj_id, 'version': version}

        assert {
                   'changed': True,
                   'response': expected_val,
                   'ansible_facts': {
                       'test_var': expected_val
                   }} == result

    # test when object exists and all fields have the same value
    def test_module_should_not_update_object_when_upsert_operation_and_object_exists_with_the_same_fields(
            self, connection_mock):
        url = '/test'
        url_with_id_templ = '{0}/{1}'.format(url, '{objId}')

        params = {
            'operation': 'upsertObject',
            'data': {'name': 'testObject', 'value': '3333', 'type': 'object'},
            'register_as': 'test_var'
        }

        expected_val = copy.deepcopy(params['data'])
        expected_val['version'] = 'test_version'
        expected_val['id'] = 'test_id'

        def request_handler(url_path=None, http_method=None, body_params=None, path_params=None, query_params=None):
            if http_method == HTTPMethod.POST:
                assert url_path == url
                assert body_params == params['data']
                assert query_params == {}
                assert path_params == {}
                return {
                    ResponseParams.SUCCESS: False,
                    ResponseParams.RESPONSE: DUPLICATE_NAME_ERROR_MESSAGE,
                    ResponseParams.STATUS_CODE: UNPROCESSABLE_ENTITY_STATUS
                }
            elif http_method == HTTPMethod.GET:
                assert url_path == url
                assert body_params == {}
                # FIXME(119vik): this check added due to issue with iterate_over_pageable_resource function
                assert (
                        query_params == {QueryParams.FILTER: 'name:testObject', 'limit': 10, 'offset': 0} or
                        query_params == {QueryParams.FILTER: 'name:testObject', 'limit': 10, 'offset': 10})
                assert path_params == {}

                # FIXME(119vik): this part added to prevent client from fetching new records
                if query_params and query_params['offset'] > 0:
                    return {
                        ResponseParams.SUCCESS: True,
                        ResponseParams.RESPONSE: {
                            'items': []
                        }
                    }

                return {
                    ResponseParams.SUCCESS: True,
                    ResponseParams.RESPONSE: {
                        'items': [expected_val]
                    }
                }
            else:
                assert False

        operations = {
            'getObjectList': {'method': HTTPMethod.GET, 'modelName': 'Object', 'url': url, 'returnMultipleItems': True},
            'addObject': {'method': HTTPMethod.POST, 'modelName': 'Object', 'url': url},
            'editObject': {'method': HTTPMethod.PUT, 'modelName': 'Object', 'url': url_with_id_templ},
            'otherObjectOperation': {
                'method': HTTPMethod.GET,
                'modelName': 'Object',
                'url': url_with_id_templ,
                'returnMultipleItems': False}
        }

        def get_operation_spec(name):
            return operations[name]

        connection_mock.get_operation_spec = get_operation_spec
        connection_mock.get_operation_specs_by_model_name.return_value = operations

        connection_mock.send_request = request_handler
        result = self._run_module(params)

        assert {
                   'changed': False,
                   'response': expected_val,
                   'ansible_facts': {
                       'test_var': expected_val
                   }} == result

    def test_module_should_fail_when_upsert_operation_is_not_supported(self, connection_mock):
        connection_mock.get_operation_specs_by_model_name.return_value = {
            'addObject': {'method': HTTPMethod.POST, 'modelName': 'Object', 'url': '/test'},
            'editObject': {'method': HTTPMethod.PUT, 'modelName': 'Object', 'url': '/test/{objId}'},
            'otherObjectOperation': {
                'method': HTTPMethod.GET,
                'modelName': 'Object',
                'url': '/test/{objId}',
                'returnMultipleItems': False}
        }
        params = {
            'operation': 'upsertObject',
            'data': {'id': '123', 'name': 'testObject', 'type': 'object'},
            'path_params': {'objId': '123'},
            'register_as': 'test_var'
        }
        result = self._run_module_with_fail_json(params)
        connection_mock.send_request.assert_not_called()
        assert {
                   'msg': 'Invalid operation name provided: upsertObject',
                   'failed': True} == result

    # when create operation raised FtdConfigurationError exception without id and version
    def test_module_should_fail_when_upsert_operation_and_failed_create_without_id_and_version(self, connection_mock):
        url = '/test'
        url_with_id_templ = '{0}/{1}'.format(url, '{objId}')

        params = {
            'operation': 'upsertObject',
            'data': {'name': 'testObject', 'value': '3333', 'type': 'object'},
            'register_as': 'test_var'
        }

        def request_handler(url_path=None, http_method=None, body_params=None, path_params=None, query_params=None):
            if http_method == HTTPMethod.POST:
                assert url_path == url
                assert body_params == params['data']
                assert query_params == {}
                assert path_params == {}
                return {
                    ResponseParams.SUCCESS: False,
                    ResponseParams.RESPONSE: DUPLICATE_NAME_ERROR_MESSAGE,
                    ResponseParams.STATUS_CODE: UNPROCESSABLE_ENTITY_STATUS
                }
            elif http_method == HTTPMethod.GET:
                assert url_path == url
                assert body_params == {}
                assert query_params == {QueryParams.FILTER: 'name:testObject', 'limit': 10, 'offset': 0}
                assert path_params == {}

                return {
                    ResponseParams.SUCCESS: True,
                    ResponseParams.RESPONSE: {
                        'items': []
                    }
                }
            else:
                assert False

        operations = {
            'getObjectList': {'method': HTTPMethod.GET, 'modelName': 'Object', 'url': url, 'returnMultipleItems': True},
            'addObject': {'method': HTTPMethod.POST, 'modelName': 'Object', 'url': url},
            'editObject': {'method': HTTPMethod.PUT, 'modelName': 'Object', 'url': url_with_id_templ},
            'otherObjectOperation': {
                'method': HTTPMethod.GET,
                'modelName': 'Object',
                'url': url_with_id_templ,
                'returnMultipleItems': False}
        }

        def get_operation_spec(name):
            return operations[name]

        connection_mock.get_operation_spec = get_operation_spec
        connection_mock.get_operation_specs_by_model_name.return_value = operations
        connection_mock.send_request = request_handler
        result = self._run_module_with_fail_json(params)

        assert result['failed']
        assert 'Server returned an error trying to execute upsertObject operation. Status code: 422. ' \
               'Server response: Validation failed due to a duplicate name' == result['msg']

    def test_module_should_fail_when_upsert_operation_and_failed_update_operation(self, connection_mock):
        url = '/test'
        obj_id = '456'
        version = 'test_version'
        url_with_id_templ = '{0}/{1}'.format(url, '{objId}')

        error_code = 404

        new_value = '0000'
        old_value = '1111'
        params = {
            'operation': 'upsertObject',
            'data': {'name': 'testObject', 'value': new_value, 'type': 'object'},
            'register_as': 'test_var'
        }

        error_msg = 'test error'

        def request_handler(url_path=None, http_method=None, body_params=None, path_params=None, query_params=None):
            if http_method == HTTPMethod.POST:
                assert url_path == url
                assert body_params == params['data']
                assert query_params == {}
                assert path_params == {}
                return {
                    ResponseParams.SUCCESS: False,
                    ResponseParams.RESPONSE: DUPLICATE_NAME_ERROR_MESSAGE,
                    ResponseParams.STATUS_CODE: UNPROCESSABLE_ENTITY_STATUS
                }
            elif http_method == HTTPMethod.GET:
                is_get_list_req = url_path == url
                is_get_req = url_path == url_with_id_templ
                assert is_get_req or is_get_list_req

                if is_get_list_req:
                    assert body_params == {}
                    #FIXME(119vik): this check added due to issue with iterate_over_pageable_resource function
                    assert (
                            query_params == {QueryParams.FILTER: 'name:testObject', 'limit': 10, 'offset': 0} or
                            query_params == {QueryParams.FILTER: 'name:testObject', 'limit': 10, 'offset': 10})
                elif is_get_req:
                    assert body_params == {}
                    assert query_params == {}
                    assert path_params == {'objId': obj_id}

                # FIXME(119vik): this part added to prevent client from fetching new records
                if query_params and query_params['offset'] > 0:
                    return {
                        ResponseParams.SUCCESS: True,
                        ResponseParams.RESPONSE: {
                            'items': []
                        }
                    }

                return {
                    ResponseParams.SUCCESS: True,
                    ResponseParams.RESPONSE: {
                        'items': [
                            {'name': 'testObject', 'value': old_value, 'type': 'object', 'id': obj_id,
                             'version': version}
                        ]
                    }
                }
            elif http_method == HTTPMethod.PUT:
                assert url_path == url_with_id_templ
                raise FtdServerError(error_msg, error_code)
            else:
                assert False

        operations = {
            'getObjectList': {'method': HTTPMethod.GET, 'modelName': 'Object', 'url': url, 'returnMultipleItems': True},
            'addObject': {'method': HTTPMethod.POST, 'modelName': 'Object', 'url': url},
            'editObject': {'method': HTTPMethod.PUT, 'modelName': 'Object', 'url': url_with_id_templ},
            'otherObjectOperation': {
                'method': HTTPMethod.GET,
                'modelName': 'Object',
                'url': url_with_id_templ,
                'returnMultipleItems': False}
        }

        def get_operation_spec(name):
            return operations[name]

        connection_mock.get_operation_spec = get_operation_spec
        connection_mock.get_operation_specs_by_model_name.return_value = operations
        connection_mock.send_request = request_handler
        result = self._run_module_with_fail_json(params)

        assert result['failed']
        assert 'Server returned an error trying to execute {0} operation. ' \
               'Status code: {1}. Server response: {2}'.format(params['operation'], error_code, error_msg) == result[
                   'msg']

    def test_module_should_fail_when_upsert_operation_and_invalid_data_for_create_operation(self, connection_mock):
        new_value = '0000'
        params = {
            'operation': 'upsertObject',
            'data': {'name': 'testObject', 'value': new_value, 'type': 'object'},
            'register_as': 'test_var'
        }

        connection_mock.send_request.assert_not_called()

        operations = {
            'getObjectList': {
                'method': HTTPMethod.GET,
                'modelName': 'Object',
                'url': 'sd',
                'returnMultipleItems': True},
            'addObject': {'method': HTTPMethod.POST, 'modelName': 'Object', 'url': 'sdf'},
            'editObject': {'method': HTTPMethod.PUT, 'modelName': 'Object', 'url': 'sadf'},
            'otherObjectOperation': {
                'method': HTTPMethod.GET,
                'modelName': 'Object',
                'url': 'sdfs',
                'returnMultipleItems': False}
        }

        def get_operation_spec(name):
            return operations[name]

        connection_mock.get_operation_spec = get_operation_spec
        connection_mock.get_operation_specs_by_model_name.return_value = operations

        report = {
            'required': ['objects[0].type'],
            'invalid_type': [
                {
                    'path': 'objects[3].id',
                    'expected_type': 'string',
                    'actually_value': 1
                }
            ]
        }
        connection_mock.validate_data.return_value = (False, json.dumps(report, sort_keys=True, indent=4))

        result = self._run_module_with_fail_json(params)

        key = 'Invalid data provided'
        assert result['msg'][key]
        result['msg'][key] = json.loads(result['msg'][key])
        assert result == {
            'msg':
                {key: {
                    'invalid_type': [{'actually_value': 1, 'expected_type': 'string', 'path': 'objects[3].id'}],
                    'required': ['objects[0].type']
                }},
            'failed': True}

    def _run_module(self, module_args):
        set_module_args(module_args)
        with pytest.raises(AnsibleExitJson) as ex:
            self.module.main()
        return ex.value.args[0]

    def _run_module_with_fail_json(self, module_args):
        set_module_args(module_args)
        with pytest.raises(AnsibleFailJson) as exc:
            self.module.main()
        result = exc.value.args[0]
        return result

    def test_module_should_fail_when_upsert_operation_and_few_objects_found_by_filter(self, connection_mock):
        url = '/test'
        url_with_id_templ = '{0}/{1}'.format(url, '{objId}')

        sample_obj = {'name': 'testObject', 'value': '3333', 'type': 'object'}
        params = {
            'operation': 'upsertObject',
            'data': sample_obj,
            'register_as': 'test_var'
        }

        def request_handler(url_path=None, http_method=None, body_params=None, path_params=None, query_params=None):
            if http_method == HTTPMethod.POST:
                assert url_path == url
                assert body_params == params['data']
                assert query_params == {}
                assert path_params == {}
                return {
                    ResponseParams.SUCCESS: False,
                    ResponseParams.RESPONSE: DUPLICATE_NAME_ERROR_MESSAGE,
                    ResponseParams.STATUS_CODE: UNPROCESSABLE_ENTITY_STATUS
                }
            elif http_method == HTTPMethod.GET:
                assert url_path == url
                assert body_params == {}
                # FIXME(119vik): this check added due to issue with iterate_over_pageable_resource function
                assert (
                        query_params == {QueryParams.FILTER: 'name:testObject', 'limit': 10, 'offset': 0} or
                        query_params == {QueryParams.FILTER: 'name:testObject', 'limit': 10, 'offset': 10})

                assert path_params == {}

                # FIXME(119vik): this part added to prevent client from fetching new records
                if query_params and query_params['offset'] > 0:
                    return {
                        ResponseParams.SUCCESS: True,
                        ResponseParams.RESPONSE: {
                            'items': []
                        }
                    }

                return {
                    ResponseParams.SUCCESS: True,
                    ResponseParams.RESPONSE: {
                        'items': [sample_obj, sample_obj]
                    }
                }
            else:
                assert False

        operations = {
            'getObjectList': {'method': HTTPMethod.GET, 'modelName': 'Object', 'url': url, 'returnMultipleItems': True},
            'addObject': {'method': HTTPMethod.POST, 'modelName': 'Object', 'url': url},
            'editObject': {'method': HTTPMethod.PUT, 'modelName': 'Object', 'url': url_with_id_templ},
            'otherObjectOperation': {
                'method': HTTPMethod.GET,
                'modelName': 'Object',
                'url': url_with_id_templ,
                'returnMultipleItems': False}
        }

        def get_operation_spec(name):
            return operations[name]

        connection_mock.get_operation_spec = get_operation_spec
        connection_mock.get_operation_specs_by_model_name.return_value = operations
        connection_mock.send_request = request_handler
        result = self._run_module_with_fail_json(params)

        assert result['failed']
        assert ('Failed to execute upsertObject operation because of the configuration error: {}'.format(
            MULTIPLE_DUPLICATES_FOUND_ERROR)) == result['msg']
