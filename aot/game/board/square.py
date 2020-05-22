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

from .color import Color, ColorSet


class Square:
    def __init__(self, x, y, color, is_occupied=False, is_arrival=False, is_departure=False):
        self._x = x
        self._y = y
        self._color = color
        self._original_color = self._color
        self._occupied = is_occupied
        self._is_arrival = is_arrival
        self._is_departure = is_departure

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def occupied(self):
        return self._occupied

    @occupied.setter
    def occupied(self, occupied):
        self._occupied = bool(occupied)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if isinstance(color, str):
            color = Color[color]
        self._color = color

    @property
    def is_departure(self):
        return self._is_departure

    @property
    def is_arrival(self):
        return self._is_arrival

    def __eq__(self, other):  # pragma: no cover
        return (
            type(other) == Square
            and other._x == self._x
            and other._y == self._y
            and other._original_color == self._original_color
        )

    def __str__(self):  # pragma: no cover
        return (
            f"Square(x={self.x}, y={self.y}, color={self.color}, "
            f"original_color={self._original_color})"
        )

    def __repr__(self):  # pragma: no cover
        return str(self)

    def __hash__(self):
        return self._x * 10 + self._y * 100 + hash(self._original_color)


class SquareSet(set):
    """Set that can only contains square of a given set of colors."""

    _colors = ColorSet()

    def __init__(self, colors=None, initial_squares=None):
        super()
        if colors is None:
            colors = [Color.ALL]
        self._colors = ColorSet(colors)
        if initial_squares:
            for square in initial_squares:
                self.add(square)

    def add(self, square):
        if square is not None and square.color in self._colors:
            super().add(square)

    @property
    def colors(self):  # pragma: no cover
        return self._colors
