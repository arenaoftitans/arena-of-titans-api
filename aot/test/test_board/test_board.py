import pytest
import json
from aot.board import Board
from aot.board import Square


@pytest.fixture()
def board():
    with open('games.json') as games:
        game = json.load(games)
        board_description = game['board']
        return Board(board_description)


def test_number_squares(board):
    assert len(board) == 24


def test_square_coords(board):
    assert board[0, 0] == Square(0, 0, "yellow")
    assert board[7, 2] == Square(7, 2, "yellow")


def test_get_line_squares(board):
    assert board.get_line_squares(Square(0, 0, "yellow"), "blue") == set([
        Square(0, 1, "blue")
    ])
    assert board.get_line_squares(Square(7, 0, "yellow"), "yellow") == set([
        Square(0, 0, "yellow"),
        Square(6, 0, "yellow")
    ])


def test_get_diagonal_square(board):
    assert board.get_diagonal_squares(Square(0, 0, "yellow"), "blue") == set([
        Square(1, 1, "blue"),
        Square(7, 1, "blue")
    ])
    assert board.get_diagonal_squares(Square(7, 0, "blue"), "blue") == set([
        Square(0, 1, "blue"),
        Square(6, 1, "blue")
    ])
