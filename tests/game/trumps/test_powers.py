################################################################################
# Copyright (C) 2015-2017 by Arena of Titans Contributors.
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

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from aot.game.board import Color
from aot.game.trumps import (
    CannotBeAffectedByTrumpsPower,
    ModifyCardColors,
    ModifyCardColorsPower,
    ModifyCardNumberMovesPower,
    Power,
    PreventTrumpActionPower,
    RemoveColor,
    StealPowerPower,
    Teleport,
    TrumpsList,
)
from aot.game.trumps.exceptions import TrumpHasNoEffectError
from tests.factories import PlayerFactory
from tests.utilities import AnyFunction


@pytest.fixture()
def initiator(player):
    return player


@pytest.fixture()
def target(player2):
    return player2


@pytest.fixture()
def steal_power_power():
    return StealPowerPower(
        trump_args={
            "color": Color.BLUE,
            "cost": 1,
            "description": "Steal power desc",
            "duration": 2,
            "must_target_player": True,
            "name": "Steal power",
        },
        passive=False,
    )


@pytest.fixture()
def passive_stolen_power():
    return ModifyCardColorsPower(
        trump_args={
            "color": Color.YELLOW,
            "cost": 10,
            "description": "Stolen power desc",
            "must_target_player": False,
            "name": "Stolen power",
        },
        trump_cost_delta=2,
        passive=True,
    )


@pytest.fixture()
def red_tower_trump():
    return RemoveColor(name="Tower", color=Color.RED, cost=4, duration=1, must_target_player=True)


@dataclass(frozen=True)
class VoidPower(Power):
    """Sample power to be used in tests.

    It exists to tests common behavior to all power. We cannot instantiate Power directly
    because it is abstract.
    """

    trump_cls: type = ModifyCardColors

    def affect(self, player):  # noqa: F811
        raise NotImplementedError


def test_create_active_power():
    power = VoidPower(passive=False)

    assert not power.passive
    assert power.duration == 0
    assert power.trump.duration == 0


def test_create_passive_power():
    power = VoidPower(passive=True)

    assert power.passive
    assert power.duration == float("inf")
    assert power.trump.duration == float("inf")


def test_enable(red_tower_trump):
    power = VoidPower(trump_cost_delta=5, passive=True)

    available_trumps = power.setup([red_tower_trump])

    assert len(available_trumps) == 1
    assert available_trumps[0].cost == red_tower_trump.cost + 5


def test_modify_card_colors(player):  # noqa: F811
    player.modify_card_colors = MagicMock()
    power = ModifyCardColorsPower(trump_args={"colors": {"BLACK"}}, passive=True)

    power.create_effect(initiator=player, target=player, context={}).apply()

    assert power.passive
    player.modify_card_colors.assert_called_once_with({"BLACK"}, filter_=AnyFunction())


def test_modify_number_moves(player):  # noqa: F811
    player.modify_card_number_moves = MagicMock()
    power = ModifyCardNumberMovesPower(trump_args={"delta_moves": 5}, passive=True)

    power.create_effect(initiator=player, target=player, context={}).apply()

    assert power.passive
    assert power.trump.delta_moves == 5
    player.modify_card_number_moves.assert_called_once_with(5, filter_=AnyFunction())


def test_prevent_trump_action(mocker, red_tower_trump):  # noqa: F811
    """Test how PreventTrumpAction and CannotBeAffectedByTrumps works together.

    GIVEN: a first player with Impassible power which prevents towers to be destroyed.
    GIVEN: a second player with Force of Nature which automatically destroys towers
    WHEN: the first player plays a tower against the second player
    THEN: the result is random.
    """
    # Setup player 1.
    impassable_power = PreventTrumpActionPower(
        trump_args={
            "prevent_trumps_to_modify": ["Force of nature"],
            "enable_for_trumps": ["Tower"],
            "name": "Impassable",
        },
        passive=True,
    )
    player = PlayerFactory(
        power=impassable_power, trumps=TrumpsList([red_tower_trump]), gauge__value=40,
    )
    player.init_turn()
    trump_to_play = player._available_trumps["Tower", Color.RED]
    player._can_play = True
    # We will play many trumps here and we don't care.
    player.MAX_NUMBER_TRUMPS_PLAYED = float("inf")

    # Setup player 2
    force_of_nature_power = CannotBeAffectedByTrumpsPower(
        passive=True, trump_args={"name": "Force of nature", "trump_names": ["Tower"]},
    )
    player2 = PlayerFactory(power=force_of_nature_power)

    # In this case, whether the trump has an effect or not is random.
    # We mock the choice function to make it stable.
    mocker.patch("aot.game.trumps.trumps.random.choice", return_value=False)
    with pytest.raises(TrumpHasNoEffectError):
        player.play_trump(trump_to_play, target=player2, context={})

    mocker.patch("aot.game.trumps.trumps.random.choice", return_value=True)
    # Must not raise.
    player.play_trump(trump_to_play, target=player2, context={})


