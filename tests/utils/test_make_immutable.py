#
#  Copyright (C) 2015-2020 by Arena of Titans Contributors.
#
#  This file is part of Arena of Titans.
#
#  Arena of Titans is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Arena of Titans is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
#

from types import MappingProxyType

import pytest

from aot.game.utils import make_immutable


def test_with_custom_objects():
    class MyClass:
        pass

    obj = MyClass()

    with pytest.raises(ValueError):
        make_immutable(obj)


def test_with_basic_types():
    data = {
        "bool": True,
        "int": 12,
        "float": 89.1,
        "str": "String",
        "tuple": ("Value", ["Value in list", set()]),
    }

    immutable_data = make_immutable(data)

    with pytest.raises(TypeError):
        immutable_data["test"] = 78
        immutable_data["bool"] = False

    assert isinstance(immutable_data, MappingProxyType)
    assert immutable_data == {
        "bool": True,
        "int": 12,
        "float": 89.1,
        "str": "String",
        "tuple": ("Value", ("Value in list", frozenset())),
    }
