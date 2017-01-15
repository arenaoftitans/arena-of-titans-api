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
import re
import socket

from aot.cards import Card
from aot.game.ai import (
    find_cheapest_card,
    find_move_to_play,
    distance_covered,
)
from aot.utils.pathfinding import a_star
# board is a fixture, ignore the unsued import warnig
from aot.test import board


# If hostname match a SHA1 (ie run in docker), increase value of TIMEOUT to prevent deploy
# errors. Leave it to 1 in all other cases to detect slowness.
TIMEOUT = 1
if re.match(r'[0-9a-f]{5,40}', socket.gethostname()):
    TIMEOUT = 2


@pytest.fixture
def goal_squares(board):
    return set([board[19, 8]])


@pytest.mark.timeout(TIMEOUT)
def test_a_star(board):
    assert len(a_star(board[0, 8], board[19, 8], board)) == 24
    assert len(a_star(board[0, 8], board[18, 8], board)) == 24
    assert len(a_star(board[0, 8], board[17, 8], board)) == 24
    assert len(a_star(board[0, 8], board[16, 8], board)) == 24
    assert len(a_star(board[18, 8], board[19, 8], board)) == 2


@pytest.mark.timeout(TIMEOUT)
def test_distance_difference(board):
    goal = board[19, 8]
    assert distance_covered(board[0, 8], board[18, 8], goal, board) == 22
    assert distance_covered(board[18, 8], board[0, 8], goal, board) == -22
    assert distance_covered(board[18, 8], board[18, 8], goal, board) == 0


@pytest.mark.timeout(TIMEOUT)
def test_find_move_to_play_best_distance(board, goal_squares):
    card1 = Card(board, name='card1', movements_types=['line'], cost=400)
    card2 = Card(board, name='card2', movements_types=['line'], number_movements=2, cost=400)
    hand = [card1, card2]

    result = find_move_to_play(hand, board[0, 8], goal_squares, board)
    assert result.card == card2
    assert result.square == board[0, 6]


@pytest.mark.timeout(TIMEOUT)
def test_find_move_to_play_same_cost(board, goal_squares):
    card1 = Card(board, name='card1', movements_types=['line'], cost=500)
    card2 = Card(board, name='card2', movements_types=['line'], cost=500)
    hand = [card1, card2]

    result = find_move_to_play(hand, board[0, 8], goal_squares, board)
    assert result.card == card1
    assert result.square == board[0, 7]


@pytest.mark.timeout(TIMEOUT)
def test_find_move_to_play_best_cost(board, goal_squares):
    card1 = Card(board, name='card1', movements_types=['line'], cost=500)
    card2 = Card(board, name='card2', movements_types=['line'], cost=400)
    hand = [card1, card2]

    result = find_move_to_play(hand, board[0, 8], goal_squares, board)
    assert result.card == card2
    assert result.square == board[0, 7]


@pytest.mark.timeout(TIMEOUT)
def test_find_move_to_play_no_move(board, goal_squares):
    card1 = Card(board, name='card1')
    card2 = Card(board, name='card2')
    hand = [card1, card2]

    result = find_move_to_play(hand, board[0, 8], goal_squares, board)
    assert result.card is None
    assert result.square is None


@pytest.mark.timeout(TIMEOUT)
def test_find_move_to_play_backward(board, goal_squares):
    card1 = Card(board, name='card1', movements_types=['line'])
    card2 = Card(board, name='card2', movements_types=['line'])
    hand = [card1, card2]

    board[0, 6].occupied = True
    board[1, 7].occupied = True
    result = find_move_to_play(hand, board[0, 7], goal_squares, board)
    assert distance_covered(board[0, 7], board[0, 8], board[19, 8], board) == -1
    assert result.card is None
    assert result.square is None


@pytest.mark.timeout(TIMEOUT)
def test_find_move_distance_null(board, goal_squares):
    card1 = Card(board, name='card1', movements_types=['line'])
    hand = [card1]

    result = find_move_to_play(hand, board[3, 3], goal_squares, board)

    assert distance_covered(board[3, 3], board[3, 2], board[19, 8], board) == 0
    assert result.card is card1


