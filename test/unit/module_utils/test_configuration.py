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

import json

import pytest
from ansible.compat.tests import mock
from ansible.compat.tests.mock import call, patch

from module_utils.configuration import iterate_over_pageable_resource, BaseConfigurationResource

try:
    from ansible.module_utils.common import HTTPMethod
    from ansible.module_utils.fdm_swagger_client import ValidationError
except ImportError:
    from module_utils.common import HTTPMethod
    from module_utils.fdm_swagger_client import ValidationError


class TestBaseConfigurationResource(object):
    @pytest.fixture
    def connection_mock(self, mocker):
        connection_class_mock = mocker.patch('library.ftd_configuration.Connection')
        connection_instance = connection_class_mock.return_value
        connection_instance.validate_data.return_value = True, None
        connection_instance.validate_query_params.return_value = True, None
        connection_instance.validate_path_params.return_value = True, None

        return connection_instance

    @patch.object(BaseConfigurationResource, '_send_request')
    def test_get_objects_by_filter_with_multiple_filters(self, send_request_mock, connection_mock):
        objects = [
            {'name': 'obj1', 'type': 1, 'foo': {'bar': 'buzz'}},
            {'name': 'obj2', 'type': 1, 'foo': {'bar': 'buz'}},
            {'name': 'obj3', 'type': 2, 'foo': {'bar': 'buzz'}}
        ]
        connection_mock.get_operation_spec.return_value = {
            'method': HTTPMethod.GET,
            'url': '/object/'
        }
        resource = BaseConfigurationResource(connection_mock, False)

        send_request_mock.side_effect = [{'items': objects}, {'items': []}]
        assert objects == resource.get_objects_by_filter('test', {})

        send_request_mock.side_effect = [{'items': objects}, {'items': []}]
        assert [objects[0]] == resource.get_objects_by_filter('test', {'filters': {'name': 'obj1'}})

        send_request_mock.side_effect = [{'items': objects}, {'items': []}]
        assert [objects[1]] == resource.get_objects_by_filter('test',
                                                              {'filters': {'type': 1, 'foo': {'bar': 'buz'}}})

    @patch.object(BaseConfigurationResource, '_send_request')
    def test_get_objects_by_filter_with_multiple_responses(self, send_request_mock, connection_mock):
        send_request_mock.side_effect = [
            {'items': [
                {'name': 'obj1', 'type': 'foo'},
                {'name': 'obj2', 'type': 'bar'}
            ]},
            {'items': [
                {'name': 'obj3', 'type': 'foo'}
            ]},
            {'items': []}
        ]
        connection_mock.get_operation_spec.return_value = {
            'method': HTTPMethod.GET,
            'url': '/object/'
        }
        resource = BaseConfigurationResource(connection_mock, False)

        assert [{'name': 'obj1', 'type': 'foo'}, {'name': 'obj3', 'type': 'foo'}] == resource.get_objects_by_filter(
            'test',
            {'filters': {'type': 'foo'}})

    def test_module_should_fail_if_validation_error_in_data(self, connection_mock):
        connection_mock.get_operation_spec.return_value = {'method': HTTPMethod.POST, 'url': '/test'}
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

        with pytest.raises(ValidationError) as e_info:
            resource = BaseConfigurationResource(connection_mock, False)
            resource.crud_operation('addTest', {'data': {}})

        result = e_info.value.args[0]
        key = 'Invalid data provided'
        assert result[key]
        result[key] = json.loads(result[key])
        assert result == {key: {
            'invalid_type': [{'actually_value': 1, 'expected_type': 'string', 'path': 'objects[3].id'}],
            'required': ['objects[0].type']
        }}

    def test_module_should_fail_if_validation_error_in_query_params(self, connection_mock):
        connection_mock.get_operation_spec.return_value = {'method': HTTPMethod.GET, 'url': '/test',
                                                           'returnMultipleItems': False}
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
        connection_mock.validate_query_params.return_value = (False, json.dumps(report, sort_keys=True, indent=4))

        with pytest.raises(ValidationError) as e_info:
            resource = BaseConfigurationResource(connection_mock, False)
            resource.crud_operation('getTestList', {'data': {}})

        result = e_info.value.args[0]

        key = 'Invalid query_params provided'
        assert result[key]
        result[key] = json.loads(result[key])

        assert result == {key: {
            'invalid_type': [{'actually_value': 1, 'expected_type': 'string', 'path': 'objects[3].id'}],
            'required': ['objects[0].type']}}

    def test_module_should_fail_if_validation_error_in_path_params(self, connection_mock):
        connection_mock.get_operation_spec.return_value = {'method': HTTPMethod.GET, 'url': '/test',
                                                           'returnMultipleItems': False}
        report = {
            'path_params': {
                'required': ['objects[0].type'],
                'invalid_type': [
                    {
                        'path': 'objects[3].id',
                        'expected_type': 'string',
                        'actually_value': 1
                    }
                ]
            }
        }
        connection_mock.validate_path_params.return_value = (False, json.dumps(report, sort_keys=True, indent=4))

        with pytest.raises(ValidationError) as e_info:
            resource = BaseConfigurationResource(connection_mock, False)
            resource.crud_operation('putTest', {'data': {}})

        result = e_info.value.args[0]

        key = 'Invalid path_params provided'
        assert result[key]
        result[key] = json.loads(result[key])

        assert result == {key: {
            'path_params': {
                'invalid_type': [{'actually_value': 1, 'expected_type': 'string', 'path': 'objects[3].id'}],
                'required': ['objects[0].type']}}}

    def test_module_should_fail_if_validation_error_in_all_params(self, connection_mock):
        connection_mock.get_operation_spec.return_value = {'method': HTTPMethod.POST, 'url': '/test'}
        report = {
            'data': {
                'required': ['objects[0].type'],
                'invalid_type': [
                    {
                        'path': 'objects[3].id',
                        'expected_type': 'string',
                        'actually_value': 1
                    }
                ]
            },
            'path_params': {
                'required': ['some_param'],
                'invalid_type': [
                    {
                        'path': 'name',
                        'expected_type': 'string',
                        'actually_value': True
                    }
                ]
            },
            'query_params': {
                'required': ['other_param'],
                'invalid_type': [
                    {
                        'path': 'f_integer',
                        'expected_type': 'integer',
                        'actually_value': "test"
                    }
                ]
            }
        }
        connection_mock.validate_data.return_value = (False, json.dumps(report['data'], sort_keys=True, indent=4))
        connection_mock.validate_query_params.return_value = (False,
                                                              json.dumps(report['query_params'], sort_keys=True,
                                                                         indent=4))
        connection_mock.validate_path_params.return_value = (False,
                                                             json.dumps(report['path_params'], sort_keys=True,
                                                                        indent=4))

        with pytest.raises(ValidationError) as e_info:
            resource = BaseConfigurationResource(connection_mock, False)
            resource.crud_operation('putTest', {'data': {}})

        result = e_info.value.args[0]

        key_data = 'Invalid data provided'
        assert result[key_data]
        result[key_data] = json.loads(result[key_data])

        key_path_params = 'Invalid path_params provided'
        assert result[key_path_params]
        result[key_path_params] = json.loads(result[key_path_params])

        key_query_params = 'Invalid query_params provided'
        assert result[key_query_params]
        result[key_query_params] = json.loads(result[key_query_params])

        assert result == {
            key_data: {'invalid_type': [{'actually_value': 1, 'expected_type': 'string', 'path': 'objects[3].id'}],
                       'required': ['objects[0].type']},
            key_path_params: {'invalid_type': [{'actually_value': True, 'expected_type': 'string', 'path': 'name'}],
                              'required': ['some_param']},
            key_query_params: {
                'invalid_type': [{'actually_value': 'test', 'expected_type': 'integer', 'path': 'f_integer'}],
                'required': ['other_param']}}


