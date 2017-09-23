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

from copy import deepcopy

import aot

from .. import Card
from ...board import (
    all_colors,
    Color,
)


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
        name='',
        **kwargs,
    ):
        self._cost = cost
        self._description = description
        self._duration = duration
        self._must_target_player = must_target_player
        self._name = name

    def _set_colors(self, color, colors):
        self._colors = set()
        if colors is not None:
            for color in colors:
                self._add_color(color)
        if color is not None:
            self._add_color(color)

    def _add_color(self, color):
        if isinstance(color, str):  # pragma: no cover
            self._colors.add(Color[color])
        else:  # pragma: no cover
            self._colors.add(color)

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

    @cost.setter
    def cost(self, value):  # pragma: no cover
        self._cost = value

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
        must_target_player=False,
        **kwargs,
    ):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name,
            **kwargs,
        )
        self._delta_moves = delta_moves

    def affect(self, player):
        if player and self._duration > 0:
            player.modify_number_moves(self._delta_moves)


class ModifyCardNumberMoves(Trump):
    _delta_moves = 0
    _card_names = None

    def __init__(
        self,
        card_names=None,
        cost=5,
        delta_moves=0,
        description='',
        duration=0,
        name='',
        must_target_player=False,
        **kwargs,
    ):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name,
            **kwargs,
        )
        self._card_names = card_names
        self._delta_moves = delta_moves

    def affect(self, player):
        if self._card_names is not None:
            def card_filter(card: Card):
                return card.name in self._card_names
        else:
            card_filter = None

        if player and self._duration > 0:
            player.modify_card_number_moves(self._delta_moves, card_filter=card_filter)


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
        must_target_player=False,
        **kwargs,
    ):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name,
            **kwargs,
        )
        self._set_colors(color, colors)

    def affect(self, player):
        for color in self._colors:
            player.deck.remove_color_from_possible_colors(color)


class Teleport(Trump):
    # Class variables
    _board = None

    # Instance variables
    _distance = 0
    _colors = None

    def __init__(
        self,
        board=None,
        distance=0,
        color=None,
        colors=None,
        cost=10,
        description='',
        duration=0,
        name='',
        must_target_player=False,
        **kwargs,
    ):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name,
            **kwargs,
        )
        self._distance = distance
        if color is None and colors is None:
            self._colors = deepcopy(all_colors)
        else:
            self._set_colors(color, colors)
        # We use a card to get the list of possible squares for teleportation.
        if Teleport._board is None:
            Teleport._board = aot.get_board()
        board = board or Teleport._board
        self._card = Card(
            board,
            color=next(iter(self._colors)),
            complementary_colors=self._colors,
            name='Teleportation',
            movements_types=['line', 'diagonal'],
            number_movements=distance,
        )

    def affect(self, player, square=None):
        origin_square = player.current_square
        if player and square and square in self._card.move(origin_square):
            player.move(square)

    def view_possible_squares(self, player):
        return self._card.move(player.current_square)

    @property
    def require_target_square(self):
        return True
