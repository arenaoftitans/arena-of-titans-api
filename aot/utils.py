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
    elif callable(data):
        return data
    else:
        raise ValueError(f"{type(data)} cannot be made immutable with basic types.")


def remove_mappingproxies(data: dict):
    """Remove mappingproxies from the data structure by copying them.

    It can be required because mappingproxies cannot be pickled.
    """
    if isinstance(data, (bool, int, float, str, bytes, type(None))):
        return data

    data = data.copy()
    for key, value in data.items():
        if isinstance(value, MappingProxyType):
            data[key] = remove_mappingproxies(value)
        elif isinstance(value, (list, tuple)):
            data[key] = tuple(remove_mappingproxies(elts) for elts in value)

    return data
