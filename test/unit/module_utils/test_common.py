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

from module_utils.common import requires_update, delete_ref_duplicates


# simple objects

def test_requires_update_return_true_with_different_length():
    assert requires_update(
        {'foo': 1},
        {'foo': 1, 'bar': 2}
    )


def test_requires_update_return_true_with_different_fields():
    assert requires_update(
        {'foo': 1},
        {'bar': 1}
    )


def test_requires_update_return_true_with_different_value_types():
    assert requires_update(
        {'foo': 1},
        {'foo': '1'}
    )


def test_requires_update_return_true_with_different_values():
    assert requires_update(
        {'foo': 1},
        {'foo': 2}
    )


def test_requires_update_return_true_with_different_nested_values():
    assert requires_update(
        {'foo': {'bar': 1}},
        {'foo': {'bar': 2}}
    )


def test_requires_update_return_true_with_different_list_length():
    assert requires_update(
        {'foo': []},
        {'foo': ['bar']}
    )


def test_requires_update_return_false_with_equal_objects():
    assert not requires_update(
        {'foo': 1, 'bar': 2},
        {'bar': 2, 'foo': 1}
    )


def test_requires_update_return_false_with_equal_str_like_values():
    assert not requires_update(
        {'foo': b'bar'},
        {'foo': u'bar'}
    )


def test_requires_update_return_false_with_equal_nested_dicts():
    assert not requires_update(
        {'foo': {'bar': 1, 'buz': 2}},
        {'foo': {'buz': 2, 'bar': 1}}
    )


def test_requires_update_return_false_with_equal_lists():
    assert not requires_update(
        {'foo': ['bar']},
        {'foo': ['bar']}
    )


def test_requires_update_return_false_with_ignored_fields():
    assert not requires_update(
        {'foo': 1, 'version': '123', 'id': '123123'},
        {'foo': 1}
    )


# objects with object references

def test_requires_update_return_false_with_different_ref_ids():
    assert requires_update(
        {'foo': {'id': '1', 'type': 'network', 'ignored_field': 'foo'}},
        {'foo': {'id': '2', 'type': 'network', 'ignored_field': 'bar'}}
    )


def test_requires_update_return_false_with_different_ref_types():
    assert requires_update(
        {'foo': {'id': '1', 'type': 'network', 'ignored_field': 'foo'}},
        {'foo': {'id': '1', 'type': 'accessRule', 'ignored_field': 'bar'}}
    )


def test_requires_update_return_false_with_same_object_refs():
    assert not requires_update(
        {'foo': {'id': '1', 'type': 'network', 'ignored_field': 'foo'}},
        {'foo': {'id': '1', 'type': 'network', 'ignored_field': 'bar'}}
    )


# objects with array of object references

def test_requires_update_return_true_with_different_array_length():
    assert requires_update(
        {'foo': [
            {'id': '1', 'type': 'network', 'ignored_field': 'foo'}
        ]},
        {'foo': []}
    )


def test_requires_update_return_true_with_different_array_order():
    assert requires_update(
        {'foo': [
            {'id': '1', 'type': 'network', 'ignored_field': 'foo'},
            {'id': '2', 'type': 'network', 'ignored_field': 'bar'}
        ]},
        {'foo': [
            {'id': '2', 'type': 'network', 'ignored_field': 'foo'},
            {'id': '1', 'type': 'network', 'ignored_field': 'bar'}
        ]}
    )


def test_requires_update_return_false_with_equal_ref_arrays():
    assert not requires_update(
        {'foo': [
            {'id': '1', 'type': 'network', 'ignored_field': 'foo'}
        ]},
        {'foo': [
            {'id': '1', 'type': 'network', 'ignored_field': 'bar'}
        ]}
    )


# objects with nested structures and object references

def test_requires_update_return_false_with_equal_nested_object_references():
    assert not requires_update(
        {
            'name': 'foo',
            'config': {
                'version': '1',
                'port': {
                    'name': 'oldPortName',
                    'type': 'port',
                    'id': '123'
                }
            }
        },
        {
            'name': 'foo',
            'config': {
                'version': '1',
                'port': {
                    'name': 'newPortName',
                    'type': 'port',
                    'id': '123'
                }
            }
        }
    )


