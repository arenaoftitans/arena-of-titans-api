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

from copy import deepcopy

import pytest

from aot.game.board import Color, ColorSet, Square
from aot.game.cards import Card
from aot.game.trumps import SpecialActionsList
from tests.factories import TeleportSpecialActionFactory

CARD_DICT = {
    "number_movements": 1,
    "color": Color.BLUE,
    "complementary_colors": set(),
    "name": "",
    "movements_types": [],
}


@pytest.fixture()
def edge_card_properties():
    card_properties = deepcopy(CARD_DICT)
    card_properties["movements_types"].append("diagonal")
    card_properties["movements_types"].append("line")
    card_properties["color"] = Color.ALL
    return card_properties


def test_set_color_to_special_action():  # noqa: F811
    actions = SpecialActionsList(
        [TeleportSpecialActionFactory(trump_args={"name": "Teleport", "color": Color.RED})]
    )

    card = Card(None, color=Color.RED, special_actions=actions)

    assert len(card.special_actions) == 1
    action = card.special_actions[0]
    assert action.trump.color == Color.RED


def test_line_card(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["movements_types"].append("line")

    card = Card(board, **card_properties)
    assert card.move(board[6, 9]) == {Square(5, 9, Color.BLUE)}

    card_properties["color"] = Color.YELLOW
    card = Card(board, **card_properties)
    assert card.move(Square(9, 4, Color.YELLOW)) == {
        Square(9, 5, Color.YELLOW),
        Square(8, 4, Color.YELLOW),
    }


def test_line_card_two_moves(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["number_movements"] = 2
    card_properties["movements_types"].append("line")
    card_properties["color"] = Color.RED
    board.free_all_squares()

    card = Card(board, **card_properties)
    assert card.move(Square(0, 0, Color.RED)) == {
        Square(0, 1, Color.RED),
        Square(1, 1, Color.RED),
        Square(0, 2, Color.RED),
        Square(x=1, y=0, color=Color.RED),
        Square(x=2, y=0, color=Color.RED),
    }


def test_line_card_occupied_square(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["movements_types"].append("line")

    card = Card(board, **card_properties)
    board[0, 1].occupied = True
    assert card.move(board[0, 0]) == set()


def test_line_card_over_occupied_square(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["movements_types"].append("line")
    card_properties["number_movements"] = 2
    card_properties["color"] = Color.RED
    board.free_all_squares()

    card = Card(board, **card_properties)
    occupied_square = board[0, 1]
    start_square = board[1, 1]
    board[0, 1].occupied = True

    assert len(card.move(start_square)) > 0
    assert occupied_square not in card.move(start_square)


def test_diagonal_card(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["movements_types"].append("diagonal")

    card = Card(board, **card_properties)
    assert card.move(Square(5, 8, Color.RED)) == {
        Square(x=6, y=9, color=Color.BLUE),
    }

    card_properties["number_movements"] = 2
    card = Card(board, **card_properties)
    assert card.move(Square(2, 8, Color.RED)) == {
        Square(x=4, y=8, color=Color.BLUE),
        Square(x=3, y=7, color=Color.BLUE),
        Square(x=2, y=6, color=Color.BLUE),
    }


def test_diagonal_card_occupied_square(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["movements_types"].append("diagonal")

    card = Card(board, **card_properties)
    board[31, 1].occupied = True
    board[1, 1].occupied = True
    board[0, 2].occupied = True
    assert card.move(Square(0, 0, Color.BLUE)) == set()


def test_line_diagonal_card(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["movements_types"].append("diagonal")
    card_properties["movements_types"].append("line")

    card = Card(board, **card_properties)
    assert card.move(Square(5, 8, Color.RED)) == {
        Square(x=6, y=9, color=Color.BLUE),
        Square(x=5, y=9, color=Color.BLUE),
        Square(x=4, y=8, color=Color.BLUE),
    }


def test_line_diagonal_card_two_moves(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["number_movements"] = 2
    card_properties["complementary_colors"] = {Color.RED}
    card_properties["movements_types"].append("diagonal")
    card_properties["movements_types"].append("line")

    card = Card(board, **card_properties)
    assert card.move(Square(8, 2, Color.BLUE)) == {
        Square(x=9, y=2, color=Color.RED),
        Square(x=7, y=2, color=Color.BLUE),
        Square(x=8, y=1, color=Color.BLUE),
        Square(x=10, y=3, color=Color.RED),
        Square(x=8, y=2, color=Color.RED),
        Square(x=6, y=3, color=Color.BLUE),
    }


def test_line_diagonal_card_two_moves2(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["number_movements"] = 2
    card_properties["color"] = Color.RED
    card_properties["movements_types"].append("diagonal")
    card_properties["movements_types"].append("line")

    card = Card(board, **card_properties)
    assert card.move(Square(0, 7, Color.RED)) == {
        Square(2, 8, Color.RED),
        Square(1, 5, Color.RED),
        Square(1, 6, Color.RED),
        Square(1, 7, Color.RED),
    }


def test_line_diagonal_card_two_moves3(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["number_movements"] = 2
    card_properties["color"] = Color.RED
    card_properties["movements_types"].append("diagonal")
    card_properties["movements_types"].append("line")

    card = Card(board, **card_properties)
    assert card.move(Square(0, 8, Color.RED)) == {
        Square(2, 8, Color.RED),
        Square(1, 7, Color.RED),
        Square(1, 6, Color.RED),
    }


def test_multiple_colors_card(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["movements_types"].append("diagonal")
    card_properties["movements_types"].append("line")
    card_properties["color"] = Color.BLUE
    card_properties["complementary_colors"].add(Color.RED)

    card = Card(board, **card_properties)
    assert card.move(board[6, 8]) == {
        Square(x=5, y=7, color=Color.RED),
        Square(x=6, y=9, color=Color.BLUE),
        Square(x=5, y=9, color=Color.BLUE),
        Square(x=6, y=7, color=Color.RED),
    }


def test_knight_no_move(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["movements_types"].append("knight")
    card_properties["color"] = Color.RED

    card = Card(board, **card_properties)
    assert card.move(board[6, 8]) == set()


def test_knight_card(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["movements_types"].append("knight")
    card_properties["color"] = Color.RED

    # Up right
    card = Card(board, **card_properties)
    assert card.move(board[0, 8]) == {
        Square(1, 6, Color.RED),
    }

    # Up left
    assert card.move(board[3, 7]) == {
        Square(1, 6, Color.RED),
    }

    # Down left
    assert card.move(board[1, 6]) == {
        Square(2, 8, Color.RED),
    }

    # Down right
    assert card.move(board[2, 3]) == {
        Square(x=1, y=5, color=Color.RED),
        Square(x=4, y=4, color=Color.RED),
    }


def test_knight_occupied_square(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card_properties["movements_types"].append("knight")
    card_properties["color"] = Color.RED

    board[0, 6].occupied = True
    card = Card(board, **card_properties)
    assert card.move(board[0, 8]) == {
        Square(1, 6, Color.RED),
    }


def test_remove_color_from_possible_colors(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card = Card(board, **card_properties)

    assert card.color in card.colors
    card.remove_color_from_possible_colors(card.color)
    assert card.color not in card.colors

    card.revert_to_default()
    assert card.color in card.colors

    card.remove_color_from_possible_colors(Color["ALL"])
    assert len(card.colors) == 0

    card.revert_to_default()
    assert card.color in card.colors


def test_revert_number_moves(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card = Card(board, **card_properties)
    assert card._number_movements == 1
    card._number_movements = 5

    card.revert_to_default()

    assert card._number_movements == 1


def test_modify_colors(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card = Card(board, **card_properties)
    assert card._colors == ColorSet([Color.BLUE])

    card.modify_colors({Color.RED})

    assert card._colors == {Color.RED}


def test_modify_colors(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card = Card(board, **card_properties)
    assert card._colors == ColorSet([Color.BLUE])

    card.modify_colors({Color.ALL})

    assert isinstance(card._colors, ColorSet)
    assert len(card._colors) == 4


def test_modify_number_moves(board):  # noqa: F811
    card_properties = deepcopy(CARD_DICT)
    card = Card(board, **card_properties)
    assert card._number_movements == 1

    card.modify_number_moves(4)

    assert card._number_movements == 5

    card.modify_number_moves(-2)

    assert card._number_movements == 3
