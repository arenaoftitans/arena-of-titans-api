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

from aot.board.color import (
    Color,
    ColorSet,
)


class Square:
    _x = 0
    _y = 0
    _color = None
    _occupied = False

    def __init__(self, x, y, color):
        self._x = x
        self._y = y
        # To ease testing
        if isinstance(color, str):  # pragma: no cover
            self._color = Color[color]
        else:  # pragma: no cover
            self._color = color

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

    def __eq__(self, other):  # pragma: no cover
        return type(other) == Square and \
            other._x == self._x and \
            other._y == self._y and \
            other._color == self._color

    def __str__(self):  # pragma: no cover
        return 'Square({}, {}, {})'.format(self._x, self._y, self._color)

    def __repr__(self):  # pragma: no cover
        return str(self)

    def __hash__(self):
        return self._x * 10 + self._y * 100 + hash(self._color)


class SquareSet(set):
    '''Set that can only contains square of a given set of colors
    '''
    _colors = ColorSet()

    def __init__(self, colors):
        super()
        self._colors = ColorSet(colors)

    def add(self, square):
        if square is not None and square.color in self._colors:
            super().add(square)

    @property
    def colors(self):  # pragma: no cover
        return self._colors
