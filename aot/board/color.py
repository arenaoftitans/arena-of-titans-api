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

from aot.utils import SimpleEnumMeta


class Color(metaclass=SimpleEnumMeta):
    BLACK = 'BLACK'
    BLUE = 'BLUE'
    RED = 'RED'
    YELLOW = 'YELLOW'
    ALL = 'ALL'


all_colors = set(Color)
all_colors.remove(Color.ALL)


class ColorSet(set):
    '''Set that contains values of the Color Enum.Color

    Convert string to the proper color on addition or update if necessary.
    '''
    def __init__(self, colors=list()):
        super()
        self.update(colors)

    def update(self, colors):
        colors = [Color[color] if isinstance(color, str) else color for color in colors]
        if Color.ALL in colors:
            super().update(all_colors)
        else:
            super().update(colors)

    def add(self, color):
        # To ease unit testing
        if isinstance(color, str):  # pragma: no cover
            color = Color[color]
        if color == Color.ALL:
            self.update([color])
        else:
            super().add(color)
