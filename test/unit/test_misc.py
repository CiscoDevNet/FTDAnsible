import pytest

from module_utils.misc import equal_dicts


def test_equal_dicts_raise_error_with_wrong_args():
    with pytest.raises(ValueError, match='Arguments must be dictionaries'):
        equal_dicts({}, 'a')


def test_equal_dicts_return_false_with_different_length():
    assert not equal_dicts(
        {'foo': 1},
        {'foo': 1, 'bar': 2}
    )


def test_equal_dicts_return_false_with_different_fields():
    assert not equal_dicts(
        {'foo': 1},
        {'bar': 1}
    )


def test_equal_dicts_return_false_with_different_value_types():
    assert not equal_dicts(
        {'foo': 1},
        {'foo': '1'}
    )


def test_equal_dicts_return_false_with_different_values():
    assert not equal_dicts(
        {'foo': 1},
        {'foo': 2}
    )


def test_equal_dicts_return_false_with_different_nested_values():
    assert not equal_dicts(
        {'foo': {'bar': 1}},
        {'foo': {'bar': 2}}
    )


def test_equal_dicts_return_true_with_equal_dicts():
    assert equal_dicts(
        {'foo': 1, 'bar': 2},
        {'bar': 2, 'foo': 1}
    )


def test_equal_dicts_return_true_with_equal_nested_dicts():
    assert equal_dicts(
        {'foo': {'bar': 1, 'buz': 2}},
        {'foo': {'buz': 2, 'bar': 1}}
    )


def test_equal_dicts_return_true_with_ignored_fields():
    assert equal_dicts(
        {'foo': 1, 'version': '123', 'id': '123123'},
        {'foo': 1}
    )
