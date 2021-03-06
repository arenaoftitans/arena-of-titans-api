################################################################################
# Copyright (C) 2015-2020 by Last Run Contributors.
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

from .. import trumps
from ..board import Color, ColorSet, SquareSet


class Card:
    _board = None
    _color = None
    _colors = set()
    _default_colors = set()
    _default_number_moves = 0
    _description = ""
    _name = ""
    _movements = []
    _number_movements = 0
    _cost = 0
    _special_actions = None
    movements_methods = set()

    def __init__(
        self,
        board,
        color=Color.ALL,
        complementary_colors=None,
        name="",
        description="",
        movements_types=None,
        number_movements=1,
        cost=0,
        special_actions=None,
    ):
        if not complementary_colors:
            complementary_colors = set()
        if not movements_types:
            movements_types = set()

        self.movements_methods = {
            "line": self._line_move,
            "diagonal": self._diagonal_move,
            "knight": self._knight_move,
        }

        self._board = board
        self._color = color
        self._colors = ColorSet(complementary_colors)
        self._colors.add(color)
        self._default_colors = set(self._colors)
        self._description = description
        self._name = name
        self._movements = [self.movements_methods[mvt] for mvt in movements_types]
        self._movements_types = movements_types
        self._default_number_moves = number_movements
        self._number_movements = number_movements
        self._cost = cost
        self._special_actions = special_actions or ()

    def modify_colors(self, colors):
        self._colors = ColorSet(colors)

    def modify_number_moves(self, delta):
        self._number_movements += delta

    def set_special_actions(self, special_action_descriptions):
        self._special_actions = trumps.SpecialActionsList(
            [
                trumps.create_action_from_description(description, self.color)
                for description in special_action_descriptions
            ]
        )

    def move(self, origin):
        number_movements_left = self._number_movements
        possible_squares = SquareSet(initial_squares={origin})
        while number_movements_left > 0:
            possible_squares_per_levels = []
            for possible_origin in possible_squares:
                possible_squares_level = self._move_level(possible_origin)
                possible_squares_per_levels.append(possible_squares_level)

            for possible_squares_per_level in possible_squares_per_levels:
                possible_squares.update(possible_squares_per_level)

            number_movements_left -= 1

        return {
            square for square in possible_squares if not square.occupied and square is not origin
        }

    def _move_level(self, origin):
        possible_squares_level = set()
        for move in self._movements:
            possible_squares_move = move(origin)
            possible_squares_level.update(possible_squares_move)

        return possible_squares_level

    def _line_move(self, origin):
        possible_squares = set()
        new_squares = self._board.get_line_squares(origin, self._colors)
        possible_squares.update(new_squares)

        return possible_squares

    def _diagonal_move(self, origin):
        possible_squares = set()
        new_squares = self._board.get_diagonal_squares(origin, self._colors)
        possible_squares.update(new_squares)

        return possible_squares

    def _knight_move(self, origin):
        possible_squares = set()
        possible_squares.update(self.__knight_get_vertical_squares(origin))

        possible_squares.update(self.__knigt_get_horizontal_square(origin))

        return possible_squares

    def __knight_get_vertical_squares(self, origin):
        probable_squares = self.__knight_get_vertical_squares_vertical_first(origin)
        probable_squares.update(self.__knight_get_vertical_squares_horizontal_first(origin))

        return [
            square
            for square in probable_squares
            if square.color in self._colors and not square.occupied
        ]

    def __knight_get_vertical_squares_vertical_first(self, origin):
        probable_squares = set()
        temporary_vertical_squares = {
            self._board[origin.x, origin.y + 2],
            self._board[origin.x, origin.y - 2],
        }

        for square in temporary_vertical_squares:
            # Squares in temporary_vertical_squares are added by board[] so they
            # can be None.
            if not square:
                continue
            right_square = self._board[square.x + 1, square.y]
            left_square = self._board[square.x - 1, square.y]
            if right_square:
                probable_squares.add(right_square)
            if left_square:
                probable_squares.add(left_square)

        return probable_squares

    def __knight_get_vertical_squares_horizontal_first(self, origin):
        probable_squares = set()
        temporary_horizontal_squares = {
            self._board[origin.x + 1, origin.y],
            self._board[origin.x - 1, origin.y],
        }

        for square in temporary_horizontal_squares:
            if square:
                upper_square = self._board[square.x, square.y + 2]
                lower_square = self._board[square.x, square.y - 2]
                if upper_square:
                    probable_squares.add(upper_square)
                if lower_square:
                    probable_squares.add(lower_square)

        return probable_squares

    def __knigt_get_horizontal_square(self, origin):
        probable_squares = set()

        for square in (self._board[origin.x, origin.y + 1], self._board[origin.x, origin.y - 1]):
            if square:
                probable_squares.update(self.__knight_get_temporary_horizontal_square(square))

        return [
            square
            for square in probable_squares
            if square and square.color in self._colors and not square.occupied
        ]

    def __knight_get_temporary_horizontal_square(self, origin):
        # We must get horizontal squares one step at a time to avoid switching
        # board
        square_left = self._board[origin.x - 1, origin.y]
        square_right = self._board[origin.x + 1, origin.y]
        temporary_horizontal_squares = set()
        if square_left:
            temporary_horizontal_squares.add(self._board[square_left.x - 1, square_left.y])
        if square_right:
            temporary_horizontal_squares.add(self._board[square_right.x + 1, square_right.y])

        return temporary_horizontal_squares

    def remove_color_from_possible_colors(self, color):
        if color == Color.ALL:
            self._colors = set()
        elif color in self._colors:
            self._colors.remove(color)

    def revert_to_default(self):
        self._colors = set(self._default_colors)
        self._number_movements = self._default_number_moves

    @property
    def color(self):
        return self._color

    @property
    def colors(self):
        return self._colors

    @property
    def cost(self):
        return self._cost

    @property
    def description(self):
        return self._description

    @property
    def is_knight(self):  # pragma: no cover
        return self._movements == [self._knight_move]

    @property
    def movements_types(self):  # pragma: no cover
        return self._movements_types

    @property
    def name(self):  # pragma: no cover
        return self._name

    @property
    def special_actions(self):
        return self._special_actions

    def __str__(self):  # pragma: no cover
        return "Card(name={name}, color={color}, colors={colors})".format(
            name=self.name, color=self.color, colors=self.colors
        )

    def __repr__(self):  # pragma: no cover
        return str(self)
