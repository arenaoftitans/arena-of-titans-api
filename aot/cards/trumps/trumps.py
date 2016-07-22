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

from aot.board import Color


class Trump:
    _name = ''
    _duration = 0
    _description = ''
    _must_target_player = False
    _initiator = ''

    def __init__(
            self,
            duration=0,
            cost=5,
            description='',
            must_target_player=False,
            name=''):
        self._cost = cost
        self._description = description
        self._duration = duration
        self._must_target_player = must_target_player
        self._name = name

    def consume(self):
        self._duration -= 1

    def __str__(self):  # pragma: no cover
        return '{type}(duration={duration}, cost={cost}, must_target_player={must_target_player}, '
        'name={name})'\
            .format(
                type=type(self).__name__,
                duration=self.duration,
                cost=self.cost,
                must_target_player=self.must_target_player,
                name=self.name)

    def __repr___(self):  # pragma: no cover
        return str(self)

    @property
    def cost(self):  # pragma: no cover
        return self._cost

    @property
    def description(self):  # pragma: no cover
        return self._description

    @property
    def duration(self):  # pragma: no cover
        return self._duration

    @property
    def must_target_player(self):  # pragma: no cover
        return self._must_target_player

    @property
    def name(self):  # pragma: no cover
        return self._name

    @property
    def initiator(self):  # pragma: no cover
        return self._initiator

    @initiator.setter
    def initiator(self, initiator):  # pragma: no cover
        self._initiator = initiator


class ModifyNumberMoves(Trump):
    _delta_moves = 0

    def __init__(
            self,
            cost=5,
            delta_moves=0,
            description='',
            duration=0,
            name='',
            must_target_player=False):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name)
        self._delta_moves = delta_moves

    def affect(self, player):
        if player and self._duration > 0:
            player.modify_number_moves(self._delta_moves)


class RemoveColor(Trump):
    _colors = set()

    def __init__(
            self,
            color=None,
            colors=None,
            cost=5,
            description='',
            duration=0,
            name='',
            must_target_player=False):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name)
        self._colors = set()
        if colors is not None:
            for color in colors:
                self._add_color(color)
        if color is not None:
            self._add_color(color)

    def _add_color(self, color):
        if isinstance(color, str):  # pragma: no cover
            self._colors.add(Color[color.upper()])
        else:
            self._colors.add(color)

    def affect(self, player):
        for color in self._colors:
            player.deck.remove_color_from_possible_colors(color)
