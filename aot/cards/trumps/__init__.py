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

from collections import namedtuple

from aot.cards.trumps.trumps import (
    ModifyNumberMoves,
    Trump,
    RemoveColor,
    Teleport,
)


trump_type_to_class = {
    'ModifyNumberMoves': ModifyNumberMoves,
    'RemoveColor': RemoveColor,
    'Teleport': Teleport,
}

SimpleTrump = namedtuple('SimpleTrump', 'type name args')


class TrumpList(list):
    def __init__(self, trumps=None):
        if trumps is not None:
            super().__init__(trumps)
        else:
            super().__init__()

    def __getitem__(self, key):
        if key is None or isinstance(key, str):
            for trump in self:
                if trump.name == key:
                    return trump_type_to_class[trump.type](**trump.args)
            raise IndexError
        elif isinstance(key, int):
            return super().__getitem__(key)
        elif isinstance(key, slice):
            return TrumpList(trumps=super().__getitem__(key))


__all__ = ['ModifyNumberMoves', 'RemoveColor', 'SimpleTrump', 'Teleport', 'Trump', 'TrumpList']