def test_cannot_be_selected_active_power(player, player2, red_tower_trump):  # noqa: F811
    """Test that we can use an active power (or trump) to prevent any trump action.

    GIVEN: a first player with "Night mist" which prevents any trump to affect it.
    GIVEN: a second player with a trump.
    WHEN: the second player tries to play a trump against the first player.
    THEN: the trump has no effect.
    """
    # Setup player 1.
    night_mist = CannotBeAffectedByTrumpsPower(
        trump_args={"name": "Night Mist", "must_target_player": False, "trump_names": ()},
        passive=False,
    )
    player._can_play = True
    player.play_trump(night_mist, target=player, context={})
    # We will play many trumps here and we don't care.
    player.MAX_NUMBER_TRUMPS_PLAYED = float("inf")

    # Setup player 2.
    player2._available_trumps = TrumpsList([red_tower_trump])
    trump_to_play = player2._available_trumps["Tower", Color.RED]
    player2._can_play = True

    with pytest.raises(TrumpHasNoEffectError):
        player2.play_trump(trump_to_play, target=player, context={})

    # Player 1 can still play trumps on itself.
    player.play_trump(night_mist, target=player, context={})


def test_cannot_be_selected_active_power_with_special_action(player, player2):  # noqa: F811
    """Test that we can use an active power (or trump) to prevent any special action.

    GIVEN: a first player with "Night mist" which prevents any trump to affect it.
    GIVEN: a second player with a special action.
    WHEN: the second player tries to play the special action against the first player.
    THEN: the special action has no effect.
    """
    # Setup player 1.
    night_mist = CannotBeAffectedByTrumpsPower(
        passive=False,
        trump_args={"name": "Night Mist", "must_target_player": False, "trump_names": ()},
    )
    player._can_play = True
    player.play_trump(night_mist, target=player, context={})

    # Setup player 2.
    action = Teleport(name="Teleport", must_target_player=True, color=Color.BLACK)

    with pytest.raises(TrumpHasNoEffectError):
        player2.play_special_action(action, target=player, context={})


def test_steal_power_target_type_reflect_target_type_stolen_power(target, initiator):  # noqa: F811
    power = StealPowerPower(passive=True, trump_args={"name": "Steal"})
    stolen_power = VoidPower(passive=False, trump_args={"name": "Stolen power"})
    initiator.init_turn()
    target._power = stolen_power
    initiator._available_trumps = power.setup(initiator._available_trumps)
    target._available_trumps = stolen_power.setup(target.available_trumps)

    initiator.play_trump(power, target=target, context={"stolen_power": stolen_power})

    assert len(initiator.trump_effects) == 1
    assert initiator.trump_effects[0].name == "Steal"
    assert initiator.power == target.power
    assert initiator.power.name == "Stolen power"


def test_steal_power_properties_no_stolen_power(steal_power_power):
    assert steal_power_power.cost == 1
    assert steal_power_power.trump.description == "Steal power desc"
    assert steal_power_power.duration == 3
    assert steal_power_power.trump.duration == 3
    assert steal_power_power.trump.must_target_player
    assert steal_power_power.name == "Steal power"
    assert steal_power_power.trump.name == "Steal power"


def test_immediately_apply_passive_power(
    initiator, target, steal_power_power, passive_stolen_power
):  # noqa: F811
    target._power = passive_stolen_power

    initiator.init_turn()
    initial_trump_cost = initiator.available_trumps[0].cost

    initiator.play_trump(
        steal_power_power, target=target, context={"stolen_power": passive_stolen_power}
    )

    assert len(initiator.trump_effects) == 2
    assert initiator.trump_effects[0].name == "Stolen power"
    assert initiator.trump_effects[1].name == "Steal power"
    assert initiator.available_trumps[0].cost == initial_trump_cost + 2
