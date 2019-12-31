################################################################################
# Copyright (C) 2015-2016 by Arena of Titans Contributors.
#
# This file is part of Arena of Titans.
#
# Arena of Titans is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Arena of Titans is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
################################################################################


from time import time
from types import MappingProxyType


def get_time():
    return int(time() * 1000)


def make_immutable(data):
    """Make the supplied data immutable.

    It only works with basic data types like dict, list and sets.
    """
    if isinstance(data, (bool, int, float, str, bytes, type(None))):
        return data
    elif isinstance(data, (tuple, list)):
        # A tuple is immutable but it can be made of things that are not.
        return tuple(make_immutable(elt) for elt in data)
    elif isinstance(data, (set, frozenset)):
        # A frozenset is immutable but it can be made of things that are not.
        return frozenset(make_immutable(elt) for elt in data)
    elif isinstance(data, dict):
        return MappingProxyType({key: make_immutable(value) for key, value in data.items()})
    else:
        raise ValueError(f"{type(data)} cannot be made immutable with basic types.")


class SimpleEnumMeta(type):
    def __new__(metacls, cls, bases, classdict):  # noqa: N804
        object_attrs = set(dir(type(cls, (object,), {})))
        simple_enum_cls = super().__new__(metacls, cls, bases, classdict)
        simple_enum_cls._member_names_ = set(classdict.keys()) - object_attrs
        non_members = set()
        for attr in simple_enum_cls._member_names_:
            if attr.startswith("_") and attr.endswith("_"):
                non_members.add(attr)
            else:
                setattr(simple_enum_cls, attr, attr)

        simple_enum_cls._member_names_.difference_update(non_members)

        return simple_enum_cls

    def __getitem__(cls, key):  # noqa: N805
        return getattr(cls, key.upper())

    def __iter__(cls):  # noqa: N805
        return (name for name in cls._member_names_)

    def __len__(cls):  # pragma: no cover  # noqa: N805
        return len(cls._member_names_)
