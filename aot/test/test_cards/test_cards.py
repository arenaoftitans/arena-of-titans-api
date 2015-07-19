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
    card = Card(board, 1, "blue", None, ['line'])
    expected = set([Square(0, 1, "blue")])
    assert card.move(Square(0, 0, "blue")) == expected
    card = Card(board, 1, "yellow", None, ['line'])
    expected = set([Square(0, 0, "yellow"), Square(6, 0, "yellow")])
    assert card.move(Square(7, 0, "yellow")) == expected


def test_line_card_two_moves(board):
    card = Card(board, 2, "blue", None, ['line'])
    expected = set([
        Square(0, 1, "blue"),
        Square(1, 1, "blue"),
        Square(7, 1, "blue"),
        Square(0, 2, "blue")
    ])
    assert card.move(Square(0, 0, "blue")) == expected


def test_diagonal_card(board):
    card = Card(board, 1, "blue", None, ['diagonal'])
    expected = set([Square(1, 1, "blue"), Square(7, 1, "blue")])
    assert card.move(Square(0, 0, "blue")) == expected
    card = Card(board, 2, "blue", None, ['diagonal'])
    expected = set([
        Square(1, 1, "blue"),
        Square(7, 1, "blue"),
        Square(0, 2, "blue")
    ])
    assert card.move(Square(0, 0, "blue")) == expected


def test_line_diagonal_card(board):
    card = Card(board, 1, "blue", None, ['line', 'diagonal'])
    expected = set([
        Square(0, 1, "blue"),
        Square(1, 1, "blue"),
        Square(7, 1, "blue")
    ])
    assert card.move(Square(0, 0, "blue")) == expected
