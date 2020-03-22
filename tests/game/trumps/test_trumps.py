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

import pytest

from aot.game.board import Color
from aot.game.trumps import (
    CannotBeAffectedByTrumps,
    ModifyCardColors,
    ModifyCardNumberMoves,
    ModifyNumberMoves,
    ModifyTrumpDurations,
    PreventTrumpAction,
    RemoveColor,
    SimpleTrump,
    Teleport,
    TrumpList,
)
from aot.game.trumps.exceptions import MaxNumberAffectingTrumpsError, TrumpHasNoEffectError

from ...utilities import AnyFunction


@pytest.fixture()
def initiator(player):
    return player


@pytest.fixture()
def target(player2):
    return player2


@pytest.fixture()
def red_tower_trump():
    return RemoveColor(name="Tower", color=Color.RED, cost=4, duration=1, must_target_player=True)


@pytest.fixture()
def blizzard_trump():
    return ModifyNumberMoves(
        delta_moves=-1, duration=1, cost=4, name="Blizzard", must_target_player=True
    )


def test_affect_modify_number_moves(initiator, target):
    target.modify_number_moves = MagicMock()
    trump = ModifyNumberMoves(delta_moves=1, duration=1)

    effect = trump.create_effect(initiator=initiator, target=target, context={})
    effect.apply()

    target.modify_number_moves.assert_called_once_with(1)


def test_affect_modify_number_moves_negative_delta(initiator, target):
    target.modify_number_moves = MagicMock()
    trump = ModifyNumberMoves(delta_moves=-1, duration=1)

    effect = trump.create_effect(initiator=initiator, target=target, context={})
    effect.apply()

    target.modify_number_moves.assert_called_once_with(-1)


def test_affect_modify_card_colors(initiator, target):
    target.modify_card_colors = MagicMock()
    trump = ModifyCardColors(colors={Color.BLACK}, duration=1)

    effect = trump.create_effect(initiator=initiator, target=target, context={})
    effect.apply()

    target.modify_card_colors.assert_called_once_with({"BLACK"}, filter_=AnyFunction())


def test_affect_modify_card_colors_with_filter(target, initiator):
    target.modify_card_colors = MagicMock()
    trump = ModifyCardColors(colors={Color.BLACK}, card_names=["Queen"], duration=1)
    queen = MagicMock()
    queen.name = "Queen"
    king = MagicMock()
    king.name = "King"

    effect = trump.create_effect(initiator=initiator, target=target, context={})
    effect.apply()

    assert target.modify_card_colors.called
    assert target.modify_card_colors.call_args[0][0] == {"BLACK"}
    assert callable(target.modify_card_colors.call_args[1]["filter_"])
    filter_ = target.modify_card_colors.call_args[1]["filter_"]
    assert filter_(queen)
    assert not filter_(king)


def test_affect_modify_card_number_moves(initiator, target):
    target.modify_card_number_moves = MagicMock()
    trump = ModifyCardNumberMoves(delta_moves=1, duration=1)

    effect = trump.create_effect(initiator=initiator, target=target, context={})
    effect.apply()

    target.modify_card_number_moves.assert_called_once_with(1, filter_=AnyFunction())


def test_affect_modify_card_number_moves_with_filter_(target, initiator):
    target.modify_card_number_moves = MagicMock()
    trump = ModifyCardNumberMoves(delta_moves=1, duration=1, card_names=["Queen"])
    queen = MagicMock()
    queen.name = "Queen"
    king = MagicMock()
    king.name = "King"

    effect = trump.create_effect(initiator=initiator, target=target, context={})
    effect.apply()

    assert target.modify_card_number_moves.called
    assert target.modify_card_number_moves.call_args[0][0] == 1
    assert callable(target.modify_card_number_moves.call_args[1]["filter_"])
    filter_ = target.modify_card_number_moves.call_args[1]["filter_"]
    assert filter_(queen)
    assert not filter_(king)


def test_affect_modify_affecting_trump_durations(initiator, target):  # noqa: F811
    target.modify_affecting_trump_durations = MagicMock()
    trump = ModifyTrumpDurations(delta_duration=-1, duration=1)

    with pytest.raises(TrumpHasNoEffectError):
        effect = trump.create_effect(initiator=initiator, target=target, context={})
        effect.apply()

    assert not target.modify_affecting_trump_durations.called


def test_affect_modify_affecting_trump_durations_with_filter_(
    initiator, target, red_tower_trump, blizzard_trump
):  # noqa: F811
    trump = ModifyTrumpDurations(delta_duration=-1, duration=1, trump_names=("Tower",))
    tower_effect = red_tower_trump.create_effect(initiator=initiator, target=target, context={})
    blizzard_effect = blizzard_trump.create_effect(initiator=initiator, target=target, context={})
    target._affecting_trumps = [
        tower_effect,
        blizzard_effect,
    ]

    effect = trump.create_effect(initiator=initiator, target=target, context={})
    effect.apply()

    assert tower_effect.duration == 0
    assert blizzard_effect.duration == 1
    assert target._affecting_trumps == [blizzard_effect]


