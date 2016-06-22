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

import json
import pytest

from aot import get_board_description
from aot.board import SvgBoardCreator


@pytest.fixture()
def svg_board():
    board_description = get_board_description()
    return SvgBoardCreator(board_description)


@pytest.fixture()
def height():
    with open('aot/resources/games/standard.json') as games:
        game_description = json.load(games)['board']
        return len(game_description['inner_circle_colors']) + \
            len(game_description['arms_colors'])


@pytest.fixture()
def width():
    with open('aot/resources/games/standard.json') as games:
        game_description = json.load(games)['board']
        return game_description['number_arms'] * game_description['arms_width']


def test_number_square(svg_board, height, width):
    board_layer = svg_board.svg.xpath(
        './/ns:g[@id="boardLayer"]',
        namespaces=SvgBoardCreator.NS)[0]
    assert len(board_layer) == height * width


def test_paws(svg_board):
    pawn_layer = svg_board.svg.xpath(
        './/ns:g[@id="pawnLayer"]',
        namespaces=SvgBoardCreator.NS)[0]
    assert len(pawn_layer) == 8


def test_str(svg_board):
    assert str(svg_board)
    assert '&gt;' not in str(svg_board)
