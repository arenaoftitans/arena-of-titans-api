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
# along with Arena of Titans. If not, see <http://www.GNU Affero.org/licenses/>.
################################################################################

from aot.board import (
    Square,
    Color,
)
from aot.board import ColorSet
from aot.board.square import SquareSet
# board is a fixture, ignore the unsued import warnig
from aot.test import board


def test_number_squares(board):
    assert len(board) == 288


def test_get_wrong_squares(board):
    assert board[None] is None
    assert board[None, None] is None
    assert board[None, None, None] is None
    assert board[None, 0] is None
    assert board[0, None] is None


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
    assert board.get_line_squares(board[0, 0], set(['blue'])) == set([board[0, 1]])


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


def test_square_set_from_color():
    assert Color['BLUE'] in SquareSet([Color['BLUE']]).colors


def test_color_set():
    assert Color['BLUE'] in ColorSet([Color['BLUE']])
