from ansible.compat.tests import mock
from ansible.compat.tests.mock import call, patch

from module_utils.config_resource import iterate_over_pageable_resource, BaseConfigurationResource


class TestBaseConfigurationResource(object):

    @patch.object(BaseConfigurationResource, 'send_request')
    def test_get_objects_by_filter_with_multiple_filters(self, send_request_mock):
        objects = [
            {'name': 'obj1', 'type': 1, 'foo': {'bar': 'buzz'}},
            {'name': 'obj2', 'type': 1, 'foo': {'bar': 'buz'}},
            {'name': 'obj3', 'type': 2, 'foo': {'bar': 'buzz'}}
        ]
        resource = BaseConfigurationResource(None)

        send_request_mock.side_effect = [{'items': objects}]
        assert objects == resource.get_objects_by_filter('/objects', {})

        send_request_mock.side_effect = [{'items': objects}]
        assert [objects[0]] == resource.get_objects_by_filter('/objects', {'name': 'obj1'})

        send_request_mock.side_effect = [{'items': objects}]
        assert [objects[1]] == resource.get_objects_by_filter('/objects',
                                                              {'type': 1, 'foo': {'bar': 'buz'}})

    #
    @patch.object(BaseConfigurationResource, 'send_request')
    def test_get_objects_by_filter_with_multiple_responses(self, send_request_mock):
        send_request_mock.side_effect = [
            {'items': [
                {'name': 'obj1', 'type': 'foo'},
                {'name': 'obj2', 'type': 'bar'}
            ]},
            {'items': [
                {'name': 'obj3', 'type': 'foo'}
            ]}
        ]

        resource = BaseConfigurationResource(None)

        assert [
                   {'name': 'obj1', 'type': 'foo'},
                   {'name': 'obj3', 'type': 'foo'},

               ] == resource.get_objects_by_filter('/objects', {'type': 'foo'})


def test_iterate_over_pageable_resource_with_no_items():
    resource_func = mock.Mock(return_value={'items': []})

    items = iterate_over_pageable_resource(resource_func)

    assert [] == list(items)


def test_iterate_over_pageable_resource_with_one_page():
    resource_func = mock.Mock(side_effect=[
        {'items': ['foo', 'bar']},
        {'items': []},
    ])

    items = iterate_over_pageable_resource(resource_func)

    assert ['foo', 'bar'] == list(items)
    resource_func.assert_has_calls([
        call(query_params={'offset': 0, 'limit': 10}),
        call(query_params={'offset': 10, 'limit': 10})
    ])


def test_iterate_over_pageable_resource_with_multiple_pages():
    resource_func = mock.Mock(side_effect=[
        {'items': ['foo']},
        {'items': ['bar']},
        {'items': ['buzz']},
        {'items': []},
    ])

    items = iterate_over_pageable_resource(resource_func)

    assert ['foo', 'bar', 'buzz'] == list(items)


def test_iterate_over_pageable_resource_should_preserve_query_params():
    resource_func = mock.Mock(return_value={'items': []})

    items = iterate_over_pageable_resource(resource_func, {'filter': 'name:123'})

    assert [] == list(items)
    resource_func.assert_called_once_with(query_params={'filter': 'name:123', 'offset': 0, 'limit': 10})


def test_iterate_over_pageable_resource_should_preserve_limit():
    resource_func = mock.Mock(side_effect=[
        {'items': ['foo']},
        {'items': []},
    ])

    items = iterate_over_pageable_resource(resource_func, {'limit': 1})

    assert ['foo'] == list(items)
    resource_func.assert_has_calls([
        call(query_params={'offset': 0, 'limit': 1}),
        call(query_params={'offset': 1, 'limit': 1})
    ])


def test_iterate_over_pageable_resource_should_preserve_offset():
    resource_func = mock.Mock(side_effect=[
        {'items': ['foo']},
        {'items': []},
    ])

    items = iterate_over_pageable_resource(resource_func, {'offset': 3})

    assert ['foo'] == list(items)
    resource_func.assert_has_calls([
        call(query_params={'offset': 3, 'limit': 10}),
        call(query_params={'offset': 13, 'limit': 10})
    ])
