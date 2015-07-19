import pytest
import json
from aot.board import Board
from aot.board import Square


@pytest.fixture()
def board():
    with open('aot/resources/games/standard.json') as games:
        game = json.load(games)
        board_description = game['board']
        return Board(board_description)


def test_number_squares(board):
    assert len(board) == 288


def test_square_coords(board):
    assert board[0, 0] == Square(0, 0, 'yellow')
    assert board[7, 2] == Square(7, 2, 'yellow')


def test_get_line_squares(board):
    assert board.get_line_squares(board[0, 0], 'blue') == set([
        Square(0, 1, 'blue')
    ])
    assert board.get_line_squares(board[7, 0], 'yellow') == set([
        Square(6, 0, 'yellow'),
        Square(8, 0, 'yellow'),
    ])


def test_get_diagonal_square(board):
    assert board.get_diagonal_squares(board[0, 0], 'blue') == set([
        Square(1, 1, 'blue'),
        Square(31, 1, 'blue'),
    ])
    assert board.get_diagonal_squares(board[7, 0], 'blue') == set([
        Square(8, 1, 'blue'),
        Square(6, 1, 'blue'),
    ])
