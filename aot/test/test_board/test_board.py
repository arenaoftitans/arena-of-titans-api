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

from .. import board  # noqa: F401
from ...board import (
    Color,
    ColorSet,
    Square,
)
from ...board.square import SquareSet


def test_number_squares(board):  # noqa: F811
    assert len(board) == 288


def test_get_wrong_squares(board):  # noqa: F811
    assert board[None] is None
    assert board[None, None] is None
    assert board[None, None, None] is None
    assert board[None, 0] is None
    assert board[0, None] is None
    assert board[200, 200] is None


def test_square_coords(board):  # noqa: F811
    assert board[0, 0] == Square(0, 0, 'yellow')
    assert board[7, 2] == Square(7, 2, 'yellow')
    assert board[-1, 0] == Square(31, 0, 'yellow')


def test_get_lines_squares(board):  # noqa: F811
    assert board.get_line_squares(board[0, 0], {'blue'}) == {
        Square(0, 1, 'blue'),
    }
    assert board.get_line_squares(board[7, 0], {'yellow'}) == {
        Square(6, 0, 'yellow'),
        Square(8, 0, 'yellow'),
    }


def test_get_line_squares_multiple_colors(board):  # noqa: F811
    colors = {'blue', 'yellow'}
    assert board.get_line_squares(board[0, 0], colors) == {
        Square(0, 1, 'blue'),
        Square(1, 0, 'yellow'),
        Square(31, 0, 'yellow'),
    }


def test_get_line_squares_all_colors(board):  # noqa: F811
    assert board.get_line_squares(board[0, 0], {'all'}) == {
        Square(0, 1, 'blue'),
        Square(1, 0, 'yellow'),
        Square(31, 0, 'yellow'),
    }


def test_get_diagonal_squares(board):  # noqa: F811
    assert board.get_diagonal_squares(board[0, 0], {'blue'}) == {
        Square(1, 1, 'blue'),
        Square(31, 1, 'blue'),
    }
    assert board.get_diagonal_squares(board[7, 0], {'blue'}) == {
        Square(8, 1, 'blue'),
        Square(6, 1, 'blue'),
    }


def test_get_line_squares_occupied_square(board):  # noqa: F811
    board[0, 1].occupied = True
    assert board.get_line_squares(board[0, 0], {'blue'}) == {board[0, 1]}


def test_get_line_squares_arm(board):  # noqa: F811
    assert board.get_line_squares(board[0, 7], {'black'}) == set()
    assert board.get_line_squares(board[3, 7], {'red'}) == set()


def test_get_diagonal_squares_multiple_colors(board):  # noqa: F811
    colors = {'black', 'yellow'}
    assert board.get_diagonal_squares(board[0, 1], colors) == {
        Square(31, 0, 'yellow'),
        Square(1, 0, 'yellow'),
        Square(1, 2, 'black'),
        Square(31, 2, 'yellow'),
    }


def test_get_diagonal_squares_all_colors(board):  # noqa: F811
    colors = {'all'}
    assert board.get_diagonal_squares(board[0, 1], colors) == {
        Square(31, 0, 'yellow'),
        Square(1, 0, 'yellow'),
        Square(1, 2, 'black'),
        Square(31, 2, 'yellow'),
    }


def test_get_diagonal_squares_on_arm(board):  # noqa: F811
    assert board.get_diagonal_squares(board[0, 7], {'black'}) == set()
    assert board.get_diagonal_squares(board[3, 7], {'red'}) == set()
    assert board.get_diagonal_squares(board[0, 3], {'yellow'}) == {
        Square(31, 2, 'yellow'),
        Square(1, 4, 'yellow'),
    }
    assert board.get_diagonal_squares(board[3, 3], {'blue'}) == {
        Square(2, 4, 'blue'),
        Square(4, 2, 'blue'),
    }


def test_square_set_from_color():  # noqa: F811
    assert Color['BLUE'] in SquareSet([Color['BLUE']]).colors


def test_color_set():  # noqa: F811
    assert Color['BLUE'] in ColorSet([Color['BLUE']])


def test_get_neighbors(board):  # noqa: F811
    square = board[0, 8]
    neighbors = board.get_neighbors(square)
    assert neighbors == {
        board[1, 8],
        board[1, 7],
        board[0, 7],
    }

    square = board[1, 7]
    neighbors = board.get_neighbors(square)
    assert neighbors == {
        board[2, 7],
        board[2, 8],
        board[1, 8],
        board[0, 8],
        board[0, 7],
        board[0, 6],
        board[1, 6],
        board[2, 6],
    }


def test_get_neighbors_with_movements_types_line(board):  # noqa: F811
    square = board[0, 8]
    neighbors = board.get_neighbors(square, movements_types={'line'})
    assert neighbors == {
        board[1, 8],
        board[0, 7],
    }


def test_get_neighbors_with_movements_types_diagonal(board):  # noqa: F811
    square = board[0, 8]
    neighbors = board.get_neighbors(square, movements_types={'diagonal'})
    assert neighbors == {
        board[1, 7],
    }


def test_get_neighbors_with_movements_types_all(board):  # noqa: F811
    square = board[0, 8]
    neighbors = board.get_neighbors(square, movements_types={'diagonal', 'line'})
    assert neighbors == {
        board[1, 8],
        board[1, 7],
        board[0, 7],
    }


def test_get_neighbors_x1_circle(board):  # noqa: F811
    square = board[0, 1]
    neighbors = board.get_neighbors(square, movements_types={'diagonal', 'line'})
    assert neighbors == {
        board[0, 0],
        board[1, 0],
        board[1, 1],
        board[1, 2],
        board[0, 2],
        board[31, 2],
        board[31, 1],
        board[31, 0],
    }


def test_get_neighbors_x31_circle(board):  # noqa: F811
    square = board[31, 1]
    neighbors = board.get_neighbors(square, movements_types={'diagonal', 'line'})
    assert neighbors == {
        board[0, 0],
        board[0, 1],
        board[0, 2],
        board[30, 2],
        board[30, 1],
        board[30, 0],
        board[31, 0],
        board[31, 2],
    }
