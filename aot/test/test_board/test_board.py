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
    assert board[-1, 0] == Square(31, 0, 'yellow')


def test_get_lines_squares(board):
    assert board.get_line_squares(board[0, 0], set(['blue'])) == set([
        Square(0, 1, 'blue')
    ])
    assert board.get_line_squares(board[7, 0], set(['yellow'])) == set([
        Square(6, 0, 'yellow'),
        Square(8, 0, 'yellow'),
    ])


def test_get_line_squares_multiple_colors(board):
    colors = set(['blue', 'yellow'])
    assert board.get_line_squares(board[0, 0], colors) == set([
        Square(0, 1, 'blue'),
        Square(1, 0, 'yellow'),
        Square(31, 0, 'yellow'),
    ])


def test_get_line_squares_all_colors(board):
    assert board.get_line_squares(board[0, 0], set(['all'])) == set([
        Square(0, 1, 'blue'),
        Square(1, 0, 'yellow'),
        Square(31, 0, 'yellow'),
    ])


def test_get_diagonal_squares(board):
    assert board.get_diagonal_squares(board[0, 0], set(['blue'])) == set([
        Square(1, 1, 'blue'),
        Square(31, 1, 'blue'),
    ])
    assert board.get_diagonal_squares(board[7, 0], set(['blue'])) == set([
        Square(8, 1, 'blue'),
        Square(6, 1, 'blue'),
    ])


def test_get_line_squares_occupied_square(board):
    board[0, 1].occupied = True
    assert board.get_line_squares(board[0, 0], set(['blue'])) == set()


def test_get_line_squares_arm(board):
    assert board.get_line_squares(board[0, 7], set(['black'])) == set()
    assert board.get_line_squares(board[3, 7], set(['red'])) == set()


def test_get_diagonal_squares_multiple_colors(board):
    colors = set(['black', 'yellow'])
    assert board.get_diagonal_squares(board[0, 1], colors) == set([
        Square(31, 0, 'yellow'),
        Square(1, 0, 'yellow'),
        Square(1, 2, 'black'),
        Square(31, 2, 'yellow'),
    ])

def test_get_diagonal_squares_all_colors(board):
    colors = set(['all'])
    assert board.get_diagonal_squares(board[0, 1], colors) == set([
        Square(31, 0, 'yellow'),
        Square(1, 0, 'yellow'),
        Square(1, 2, 'black'),
        Square(31, 2, 'yellow'),
    ])


def test_get_diagonal_squares_on_arm(board):
    assert board.get_diagonal_squares(board[0, 7], set(['black'])) == set()
    assert board.get_diagonal_squares(board[3, 7], set(['red'])) == set()
    assert board.get_diagonal_squares(board[0, 3], set(['yellow'])) == set([
        Square(31, 2, 'yellow'),
        Square(1, 4, 'yellow'),
    ])
    assert board.get_diagonal_squares(board[3, 3], set(['blue'])) == set([
        Square(2, 4, 'blue'),
        Square(4, 2, 'blue'),
    ])
