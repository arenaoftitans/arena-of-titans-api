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


from aot.game.ai import (
    distance_covered,
)
from aot.game.ai.pathfinding import a_star
# board is a fixture, ignore the unsued import warnig
from aot.test import board


def test_a_star(board):
    assert len(a_star(board[0, 8], board[19, 8], board)) == 25
    assert len(a_star(board[18, 8], board[19, 8], board)) == 2


def test_distance_difference(board):
    goal = board[19, 8]
    assert distance_covered(board[0, 8], board[18, 8], goal, board) == 23
    assert distance_covered(board[18, 8], board[0, 8], goal, board) == -23
    assert distance_covered(board[18, 8], board[18, 8], goal, board) == 0
