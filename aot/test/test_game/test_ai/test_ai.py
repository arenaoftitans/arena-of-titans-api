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

import pytest

from aot.cards import Card
from aot.game.ai import (
    find_cheapest_card,
    find_move_to_play,
    distance_covered,
)
from aot.game.ai.pathfinding import a_star
# board is a fixture, ignore the unsued import warnig
from aot.test import board


@pytest.mark.timeout(1)
def test_a_star(board):
    assert len(a_star(board[0, 8], board[19, 8], board)) == 25
    assert len(a_star(board[0, 8], board[18, 8], board)) == 25
    assert len(a_star(board[0, 8], board[17, 8], board)) == 25
    assert len(a_star(board[0, 8], board[16, 8], board)) == 25
    assert len(a_star(board[18, 8], board[19, 8], board)) == 2


@pytest.mark.timeout(1)
def test_distance_difference(board):
    goal = board[19, 8]
    assert distance_covered(board[0, 8], board[18, 8], goal, board) == 23
    assert distance_covered(board[18, 8], board[0, 8], goal, board) == -23
    assert distance_covered(board[18, 8], board[18, 8], goal, board) == 0


def test_find_move_to_play_best_distance(board):
@pytest.mark.timeout(1)
    card1 = Card(board, name='card1', movements_types=['line'], cost=400)
    card2 = Card(board, name='card2', movements_types=['line'], number_movements=2, cost=400)
    hand = [card1, card2]

    result = find_move_to_play(hand, board[0, 8], board[19, 8], board)
    assert result.card == card2
    assert result.square == board[0, 6]


def test_find_move_to_play_same_cost(board):
@pytest.mark.timeout(1)
    card1 = Card(board, name='card1', movements_types=['line'], cost=500)
    card2 = Card(board, name='card2', movements_types=['line'], cost=500)
    hand = [card1, card2]

    result = find_move_to_play(hand, board[0, 8], board[19, 8], board)
    assert result.card == card1
    assert result.square == board[0, 7]


def test_find_move_to_play_best_cost(board):
@pytest.mark.timeout(1)
    card1 = Card(board, name='card1', movements_types=['line'], cost=500)
    card2 = Card(board, name='card2', movements_types=['line'], cost=400)
    hand = [card1, card2]

    result = find_move_to_play(hand, board[0, 8], board[19, 8], board)
    assert result.card == card2
    assert result.square == board[0, 7]


def test_find_move_to_play_no_move(board):
@pytest.mark.timeout(1)
    card1 = Card(board, name='card1')
    card2 = Card(board, name='card2')
    hand = [card1, card2]

    result = find_move_to_play(hand, board[0, 8], board[19, 8], board)
    assert result.card is None
    assert result.square is None


def test_find_move_to_play_backward(board):
@pytest.mark.timeout(1)
    card1 = Card(board, name='card1')
    card2 = Card(board, name='card2')
    hand = [card1, card2]

    board[0, 6].occupied = True
    board[1, 7].occupied = True
    result = find_move_to_play(hand, board[0, 7], board[19, 8], board)
    assert distance_covered(board[0, 7], board[0, 8], board[19, 8], board) == -1
    assert result.card is None
    assert result.square is None


def test_find_cheapest_card_same_cost():
    card1 = Card(board, name='card1')
    card2 = Card(board, name='card2')
    hand = [card1, card2]

    assert find_cheapest_card(hand) == card1


def test_find_cheapest_card():
    card1 = Card(board, name='card1', cost=500)
    card2 = Card(board, name='card2', cost=200)
    hand = [card1, card2]

    assert find_cheapest_card(hand) == card2
