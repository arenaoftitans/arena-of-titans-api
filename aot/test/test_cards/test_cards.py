import pytest
import json
from aot.board import Board
from aot.board import Square
from aot.cards import Card


@pytest.fixture()
def board():
    with open('games.json') as games:
        game = json.load(games)
        board_description = game['board']
        return Board(board_description)


def test_line_card(board):
    card = Card(board, 1, 'BLUE', None, ['line'])
    assert card.move(Square(0, 0, 'BLUE')) == set([Square(0, 1, 'BLUE')])
    card = Card(board, 1, 'YELLOW', None, ['line'])
    assert card.move(Square(7, 0, 'YELLOW')) == set([
        Square(0, 0, 'YELLOW'),
        Square(6, 0, 'YELLOW')
    ])


def test_line_card_two_moves(board):
    card = Card(board, 2, 'BLUE', None, ['line'])
    assert card.move(Square(0, 0, 'BLUE')) == set([
        Square(0, 1, 'BLUE'),
        Square(1, 1, 'BLUE'),
        Square(7, 1, 'BLUE'),
        Square(0, 2, 'BLUE')
    ])


def test_diagonal_card(board):
    card = Card(board, 1, 'BLUE', None, ['diagonal'])
    assert card.move(Square(0, 0, 'BLUE')) == set([
        Square(1, 1, 'BLUE'),
        Square(7, 1, 'BLUE')
    ])
    card = Card(board, 2, 'BLUE', None, ['diagonal'])
    assert card.move(Square(0, 0, 'BLUE')) == set([
        Square(1, 1, 'BLUE'),
        Square(7, 1, 'BLUE'),
        Square(0, 2, 'BLUE')
    ])


def test_line_diagonal_card(board):
    card = Card(board, 1, 'BLUE', None, ['line', 'diagonal'])
    assert card.move(Square(0, 0, 'BLUE')) == set([
        Square(0, 1, 'BLUE'),
        Square(1, 1, 'BLUE'),
        Square(7, 1, 'BLUE')
    ])
