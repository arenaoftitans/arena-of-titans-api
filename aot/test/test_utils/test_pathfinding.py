################################################################################
# Copyright (C) 2016 by Arena of Titans Contributors.
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

from collections import namedtuple

import pytest

from ...utils.pathfinding import heuristic_cost_estimate

MockedSquare = namedtuple("MockedSquare", "x y")


class MockedBoard:
    arms_width = 4

    def get_arm_id(self, square):
        if square.x >= 29:
            return 7
        elif square.x >= 4:
            return 2

        return 1


@pytest.fixture
def board():
    return MockedBoard()


def test_heuristic_cost_estimate_x1_y1__x2_y1(board):  # noqa: F811
    start = MockedSquare(x=1, y=1)
    goal = MockedSquare(x=2, y=1)
    assert heuristic_cost_estimate(start, goal, board) == 10


def test_heuristic_cost_estimate_x1_y1__x1_y2(board):  # noqa: F811
    start = MockedSquare(x=1, y=1)
    goal = MockedSquare(x=1, y=2)
    assert heuristic_cost_estimate(start, goal, board) == 10


def test_heuristic_cost_estimate_x1_y1__x2_y2(board):  # noqa: F811
    start = MockedSquare(x=1, y=1)
    goal = MockedSquare(x=2, y=2)
    assert heuristic_cost_estimate(start, goal, board) == 10


def test_heuristic_cost_estimate_x1_y1__x3_y1(board):  # noqa: F811
    start = MockedSquare(x=1, y=1)
    goal = MockedSquare(x=3, y=1)
    assert heuristic_cost_estimate(start, goal, board) == 20


def test_heuristic_cost_estimate_x1_y1__x1_y3(board):  # noqa: F811
    start = MockedSquare(x=1, y=1)
    goal = MockedSquare(x=1, y=3)
    assert heuristic_cost_estimate(start, goal, board) == 20


def test_heuristic_cost_estimate_x1_y1__x3_y3(board):  # noqa: F811
    start = MockedSquare(x=1, y=1)
    goal = MockedSquare(x=3, y=3)
    assert heuristic_cost_estimate(start, goal, board) == 20


def test_heuristic_cost_estimate_x1_y1__x2_y3(board):  # noqa: F811
    start = MockedSquare(x=1, y=1)
    goal = MockedSquare(x=2, y=3)
    assert heuristic_cost_estimate(start, goal, board) == 20


def test_heuristic_cost_estimate_x1_y1__x3_y2(board):  # noqa: F811
    start = MockedSquare(x=1, y=1)
    goal = MockedSquare(x=3, y=2)
    assert heuristic_cost_estimate(start, goal, board) == 20
