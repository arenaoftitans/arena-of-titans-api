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

from .square import Color, Square, SquareSet


class Board:
    def __init__(self, board_description):
        self._board = {}
        self._updated_squares = []
        for square in board_description["squares"]:
            type_ = square["type"]
            try:
                color = Color[board_description["squares-types-to-colors"].get(type_)]
            except KeyError:
                # This is an empty square, existing only to fill the board definition and to
                # calculate some moves.
                color = None

            x = square["x"]
            y = square["y"]
            self._board[(x, y)] = Square(
                x,
                y,
                color,
                is_occupied=square["id"] is None,
                is_arrival=square["is-arrival"],
                is_departure=square["is-departure"],
            )

    def change_color_of_square(self, x, y, color):
        updated_square = self[x, y]
        updated_square.color = color
        self._updated_squares.append(updated_square)

    def free_all_squares(self):
        """Can be used in some tests to move outside the "normal" board on hidden squares."""
        for square in self._board.values():
            square.occupied = False

    def get_line_squares(self, square, colors):
        squares = SquareSet(colors)
        squares.add(self[square.x - 1, square.y])
        squares.add(self[square.x + 1, square.y])
        squares.add(self[square.x, square.y - 1])
        squares.add(self[square.x, square.y + 1])
        return squares

    def get_diagonal_squares(self, square, colors):
        squares = SquareSet(colors)
        squares.add(self[square.x - 1, square.y - 1])
        squares.add(self[square.x + 1, square.y - 1])
        squares.add(self[square.x - 1, square.y + 1])
        squares.add(self[square.x + 1, square.y + 1])
        return squares

    def get_neighbors(self, square, movements_types=None):
        neighbors = set()
        if movements_types is None or "line" in movements_types:
            neighbors.update(self.get_line_squares(square, [Color.ALL]))
        if movements_types is None or "diagonal" in movements_types:
            neighbors.update(self.get_diagonal_squares(square, [Color.ALL]))
        return neighbors

    def get_square_for_player_with_index(self, index):
        departure_squares = [square for square in self._board.values() if square.is_departure]
        return departure_squares[index]

    def __len__(self):  # pragma: no cover
        return len(self._board)

    def __getitem__(self, coords):
        """Return the square at the given coordinates.

        **PARAMETERS**

        * *coords* - tuple of coordinates. Use a third optional element to
          indicate horizontal direction (among 'left', 'right'). Use a forth optional element to
          indicate if you are currently on the circle.
        """
        if coords is None:
            return

        x, y = coords
        try:
            return self._board[(x, y)]
        except KeyError:
            return None

    @property
    def aim(self):
        return [square for square in self._board.values() if square.is_arrival]

    @property
    def updated_squares(self) -> tuple:
        """Tuple of square that were updated (eg changed color) since the start of the game."""
        return tuple(self._updated_squares)
