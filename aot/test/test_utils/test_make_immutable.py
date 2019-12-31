from types import MappingProxyType

import pytest

from ...utils import make_immutable


def test_with_custom_objects():
    class MyClass:
        pass
    obj = MyClass()

    with pytest.raises(ValueError):
        make_immutable(obj)


def test_with_basic_types():
    data = {
        'bool': True,
        'int': 12,
        'float': 89.1,
        'str': 'String',
        'tuple': ('Value', ['Value in list', set()]),
    }

    immutable_data = make_immutable(data)

    with pytest.raises(TypeError):
        immutable_data['test'] = 78
        immutable_data['bool'] = False

    assert isinstance(immutable_data, MappingProxyType)
    assert immutable_data == {
        'bool': True,
        'int': 12,
        'float': 89.1,
        'str': 'String',
        'tuple': ('Value', ('Value in list', frozenset())),
    }
