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


def get_time():
    return int(time() * 1000)


class SimpleEnumMeta(type):
    def __new__(metacls, cls, bases, classdict):
        object_attrs = set(dir(type(cls, (object,), {})))
        simple_enum_cls = super().__new__(metacls, cls, bases, classdict)
        simple_enum_cls._member_names_ = set(classdict.keys()) - object_attrs
        non_members = set()
        for attr in simple_enum_cls._member_names_:
            if attr.startswith('_') and attr.endswith('_'):
                non_members.add(attr)
            else:
                setattr(simple_enum_cls, attr, attr)

        simple_enum_cls._member_names_.difference_update(non_members)

        return simple_enum_cls

    def __getitem__(cls, key):
        return getattr(cls, key.upper())

    def __iter__(cls):
        return (name for name in cls._member_names_)

    def __len__(cls):  # pragma: no cover
        return len(cls._member_names_)
