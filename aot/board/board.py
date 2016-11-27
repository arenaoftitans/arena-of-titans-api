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

from aot.board.square import (
    Square,
    SquareSet,
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
        on_circle = not self._on_arm(square.y)
        squares.add(self[square.x - 1, square.y - 1, 'left', on_circle])
        squares.add(self[square.x + 1, square.y - 1, 'right', on_circle])
        squares.add(self[square.x - 1, square.y + 1, 'left', on_circle])
        squares.add(self[square.x + 1, square.y + 1, 'right', on_circle])
        return squares

    def get_neighbors(self, square):
        neighbors = set()
        neighbors.update(self.get_line_squares(square, ['all']))
        neighbors.update(self.get_diagonal_squares(square, ['all']))
        return neighbors

    def _correct_x(self, x):
        """Correct the absissa, ie make it positive and congrent to _x_max

        **PARAMETERS**

        * *x* - integer or tuple of coordonates
        """
        coords = None
        if isinstance(x, tuple):
            coords = x
            x_direction = None
            on_circle = False
            if len(coords) == 2:
                x, y = coords
            elif len(coords) == 3:
                x, y, x_direction = coords
            elif len(coords) == 4:
                x, y, x_direction, on_circle = coords

        if coords is not None and x is not None:
            x = self.correct_x(x)
            return (x, y, x_direction, on_circle)
        else:
            return None, None, None, False

    def correct_x(self, x):
        while x < 0:
            x += self._x_max
        x = x % self._x_max
        return x

    def _on_arm_edge(self, x, y, x_direction):
        on_arm = self._on_arm(y)
        if x_direction == 'left':
            # When going left, x from original square is x + 1
            return (x + 1) % self._arms_width == 0 and on_arm
        elif x_direction == 'right':
            # When going right, x from original square is x - 1
            return (x - 1) % self._arms_width == self._arms_width - 1 \
                and on_arm
        else:
            return False

    def _on_arm(self, y):
        return y > self._inner_circle_higher_y

    def __len__(self):  # pragma: no cover
        return len(self._board) * len(self._board[0])

    def __getitem__(self, coords):
        """Return the square at the given coordonates

        **PARAMTERS**

        * *coords* - tuple of coordonates. Use a third optional element to
          indicate horizontal direction (among 'left', 'right'). Use a forth optional element to
          indicate if you are currenctly on the circle.
        """
        x, y, x_direction, on_circle = self._correct_x(coords)

        if y is not None and \
                self._edge_move_valid(on_circle, x, y, x_direction) and \
                self._y_in_bounds(y):
            return self._board[y][x]

    def _edge_move_valid(self, on_circle, x, y, x_direction):
        # If the start square is on the circle, we can move in any arm.
        # If it is not, we need to check the arm edge rules.
        return on_circle or not self._on_arm_edge(x, y, x_direction)

    def _y_in_bounds(self, y):
        return 0 <= y and y < self._y_max

    def is_in_arm(self, square):
        return square.y > self._inner_circle_higher_y

    @property
    def _x_max(self):
        return len(self._board[0])

    @property
    def _y_max(self):
        return len(self._board)
