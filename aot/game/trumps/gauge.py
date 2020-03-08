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

from aot.game.ai.pathfinding import a_star


class Gauge:
    MAX_VALUE = 40

    def __init__(self, board, value=0):
        self._board = board
        self._value = value

    def move(self, from_, to, card):
        if card is not None and card.is_knight:
            is_knight = True
        else:
            is_knight = False

        if from_ is not None and to is not None:
            if is_knight:
                self._value += 1
            else:
                # The list returned by a_star always contain the 1st and last square. Which means
                # it over-evaluate the distance by 1.
                path = a_star(from_, to, self._board, movements_types=card.movements_types)
                distance = len(path) - 1
                if distance > 0:
                    self._value += distance

        if self.value > self.MAX_VALUE:
            self._value = self.MAX_VALUE

    def can_play_trump(self, trump):
        # We are dealing with a SimpleTrump. play_trump must be called with a trump.
        if hasattr(trump, "cost"):
            cost = trump.cost
        else:
            cost = trump.args["cost"]

        if self.value >= cost:
            return True
        else:
            return False

    def play_trump(self, trump):
        self._value -= trump.cost

    @property
    def value(self):
        return self._value
