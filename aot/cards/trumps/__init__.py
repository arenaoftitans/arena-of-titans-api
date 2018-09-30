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

import copy
from collections import namedtuple
from operator import xor

from .gauge import Gauge
from .powers import (
    CannotBeAffectedByTrumpsPower,
    ModifyCardColorsPower,
    ModifyCardNumberMovesPower,
    Power,
    PreventTrumpActionPower,
)
from .trumps import (
    ModifyCardColors,
    ModifyCardNumberMoves,
    ModifyNumberMoves,
    ModifyTrumpDurations,
    PreventTrumpAction,
    RemoveColor,
    Teleport,
    Trump,
)


power_type_to_class = {
    'CannotBeAffectedByTrumps': CannotBeAffectedByTrumpsPower,
    'ModifyCardColors': ModifyCardColorsPower,
    'ModifyCardNumberMoves': ModifyCardNumberMovesPower,
    'PreventTrumpAction': PreventTrumpActionPower,
}

trump_type_to_class = {
    'ModifyNumberMoves': ModifyNumberMoves,
    'ModifyTrumpDurations': ModifyTrumpDurations,
    'PreventTrumpAction': PreventTrumpAction,
    'RemoveColor': RemoveColor,
    'Teleport': Teleport,
}

SimpleTrump = namedtuple('SimpleTrump', 'type name color args')
SimpleTrump.__new__.__defaults__ = (None, None, None, None)


def create_power(power: SimpleTrump):
    kwargs = copy.copy(power.args)
    return power_type_to_class[power.type](**kwargs)


class TrumpList(list):
    def __init__(self, trumps=None):
        self._additionnal_arguments = {}
        if trumps is not None:
            super().__init__(trumps)
        else:
            super().__init__()

    def set_additionnal_arguments(self, **kwargs):
        self._additionnal_arguments = kwargs

    def __getitem__(self, key):
        if key is None:
            raise IndexError
        elif isinstance(key, (tuple, list)):
            name, color = key
            for trump in self:
                if self._has_proper_name(trump, name) and self._has_proper_color(trump, color):
                    kwargs = copy.copy(trump.args)
                    kwargs.update(self._additionnal_arguments)
                    return trump_type_to_class[trump.type](**kwargs)
            raise IndexError
        elif isinstance(key, int):
            return super().__getitem__(key)
        elif isinstance(key, slice):
            return TrumpList(trumps=super().__getitem__(key))

    def _has_proper_name(self, trump, name):
        if name is None:
            return False
        return trump.name.lower() == name.lower()

    def _has_proper_color(self, trump, color):
        if xor(trump.color is None, color is None):
            return False

        return ((color is None and trump.color is None) or
                trump.color.lower() == color.lower())


__all__ = [
    # Powers
    'ModifyCardColorsPower',
    'ModifyCardNumberMovesPower',
    # Power utils
    'Power',
    # Trumps
    'ModifyCardColors',
    'ModifyCardNumberMoves',
    'ModifyNumberMoves',
    'ModifyTrumpDurations',
    'RemoveColor',
    'SimpleTrump',
    'Teleport',
    # Trump utils
    'Gauge',
    'Trump',
    'TrumpList',
]
