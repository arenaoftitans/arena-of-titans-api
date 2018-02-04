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

from unittest.mock import MagicMock

from .. import (  # noqa: F401
    board,
    deck,
    game,
    player,
)
from ...board import Color
from ...cards.trumps import (
    ModifyCardColors,
    ModifyCardNumberMoves,
    ModifyNumberMoves,
    ModifyTrumpDurations,
    RemoveColor,
    Teleport,
)


def test_affect_modify_number_moves(player):  # noqa: F811
    player.modify_number_moves = MagicMock()
    trump = ModifyNumberMoves(delta_moves=1, duration=1)
    trump.affect(player)
    player.modify_number_moves.assert_called_once_with(1)


def test_affect_modify_number_moves_negative_delta(player):  # noqa: F811
    player.modify_number_moves = MagicMock()
    trump = ModifyNumberMoves(delta_moves=-1, duration=1)
    trump.affect(player)
    player.modify_number_moves.assert_called_once_with(-1)


def test_affect_modify_card_colors(player):  # noqa: F811
    player.modify_card_colors = MagicMock()
    trump = ModifyCardColors(add_colors=['BLACK'], duration=1)

    trump.affect(player)

    player.modify_card_colors.assert_called_once_with({'BLACK'}, filter_=None)


def test_affect_modify_card_colors_with_filter_(player):  # noqa: F811
    player.modify_card_colors = MagicMock()
    trump = ModifyCardColors(add_colors=['BLACK'], card_names=['Queen'], duration=1)
    queen = MagicMock()
    queen.name = 'Queen'
    king = MagicMock()
    king.name = 'King'

    trump.affect(player)

    assert player.modify_card_colors.called
    assert player.modify_card_colors.call_args[0][0] == {'BLACK'}
    assert callable(player.modify_card_colors.call_args[1]['filter_'])
    filter_ = player.modify_card_colors.call_args[1]['filter_']
    assert filter_(queen)
    assert not filter_(king)


def test_affect_modify_card_number_moves(player):  # noqa: F811
    player.modify_card_number_moves = MagicMock()
    trump = ModifyCardNumberMoves(delta_moves=1, duration=1)
    trump.affect(player)
    player.modify_card_number_moves.assert_called_once_with(1, filter_=None)


def test_affect_modify_card_number_moves_with_filter_(player):  # noqa: F811
    player.modify_card_number_moves = MagicMock()
    trump = ModifyCardNumberMoves(delta_moves=1, duration=1, card_names=['Queen'])
    queen = MagicMock()
    queen.name = 'Queen'
    king = MagicMock()
    king.name = 'King'

    trump.affect(player)

    assert player.modify_card_number_moves.called
    assert player.modify_card_number_moves.call_args[0][0] == 1
    assert callable(player.modify_card_number_moves.call_args[1]['filter_'])
    filter_ = player.modify_card_number_moves.call_args[1]['filter_']
    assert filter_(queen)
    assert not filter_(king)


def test_affect_modify_affecting_trump_durations(player):  # noqa: F811
    player.modify_affecting_trump_durations = MagicMock()
    trump = ModifyTrumpDurations(delta_duration=-1, duration=1)
    trump.affect(player)
    player.modify_affecting_trump_durations.assert_called_once_with(-1, filter_=None)


def test_affect_modify_affecting_trump_durations_with_filter_(player):  # noqa: F811
    player.modify_affecting_trump_durations = MagicMock()
    trump = ModifyTrumpDurations(delta_duration=-1, duration=1, trump_names=['Tower'])
    tower = MagicMock()
    tower.name = 'Tower'
    blizzard = MagicMock()
    blizzard.name = 'Blizzard'

    trump.affect(player)

    assert player.modify_affecting_trump_durations.called
    assert player.modify_affecting_trump_durations.call_args[0][0] == -1
    assert callable(player.modify_affecting_trump_durations.call_args[1]['filter_'])
    filter_ = player.modify_affecting_trump_durations.call_args[1]['filter_']
    assert filter_(tower)
    assert not filter_(blizzard)


def test_remove_color(player):  # noqa: F811
    player.deck.remove_color_from_possible_colors = MagicMock()
    card = player.deck.first_card_in_hand
    color = card.color
    trump = RemoveColor(color=color, duration=1)
    trump.affect(player)
    player.deck.remove_color_from_possible_colors.assert_called_once_with(color)


def test_remove_all_colors(player):  # noqa: F811
    player.deck.remove_color_from_possible_colors = MagicMock()
    trump = RemoveColor(color=Color['ALL'], duration=1)
    trump.affect(player)
    player.deck.remove_color_from_possible_colors.assert_called_once_with(Color['ALL'])


def test_remove_multiple_colors(player):  # noqa: F811
    player.deck.remove_color_from_possible_colors = MagicMock()
    card = player.deck.first_card_in_hand
    colors = {card.color, Color['BLACK']}
    trump = RemoveColor(colors=colors, duration=1)
    trump.affect(player)
    assert player.deck.remove_color_from_possible_colors.called
    assert player.deck.remove_color_from_possible_colors.call_count == len(colors)


def test_teleport_no_target_square(board, player):  # noqa: F811
    player.move = MagicMock()
    trump = Teleport(distance=1)

    trump.affect(player)

    assert not player.move.called


def test_teleport_wrong_distance(board, player):  # noqa: F811
    player.move = MagicMock()
    trump = Teleport(distance=1)
    square = board[5, 8]

    trump.affect(player, square=square)

    assert not player.move.called


def test_teleport_wrong_color(board, player):  # noqa: F811
    player.move = MagicMock()
    trump = Teleport(distance=1, color='blue')
    square = board[0, 7]

    trump.affect(player, square=square)

    assert not player.move.called


def test_teleport(board, player):  # noqa: F811
    square = None
    player.move = MagicMock()
    trump = Teleport(distance=1)
    square = board[0, 7]

    trump.affect(player, square=square)

    player.move.assert_called_once_with(square)


def test_teleport_view_possible_squares(player):  # noqa: F811
    trump = Teleport(distance=1)
    trump._card = MagicMock()

    trump.view_possible_squares(player)

    trump._card.move.assert_called_once_with(player.current_square)


def test_player_can_only_be_affected_by_max_affecting_trumps_number_trump(game):  # noqa: F811
    player1 = game.players[0]

    for i in range(player1.MAX_NUMBER_AFFECTING_TRUMPS):
        trump = RemoveColor(colors=[Color['BLACK']], duration=1)
        assert player1._affect_by(trump)
        assert len(player1.affecting_trumps) == i + 1

    trump = RemoveColor(colors=[Color['BLACK']], duration=1)
    assert not player1._affect_by(trump)
    assert len(player1.affecting_trumps) == player1.MAX_NUMBER_AFFECTING_TRUMPS
