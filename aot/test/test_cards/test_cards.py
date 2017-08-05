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

import pytest

from .. import board
from ...board import (
    Color,
    Square,
)
from ...cards import Card
from ...cards.trumps import (
    SimpleTrump,
    TrumpList,
)


CARD_DICT = {
    'number_movements': 1,
    'color': 'blue',
    'complementary_colors': set(),
    'name': '',
    'movements_types': list(),
}


@pytest.fixture()
def edge_card_properties():
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('diagonal')
    card_properties['movements_types'].append('line')
    card_properties['color'] = 'all'
    return card_properties


def test_set_color_to_special_action():
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type='Teleport', args={}))

    card = Card(None, color='red', special_actions=actions)

    assert len(card.special_actions) == 1
    assert isinstance(card.special_actions[0], SimpleTrump)
    action = card.special_actions[0]
    assert action.args == {'color': 'RED'}


def test_line_card(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('line')

    card = Card(board, **card_properties)
    assert card.move(board[0, 0]) == set([Square(0, 1, 'BLUE')])

    card_properties['color'] = 'yellow'
    card = Card(board, **card_properties)
    assert card.move(Square(7, 0, 'YELLOW')) == set([
        Square(8, 0, 'YELLOW'),
        Square(6, 0, 'YELLOW'),
    ])


def test_line_card_two_moves(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['number_movements'] = 2
    card_properties['movements_types'].append('line')

    card = Card(board, **card_properties)
    assert card.move(Square(0, 0, 'BLUE')) == set([
        Square(0, 1, 'BLUE'),
        Square(1, 1, 'BLUE'),
        Square(0, 2, 'BLUE'),
        Square(31, 1, 'BLUE'),
    ])


def test_line_card_occupied_square(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('line')

    card = Card(board, **card_properties)
    board[0, 1].occupied = True
    assert card.move(board[0, 0]) == set()


def test_line_card_over_occupied_square(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('line')
    card_properties['number_movements'] = 2

    card = Card(board, **card_properties)
    board[0, 1].occupied = True
    assert card.move(board[0, 0]) == set([
        board[0, 2],
        board[31, 1],
        board[1, 1],
    ])


def test_diagonal_card(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('diagonal')

    card = Card(board, **card_properties)
    assert card.move(Square(0, 0, 'BLUE')) == set([
        Square(31, 1, 'BLUE'),
        Square(1, 1, 'BLUE'),
    ])

    card_properties['number_movements'] = 2
    card = Card(board, **card_properties)
    assert card.move(Square(0, 0, 'BLUE')) == set([
        Square(31, 1, 'BLUE'),
        Square(1, 1, 'BLUE'),
        Square(0, 2, 'BLUE'),
    ])


def test_diagonal_card_occupied_square(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('diagonal')

    card = Card(board, **card_properties)
    board[31, 1].occupied = True
    board[1, 1].occupied = True
    board[0, 2].occupied = True
    assert card.move(Square(0, 0, 'BLUE')) == set()


def test_diagonal_card_over_occupied_square(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('diagonal')
    card_properties['number_movements'] = 2
    card_properties['complementary_colors'] = ['red']

    card = Card(board, **card_properties)
    board[31, 1].occupied = True
    board[1, 1].occupied = True
    board[0, 2].occupied = True
    assert card.move(Square(0, 0, 'BLUE')) == set([
        board[30, 2],
        board[2, 2],
    ])


def test_line_diagonal_card(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('diagonal')
    card_properties['movements_types'].append('line')

    card = Card(board, **card_properties)
    assert card.move(Square(0, 0, 'BLUE')) == set([
        Square(31, 1, 'BLUE'),
        Square(1, 1, 'BLUE'),
        Square(0, 1, 'BLUE'),
    ])


def test_line_diagonal_card_two_moves(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['number_movements'] = 2
    card_properties['complementary_colors'] = set(['RED'])
    card_properties['movements_types'].append('diagonal')
    card_properties['movements_types'].append('line')

    card = Card(board, **card_properties)
    assert card.move(Square(0, 0, 'BLUE')) == set([
        Square(31, 1, 'BLUE'),
        Square(1, 1, 'BLUE'),
        Square(0, 1, 'BLUE'),
        Square(0, 2, 'BLUE'),
        Square(2, 1, 'RED'),
        Square(2, 2, 'RED'),
        Square(30, 2, 'RED'),
        Square(30, 1, 'BLUE'),
    ])


def test_line_diagonal_card_two_moves2(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['number_movements'] = 2
    card_properties['movements_types'].append('diagonal')
    card_properties['movements_types'].append('line')

    card = Card(board, **card_properties)
    assert card.move(Square(0, 7, 'RED')) == set([
        Square(0, 6, 'BLUE'),
        Square(0, 5, 'BLUE'),
        Square(1, 7, 'BLUE'),
        Square(1, 8, 'BLUE'),
    ])


def test_line_diagonal_card_two_moves3(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['number_movements'] = 2
    card_properties['movements_types'].append('diagonal')
    card_properties['movements_types'].append('line')

    card = Card(board, **card_properties)
    assert card.move(Square(0, 8, 'RED')) == set([
        Square(0, 6, 'BLUE'),
        Square(1, 7, 'BLUE'),
        Square(1, 8, 'BLUE'),
    ])


def test_multiple_colors_card(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('diagonal')
    card_properties['movements_types'].append('line')
    card_properties['color'] = 'blue'
    card_properties['complementary_colors'].add('red')

    card = Card(board, **card_properties)
    assert card.move(board[0, 8]) == set([
        Square(0, 7, 'red'),
        Square(1, 7, 'blue'),
        Square(1, 8, 'blue'),
    ])


def test_line_diagonal_arms_edges(board, edge_card_properties):
    # Bottom left
    edge_card_properties['color'] = 'black'
    card = Card(board, **edge_card_properties)
    assert card.move(board[0, 8]) == set()

    # Bottom right
    edge_card_properties['color'] = 'red'
    card = Card(board, **edge_card_properties)
    assert card.move(board[3, 8]) == set()

    # Up left
    edge_card_properties['color'] = 'all'
    card = Card(board, **edge_card_properties)
    assert card.move(board[0, 3]) == set([
        Square(31, 2, 'yellow'),
        Square(0, 2, 'blue'),
        Square(1, 2, 'black'),
        Square(1, 3, 'yellow'),
        Square(1, 4, 'yellow'),
        Square(0, 4, 'black'),
    ])

    # Up right
    edge_card_properties['color'] = 'all'
    card = Card(board, **edge_card_properties)
    assert card.move(board[3, 3]) == set([
        Square(2, 2, 'red'),
        Square(3, 2, 'yellow'),
        Square(4, 2, 'blue'),
        Square(3, 4, 'red'),
        Square(2, 4, 'blue'),
        Square(2, 3, 'blue'),
    ])


def test_line_diagonal_arms_edges_from_circle(board, edge_card_properties):
    edge_card_properties['movements_types'].remove('line')
    edge_card_properties['color'] = 'black'
    card = Card(board, **edge_card_properties)
    assert card.move(board[31, 2]) == set([board[0, 3]])

    edge_card_properties['color'] = 'red'
    card = Card(board, **edge_card_properties)
    assert card.move(board[4, 2]) == set([
        board[3, 1],
        board[3, 3],
        board[5, 1],
    ])


def test_knight_no_move(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('knight')
    card_properties['color'] = 'red'

    card = Card(board, **card_properties)
    assert card.move(board[3, 8]) == set()


def test_knight_card(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('knight')
    card_properties['color'] = 'red'

    # Up right
    card = Card(board, **card_properties)
    assert card.move(board[0, 8]) == set([
        Square(1, 6, 'red'),
    ])

    # Up left
    assert card.move(board[3, 7]) == set([
        Square(2, 5, 'red'),
        Square(1, 6, 'red'),
    ])

    # Down left
    assert card.move(board[1, 6]) == set([
        Square(0, 8, 'red'),
    ])

    # Down right
    assert card.move(board[0, 4]) == set([
        Square(1, 6, 'red'),
        Square(2, 5, 'red'),
    ])


def test_knight_arm_edge(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('knight')
    card_properties['color'] = 'red'

    # Left edge
    card = Card(board, **card_properties)
    assert card.move(board[0, 6]) == set([
        Square(2, 5, 'red'),
    ])


def test_knight_arm_edge_horizontal(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('knight')
    card_properties['color'] = 'yellow'

    # Left edge
    card = Card(board, **card_properties)
    assert card.move(board[1, 3]) == set([
        Square(3, 2, 'yellow'),
        Square(31, 2, 'yellow'),
    ])


def test_knight_arm_edge_horizontal2(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('knight')
    card_properties['color'] = 'black'

    # Left edge
    card = Card(board, **card_properties)
    assert card.move(board[1, 8]) == set([
        Square(2, 6, 'black'),
        Square(3, 7, 'black'),
    ])


def test_knight_arm_edge_vertical(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('knight')
    card_properties['color'] = 'black'

    # Left edge
    card = Card(board, **card_properties)
    assert card.move(board[0, 4]) == set([
        Square(1, 2, 'black'),
    ])


def test_knight_arm_edge_vertical2(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('knight')
    card_properties['color'] = 'yellow'

    # Left edge
    card = Card(board, **card_properties)
    assert card.move(board[0, 4]) == set([
        Square(31, 2, 'yellow'),
    ])


def test_knight_circle(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('knight')
    card_properties['color'] = 'red'

    card = Card(board, **card_properties)
    assert card.move(board[4, 1]) == set([
        Square(6, 2, 'red'),
        Square(2, 2, 'red'),
        Square(3, 3, 'red'),
    ])


def test_knight_circle_to_arm(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('knight')
    card_properties['color'] = 'black'

    card = Card(board, **card_properties)
    assert card.move(board[3, 2]) == set([
        Square(2, 0, 'black'),
        Square(4, 0, 'black'),
        Square(4, 4, 'black'),
    ])


def test_knight_occupied_square(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('knight')
    card_properties['color'] = 'red'

    board[0, 6].occupied = True
    card = Card(board, **card_properties)
    assert card.move(board[0, 8]) == set([
        Square(1, 6, 'red'),
    ])


def test_remove_color_from_possible_colors(board):
    card_properties = deepcopy(CARD_DICT)
    card = Card(board, **card_properties)

    assert card.color in card.colors
    card.remove_color_from_possible_colors(card.color)
    assert card.color not in card.colors

    card.revert_to_default()
    assert card.color in card.colors

    card.remove_color_from_possible_colors(Color['ALL'])
    assert len(card.colors) == 0

    card.revert_to_default()
    assert card.color in card.colors
