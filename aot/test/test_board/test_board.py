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


def test_get_wrong_squares(board):  # noqa: F811
    assert board[None] is None
    assert board[None, None] is None
    assert board[None, 0] is None
    assert board[0, None] is None
    assert board[200, 200] is None
    assert board[-1, 0] is None


def test_square_coords(board):  # noqa: F811
    assert board[0, 0] == Square(0, 0, "red")
    assert board[7, 2] == Square(7, 2, "blue")


def test_get_lines_squares(board):  # noqa: F811
    assert board.get_line_squares(board[6, 8], {"blue"}) == {
        Square(6, 9, "blue"),
    }
    assert board.get_line_squares(board[6, 8], {"yellow"}) == {
        Square(5, 8, "yellow"),
    }


def test_get_line_squares_multiple_colors(board):  # noqa: F811
    colors = {"red", "yellow"}
    assert board.get_line_squares(board[5, 7], colors) == {
        Square(x=5, y=8, color="YELLOW"),
        Square(x=6, y=7, color="RED"),
        Square(x=5, y=6, color="RED"),
    }


def test_get_line_squares_all_colors(board):  # noqa: F811
    assert board.get_line_squares(board[6, 8], {"all"}) == {
        Square(x=6, y=9, color="BLUE"),
        Square(x=6, y=7, color="RED"),
        Square(x=7, y=8, color="RED"),
        Square(x=5, y=8, color="YELLOW"),
    }


def test_get_diagonal_squares(board):  # noqa: F811
    assert board.get_diagonal_squares(board[5, 7], {"all"}) == {
        Square(x=4, y=6, color="BLACK"),
        Square(x=4, y=8, color="BLUE"),
        Square(x=6, y=6, color="RED"),
        Square(x=6, y=8, color="YELLOW"),
    }
    assert board.get_diagonal_squares(board[5, 7], {"blue"}) == {
        Square(x=4, y=8, color="BLUE"),
    }


def test_get_line_squares_occupied_square(board):  # noqa: F811test_find_move_to_play_same_cost
    board[0, 1].occupied = True
    assert board.get_line_squares(board[0, 0], {"red"}) == {board[0, 1], board[1, 0]}


def test_get_line_squares_arm(board):  # noqa: F811
    assert board.get_line_squares(board[0, 7], {"black"}) == set()
    assert board.get_line_squares(board[3, 7], {"red"}) == set()


def test_get_diagonal_squares_multiple_colors(board):  # noqa: F811
    colors = {"blue", "yellow"}
    assert board.get_diagonal_squares(board[5, 7], colors) == {
        Square(x=4, y=8, color="BLUE"),
        Square(x=6, y=8, color="YELLOW"),
    }


def test_get_diagonal_squares_all_colors(board):  # noqa: F811
    colors = {"all"}
    assert board.get_diagonal_squares(board[6, 8], colors) == {
        Square(x=5, y=7, color="RED"),
        Square(x=5, y=9, color="BLUE"),
        Square(x=7, y=9, color="RED"),
        Square(x=7, y=7, color="RED"),
    }


def test_square_set_from_color():  # noqa: F811
    assert Color["BLUE"] in SquareSet([Color["BLUE"]]).colors


def test_color_set():  # noqa: F811
    assert Color["BLUE"] in ColorSet([Color["BLUE"]])


def test_get_neighbors(board):  # noqa: F811
    square = board[0, 8]
    neighbors = board.get_neighbors(square)
    assert neighbors == {
        board[1, 8],
        board[1, 7],
        board[0, 7],
        board[0, 9],
        board[1, 9],
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
    neighbors = board.get_neighbors(square, movements_types={"line"})
    assert neighbors == {
        board[1, 8],
        board[0, 7],
        board[0, 9],
    }


def test_get_neighbors_with_movements_types_diagonal(board):  # noqa: F811
    square = board[0, 8]
    neighbors = board.get_neighbors(square, movements_types={"diagonal"})
    assert neighbors == {
        board[1, 7],
        board[1, 9],
    }


def test_get_neighbors_with_movements_types_all(board):  # noqa: F811
    square = board[0, 8]
    neighbors = board.get_neighbors(square, movements_types={"diagonal", "line"})
    assert neighbors == {
        board[1, 9],
        board[1, 8],
        board[0, 9],
        board[0, 7],
        board[1, 7],
    }
