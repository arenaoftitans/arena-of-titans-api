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

from aot.board.square import (
    Square,
    SquareSet
    )
from aot.board.color import Color


def get_colors_disposition(arms_colors, inner_circle_colors, number_arms):
    disposition = []
    for partial_line in inner_circle_colors:
        number_times_repeat_line = int(number_arms / 2 - 1)
        _append_line_disposition(
            disposition,
            partial_line,
            number_times_repeat_line)

    for partial_line in arms_colors:
        number_times_repeat_line = number_arms - 1
        _append_line_disposition(
            disposition,
            partial_line,
            number_times_repeat_line)

    return disposition


def _append_line_disposition(disposition, partial_line, number_times_repeat_line):
    complete_line = partial_line
    for _ in range(0, number_times_repeat_line):
        complete_line += ',' + partial_line

    disposition.append([Color[color_name]
                       for color_name in complete_line.split(',')])


class Board:
    _arms_width = 0
    _board = []
    _inner_circle_higher_y = 0

    def __init__(self, board_description):
        self._arms_width = board_description['arms_width']
        self._board = []
        self._inner_circle_higher_y = len(
            board_description['inner_circle_colors']) - 1

        self._create_board(board_description)

    def _create_board(self, board_description):
        x, y = 0, 0
        disposition = get_colors_disposition(
            board_description['arms_colors'],
            board_description['inner_circle_colors'],
            board_description['number_arms'])
        for line in disposition:
            line_board = []
            x = 0
            for color in line:
                line_board.append(Square(x, y, color))
                x += 1
            self._board.append(line_board)
            y += 1

    def get_line_squares(self, square, colors):
        squares = SquareSet(colors)
        squares.add(self[square.x - 1, square.y, 'left'])
        squares.add(self[square.x + 1, square.y, 'right'])
        squares.add(self[square.x, square.y - 1])
        squares.add(self[square.x, square.y + 1])
        return squares

    def get_diagonal_squares(self, square, colors):
        squares = SquareSet(colors)
        squares.add(self[square.x - 1, square.y - 1, 'left'])
        squares.add(self[square.x + 1, square.y - 1, 'right'])
        squares.add(self[square.x - 1, square.y + 1, 'left'])
        squares.add(self[square.x + 1, square.y + 1, 'right'])
        return squares

    def _correct_x(self, x):
        """Correct the absissa, ie make it positive and congrent to _x_max

        **PARAMETERS**

        * *x* - integer or tuple of coordonates
        """
        coords = None
        if isinstance(x, tuple):
            coords = x
            if len(coords) == 2:
                x, y = coords
                x_direction = None
            elif len(coords) == 3:
                x, y, x_direction = coords

        if coords is not None and x is not None:
            while x < 0:
                x += self._x_max
            x = x % self._x_max
            return (x, y, x_direction)
        else:
            return None, None, None

    def _on_arm_edge(self, x, y, x_direction):
        on_arm = y > self._inner_circle_higher_y
        if x_direction == 'left':
            # When going left, x from original square is x + 1
            return (x + 1) % self._arms_width == 0 and on_arm
        elif x_direction == 'right':
            # When going right, x from original square is x - 1
            return (x - 1) % self._arms_width == self._arms_width - 1 \
                and on_arm
        else:
            return False

    def __len__(self):  # pragma: no cover
        return len(self._board) * len(self._board[0])

    def __getitem__(self, coords):
        """Return the square at the given coordonates

        **PARAMTERS**

        * *coords* - tuple of coordonates. Use a third optional element to
          indicate horizontal direction (among 'left', 'right')
        """
        x, y, x_direction = self._correct_x(coords)

        if y is not None and not self._on_arm_edge(x, y, x_direction) and \
                0 <= y and y < self._y_max:
            return self._board[y][x]

    @property
    def _x_max(self):
        return len(self._board[0])

    @property
    def _y_max(self):
        return len(self._board)
