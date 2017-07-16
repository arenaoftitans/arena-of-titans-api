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

import pytest

from aot.cards.trumps import (
    Gauge,
    SimpleTrump,
)
from aot.test import (
    board,
    gauge,
)
from unittest.mock import MagicMock


def test_can_play(gauge):
    trump = MagicMock()
    trump.cost = 5

    assert not gauge.can_play_trump(trump)

    trump.cost = 0
    assert gauge.can_play_trump(trump)
    gauge._value = 6

    trump.cost = 5
    assert gauge.can_play_trump(trump)


def test_can_play_simple_trump(gauge):
    trump = SimpleTrump('type', 'name', {'cost': 5})

    assert not gauge.can_play_trump(trump)

    gauge._value = 6
    assert gauge.can_play_trump(trump)


def test_move_all_movements_types(gauge, mock):
    a_star = MagicMock(return_value=[None, None, None])
    mock.patch('aot.cards.trumps.gauge.a_star', new=a_star)
    gauge._value = 10
    from_ = MagicMock()
    to = MagicMock()
    card = MagicMock()
    card.is_knight = False
    card.movements_types = ['line', 'diagonal']

    gauge.move(from_, to, card)

    a_star.assert_called_once_with(from_, to, None, movements_types=card.movements_types)
    assert gauge.value == 12


def test_move_line(board):
    # We use the real implementation of a_start with the goal of finding the correct distance
    # traveled by the card.
    gauge = Gauge(board)
    from_ = board[0, 8]
    to = board[1, 7]
    card = MagicMock()
    card.is_knight = False
    card.movements_types = ['line']

    gauge.move(from_, to, card)

    assert gauge.value == 2


def test_move_from_x1_to_x31_circle(board):
    # We use the real implementation of a_start with the goal of finding the correct distance
    # traveled by the card.
    gauge = Gauge(board)
    from_ = board[1, 2]
    to = board[31, 1]
    card = MagicMock()
    card.is_knight = False
    card.movements_types = ['line']

    gauge.move(from_, to, card)

    assert gauge.value == 3


def test_move_empty(gauge, mock):
    a_star = MagicMock(return_value=[])
    mock.patch('aot.cards.trumps.gauge.a_star', new=a_star)
    gauge._value = 10
    from_ = MagicMock()
    to = MagicMock()
    card = MagicMock()
    card.is_knight = False
    card.movements_types = ['line', 'diagonal']

    gauge.move(from_, to, card)

    a_star.assert_called_once_with(from_, to, None, movements_types=['line', 'diagonal'])
    assert gauge.value == 10


def test_move_max(gauge, mock):
    a_star = MagicMock(return_value=[None, None, None])
    mock.patch('aot.cards.trumps.gauge.a_star', new=a_star)
    gauge._value = gauge.MAX_VALUE
    from_ = MagicMock()
    to = MagicMock()
    card = MagicMock()
    card.is_knight = False
    card.movements_types = ['line', 'diagonal']

    gauge.move(from_, to, card)

    a_star.assert_called_once_with(from_, to, None, movements_types=['line', 'diagonal'])
    assert gauge.value == gauge.MAX_VALUE


def test_move_knight(gauge, mock):
    a_star = MagicMock(return_value=[None, None, None])
    mock.patch('aot.cards.trumps.gauge.a_star', new=a_star)
    gauge._value = 10
    from_ = MagicMock()
    to = MagicMock()
    card = MagicMock()
    card.is_knight = True

    gauge.move(from_, to, card)

    assert not a_star.called
    assert gauge.value == 11


def test_move_wrong(gauge):
    card = MagicMock()
    card.is_knight = False
    card.movements_types = ['line', 'diagonal']

    gauge.move(None, None, card)
    assert gauge.value == 0
    gauge.move(MagicMock(), None, card)
    assert gauge.value == 0
    gauge.move(None, MagicMock(), card)
    assert gauge.value == 0


def test_play_trump(gauge):
    gauge._value = 10
    trump = MagicMock()
    trump.cost = 7

    gauge.play_trump(trump)

    assert gauge.value == 3