@pytest.mark.timeout(TIMEOUT)
def test_find_move_distance_null_card1_positive_card2(board, goal_squares):
    card1 = Card(board, name='card1', movements_types=['line'], cost=300)
    card2 = Card(board, name='card2', movements_types=['line', 'diagonal'], cost=400)
    hand = [card1, card2]
    # Square (2, 3) is possible for card1 and reduce the distance to the goal square
    # Make it occupied so we cannot go there and the test tests what it must.
    board[2, 3].occupied = True

    result = find_move_to_play(hand, board[3, 3], goal_squares, board)

    assert distance_covered(board[3, 3], board[3, 2], board[19, 8], board) == 0
    assert result.card is card2


@pytest.mark.timeout(TIMEOUT)
def test_find_move_distance_null_card2_positive_card1(board, goal_squares):
    card1 = Card(board, name='card1', movements_types=['line', 'diagonal'], cost=300)
    card2 = Card(board, name='card2', movements_types=['line'], cost=400)
    hand = [card1, card2]
    # Square (2, 3) is possible for card1 and reduce the distance to the goal square
    # Make it occupied so we cannot go there and the test tests what it must.
    board[2, 3].occupied = True

    result = find_move_to_play(hand, board[3, 3], goal_squares, board)

    assert distance_covered(board[3, 3], board[3, 2], board[19, 8], board) == 0
    assert result.card is card1


@pytest.mark.timeout(TIMEOUT)
def test_find_move_distance_null_with_cheaper_card(board, goal_squares):
    card1 = Card(board, name='card1', movements_types=['line'], cost=500)
    card2 = Card(board, name='card2', movements_types=['line'], cost=400)
    hand = [card1, card2]

    result = find_move_to_play(hand, board[3, 3], goal_squares, board)

    assert distance_covered(board[3, 3], board[3, 2], board[19, 8], board) == 0
    assert result.card is card2


@pytest.mark.timeout(TIMEOUT)
def test_find_move_to_play_full_set_of_goal(board):
    goal_squares = set([board[19, 8], board[18, 8], board[17, 8], board[16, 8]])
    card1 = Card(board, name='card1', movements_types=['line'], cost=500)
    card2 = Card(board, name='card2', movements_types=['line'], cost=400)
    hand = [card1, card2]

    result = find_move_to_play(hand, board[19, 3], goal_squares, board)
    assert result.card is card2
    assert result.square is board[19, 4]


@pytest.mark.timeout(TIMEOUT)
def test_move_to_goal(board):
    # We can use a set here to be sure of the order in which the square will be iterated trough
    # Going from board[16, 7] to board[17, 7] gets us closer of board[19, 8] by one. So we need
    # to evaluate the distance from board[19, 8] first for this test to be valid.
    goal_squares = [board[19, 8], board[18, 8], board[17, 8], board[16, 8]]
    card1 = Card(board, name='card1', movements_types=['line'], cost=400)
    hand = [card1]

    result = find_move_to_play(hand, board[16, 7], goal_squares, board)
    assert result.card is card1
    assert result.square is board[16, 8]


@pytest.mark.timeout(TIMEOUT)
def test_move_to_goal_same_distance_cheapest_card(board):
    # We can use a set here to be sure of the order in which the square will be iterated trough
    # Going from board[16, 7] to board[17, 7] gets us closer of board[19, 8] by one. So we need
    # to evaluate the distance from board[19, 8] first for this test to be valid.
    goal_squares = [board[19, 8], board[18, 8], board[17, 8], board[16, 8]]
    card1 = Card(board, name='card1', movements_types=['line'], cost=800)
    card2 = Card(board, name='card2', movements_types=['line'], color='blue', cost=600)
    hand = [card1, card2]

    result = find_move_to_play(hand, board[16, 7], goal_squares, board)
    assert result.card is card1
    assert result.square is board[16, 8]


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