def test_prevent_trump_action_dont_enable_on_relevant_trump(player, player2):  # noqa: F811
    """Test that we only prevent the action of proper trumps.

    GIVEN: a prevent action trump enabled on 'Tower' trumps to prevent the 'Ram' trump for player.
    GIVEN: a Fortress trump that affects player 2
    GIVEN: a Ram trump for player 2
    WHEN: player 2 plays the Ram trump to cancel the Fortress
    THEN: it works.
    """
    # Setup player.
    prevent_action_trump = PreventTrumpAction(
        name="Impassable Trump", prevent_trumps_to_modify=["Ram"], enable_for_trumps=["Tower"],
    )
    trump_not_to_improve = SimpleTrump(
        type="RemoveColor", name="Fortress", args={"duration": 2, "name": "Fortress"},
    )
    player._available_trumps = TrumpList([trump_not_to_improve])
    effect = prevent_action_trump.create_effect(initiator=player, target=player, context={})
    effect.apply()
    fortress = player._available_trumps["Fortress", None]
    player._can_play = True
    player.play_trump(fortress, target=player2, context={})
    # Setup trump to play.
    ram = ModifyTrumpDurations(
        name="Ram", trump_names=("Tower", "Fortress"), duration=1, delta_duration=-1,
    )

    ram.create_effect(initiator=player2, target=player2, context={}).apply()

    fortress_effect = player2.affecting_trumps[0]
    assert len(player2.affecting_trumps) == 1
    assert fortress_effect.duration == 1

    ram.create_effect(initiator=player2, target=player2, context={}).apply()
    assert fortress_effect.duration == 0
    assert player2.affecting_trumps == ()


def test_remove_color(initiator, target):  # noqa: F811
    target.deck.remove_color_from_possible_colors = MagicMock()
    color = Color.RED
    trump = RemoveColor(color=color, duration=1)

    effect = trump.create_effect(initiator=initiator, target=target, context={})
    effect.apply()

    target.deck.remove_color_from_possible_colors.assert_called_once_with(color)


def test_remove_all_colors(initiator, target):  # noqa: F811
    target.deck.remove_color_from_possible_colors = MagicMock()
    trump = RemoveColor(color=Color["ALL"], duration=1)

    effect = trump.create_effect(initiator=initiator, target=target, context={})
    effect.apply()

    target.deck.remove_color_from_possible_colors.assert_called_once_with(Color["ALL"])


def test_remove_multiple_colors(initiator, target):
    target.deck.remove_color_from_possible_colors = MagicMock()
    colors = {Color.BLACK, Color.RED}
    trump = RemoveColor(colors=colors, duration=1)

    effect = trump.create_effect(initiator=initiator, target=target, context={})
    effect.apply()

    assert target.deck.remove_color_from_possible_colors.called
    assert target.deck.remove_color_from_possible_colors.call_count == len(colors)


def test_teleport_no_target_square(board, player):  # noqa: F811
    player.move = MagicMock()
    trump = Teleport(distance=1, color=Color.BLACK)

    trump.create_effect(
        initiator=player, target=player, context={"board": board, "square": None}
    ).apply()

    assert not player.move.called


def test_teleport_wrong_distance(board, player):  # noqa: F811
    player.move = MagicMock()
    trump = Teleport(distance=1, color=Color.BLACK)
    square = board[0, 0]

    trump.create_effect(
        initiator=player, target=player, context={"board": board, "square": square}
    ).apply()

    assert not player.move.called


def test_teleport_wrong_color(board, player):  # noqa: F811
    player.move = MagicMock()
    trump = Teleport(distance=1, color=Color.BLUE)
    square = board[0, 7]

    trump.create_effect(
        initiator=player, target=player, context={"board": board, "square": square}
    ).apply()

    assert not player.move.called


def test_teleport(board, player):  # noqa: F811
    player.move = MagicMock()
    square = board[6, 8]
    trump = Teleport(distance=1, color=square.color)

    trump.create_effect(
        initiator=player, target=player, context={"board": board, "square": square}
    ).apply()

    player.move.assert_called_once_with(square)


def test_player_can_only_be_affected_by_max_affecting_trumps_number_trump(
    target, initiator
):  # noqa: F811
    for i in range(target.MAX_NUMBER_AFFECTING_TRUMPS):
        trump = RemoveColor(colors=[Color["BLACK"]], duration=1)
        initiator.can_play = True
        initiator._number_trumps_played = 0
        initiator.play_trump(trump, target=target, context={})
        assert len(target.affecting_trumps) == i + 1

    trump = RemoveColor(colors=[Color["BLACK"]], duration=1)
    with pytest.raises(MaxNumberAffectingTrumpsError):
        initiator.can_play = True
        initiator._number_trumps_played = 0
        initiator.play_trump(trump, target=target, context={})
    assert len(target.affecting_trumps) == target.MAX_NUMBER_AFFECTING_TRUMPS


def test_cannot_be_affected_by_trump_empty_list_names(player, player2):  # noqa: F811
    trump = CannotBeAffectedByTrumps(trump_names=[])
    assert not trump.allow_trump_to_affect(None)

    trump = CannotBeAffectedByTrumps(trump_names=None)
    assert not trump.allow_trump_to_affect(None)