def test_requires_update_return_true_with_different_nested_object_references():
    assert requires_update(
        {
            'name': 'foo',
            'config': {
                'version': '1',
                'port': {
                    'name': 'oldPortName',
                    'type': 'port',
                    'id': '123'
                }
            }
        },
        {
            'name': 'foo',
            'config': {
                'version': '1',
                'port': {
                    'name': 'oldPortName',
                    'type': 'port',
                    'id': '234'
                }
            }
        }
    )


def test_requires_update_return_false_with_equal_nested_list_of_object_references():
    assert not requires_update(
        {
            'name': 'foo',
            'config': {
                'version': '1',
                'ports': [{
                    'name': 'oldPortName',
                    'type': 'port',
                    'id': '123'
                }, {
                    'name': 'oldPortName2',
                    'type': 'port',
                    'id': '234'
                }]
            }
        },
        {
            'name': 'foo',
            'config': {
                'version': '1',
                'ports': [{
                    'name': 'newPortName',
                    'type': 'port',
                    'id': '123'
                }, {
                    'name': 'newPortName2',
                    'type': 'port',
                    'id': '234',
                    'extraField': 'foo'
                }]
            }
        }
    )


def test_requires_update_return_false_with_reference_list_containing_duplicates():
    assert not requires_update(
        {
            'name': 'foo',
            'config': {
                'version': '1',
                'ports': [{
                    'name': 'oldPortName',
                    'type': 'port',
                    'id': '123'
                }, {
                    'name': 'oldPortName',
                    'type': 'port',
                    'id': '123'
                }, {
                    'name': 'oldPortName2',
                    'type': 'port',
                    'id': '234'
                }]
            }
        },
        {
            'name': 'foo',
            'config': {
                'version': '1',
                'ports': [{
                    'name': 'newPortName',
                    'type': 'port',
                    'id': '123'
                }, {
                    'name': 'newPortName2',
                    'type': 'port',
                    'id': '234',
                    'extraField': 'foo'
                }]
            }
        }
    )


def test_delete_ref_duplicates_with_none():
    assert delete_ref_duplicates(None) is None


def test_delete_ref_duplicates_with_empty_dict():
    assert {} == delete_ref_duplicates({})


def test_delete_ref_duplicates_with_simple_object():
    data = {
        'id': '123',
        'name': 'foo',
        'type': 'bar',
        'values': ['a', 'b']
    }
    assert data == delete_ref_duplicates(data)


def test_delete_ref_duplicates_with_object_containing_refs():
    data = {
        'id': '123',
        'name': 'foo',
        'type': 'bar',
        'refs': [
            {'id': '123', 'type': 'baz'},
            {'id': '234', 'type': 'baz'},
            {'id': '234', 'type': 'foo'}
        ]
    }
    assert data == delete_ref_duplicates(data)


def test_delete_ref_duplicates_with_object_containing_duplicate_refs():
    data = {
        'id': '123',
        'name': 'foo',
        'type': 'bar',
        'refs': [
            {'id': '123', 'type': 'baz'},
            {'id': '123', 'type': 'baz'},
            {'id': '234', 'type': 'baz'},
            {'id': '234', 'type': 'baz'},
            {'id': '234', 'type': 'foo'}
        ]
    }
    assert {
               'id': '123',
               'name': 'foo',
               'type': 'bar',
               'refs': [
                   {'id': '123', 'type': 'baz'},
                   {'id': '234', 'type': 'baz'},
                   {'id': '234', 'type': 'foo'}
               ]
           } == delete_ref_duplicates(data)


def test_delete_ref_duplicates_with_object_containing_duplicate_refs_in_nested_object():
    data = {
        'id': '123',
        'name': 'foo',
        'type': 'bar',
        'children': {
            'refs': [
                {'id': '123', 'type': 'baz'},
                {'id': '123', 'type': 'baz'},
                {'id': '234', 'type': 'baz'},
                {'id': '234', 'type': 'baz'},
                {'id': '234', 'type': 'foo'}
            ]
        }
    }
    assert {
               'id': '123',
               'name': 'foo',
               'type': 'bar',
               'children': {
                   'refs': [
                       {'id': '123', 'type': 'baz'},
                       {'id': '234', 'type': 'baz'},
                       {'id': '234', 'type': 'foo'}
                   ]
               }
           } == delete_ref_duplicates(data)
