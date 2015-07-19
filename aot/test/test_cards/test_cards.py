import pytest
import json
from copy import deepcopy
from aot.board import Board
from aot.board import Square
from aot.cards import Card


CARD_DICT = {
    'number_movements': 1,
    'color': 'blue',
    'complementary_colors': set(),
    'name': '',
    'movements_types': list(),
}


@pytest.fixture()
def board():
    with open('aot/resources/games/standard.json') as games:
        game = json.load(games)
        board_description = game['board']
        return Board(board_description)


def test_line_card(board):
    card_properties = deepcopy(CARD_DICT)
    card_properties['movements_types'].append('line')

    card = Card(board, **card_properties)
    assert card.move(board[0, 0]) == set([Square(0, 1, 'BLUE')])

    card_properties['color'] = 'yellow'
    card = Card(board, **card_properties)
    assert card.move(Square(7, 0, 'YELLOW')) == set([
        Square(8, 0, 'YELLOW'),
        Square(6, 0, 'YELLOW')
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
        Square(31, 1, 'BLUE')
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