class TestIterateOverPageableResource(object):

    def test_iterate_over_pageable_resource_with_no_items(self):
        resource_func = mock.Mock(return_value={'items': []})

        items = iterate_over_pageable_resource(resource_func, {'query_params': {}})

        assert [] == list(items)

    def test_iterate_over_pageable_resource_with_one_page(self):
        resource_func = mock.Mock(side_effect=[
            {'items': ['foo', 'bar']},
            {'items': []},
        ])

        items = iterate_over_pageable_resource(resource_func, {'query_params': {}})

        assert ['foo', 'bar'] == list(items)
        resource_func.assert_has_calls([
            call(params={'query_params': {'offset': 0, 'limit': 10}}),
            call(params={'query_params': {'offset': 10, 'limit': 10}})
        ])

    def test_iterate_over_pageable_resource_with_multiple_pages(self):
        resource_func = mock.Mock(side_effect=[
            {'items': ['foo']},
            {'items': ['bar']},
            {'items': ['buzz']},
            {'items': []},
        ])

        items = iterate_over_pageable_resource(resource_func, {'query_params': {}})

        assert ['foo', 'bar', 'buzz'] == list(items)

    def test_iterate_over_pageable_resource_should_preserve_query_params(self):
        resource_func = mock.Mock(return_value={'items': []})

        items = iterate_over_pageable_resource(resource_func, {'query_params': {'filter': 'name:123'}})

        assert [] == list(items)
        resource_func.assert_called_once_with(params={'query_params': {'filter': 'name:123', 'offset': 0, 'limit': 10}})

    def test_iterate_over_pageable_resource_should_preserve_limit(self):
        resource_func = mock.Mock(side_effect=[
            {'items': ['foo']},
            {'items': []},
        ])

        items = iterate_over_pageable_resource(resource_func, {'query_params': {'limit': 1}})

        assert ['foo'] == list(items)
        resource_func.assert_has_calls([
            call(params={'query_params': {'offset': 0, 'limit': 1}}),
            call(params={'query_params': {'offset': 1, 'limit': 1}})
        ])

    def test_iterate_over_pageable_resource_should_preserve_offset(self):
        resource_func = mock.Mock(side_effect=[
            {'items': ['foo']},
            {'items': []},
        ])

        items = iterate_over_pageable_resource(resource_func, {'query_params': {'offset': 3}})

        assert ['foo'] == list(items)
        resource_func.assert_has_calls([
            call(params={'query_params': {'offset': 3, 'limit': 10}}),
            call(params={'query_params': {'offset': 13, 'limit': 10}})
        ])

    def test_iterate_over_pageable_resource_should_pass_with_string_offset_and_limit(self):
        resource_func = mock.Mock(side_effect=[
            {'items': ['foo']},
            {'items': []},
        ])

        items = iterate_over_pageable_resource(resource_func, {'query_params': {'offset': '1', 'limit': '1'}})

        assert ['foo'] == list(items)
        resource_func.assert_has_calls([
            call(params={'query_params': {'offset': '1', 'limit': '1'}}),
            call(params={'query_params': {'offset': 2, 'limit': '1'}})
        ])
