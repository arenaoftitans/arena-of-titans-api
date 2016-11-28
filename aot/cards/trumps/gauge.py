################################################################################
# Copyright (C) 2016 by Arena of Titans Contributors.
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

from aot.utils.pathfinding import a_star


class Gauge:
    def __init__(self, board, value=0):
        self._board = board
        self._value = value

    def move(self, from_, to, card=None):
        if card is not None and card.is_knight:
            is_knight = True
        else:
            is_knight = False

        if from_ is not None and to is not None:
            if is_knight:
                self._value += 1
            else:
                distance = len(a_star(from_, to, self._board))
                self._value += distance

    def can_play_trump(self, trump):
        if self.value >= trump.cost:
            return True
        else:
            return False

    def play_trump(self, trump):
        self._value -= trump.cost

    @property
    def value(self):
        return self._value
