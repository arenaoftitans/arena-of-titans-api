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

from unittest.mock import create_autospec, MagicMock

import pytest

from .. import (  # noqa: F401
    board,
    deck,
    game,
    player,
    player2,
)
from ...board import Color
from ...cards.trumps import (
    CannotBeAffectedByTrumps,
    ModifyCardColorsPower,
    ModifyCardNumberMovesPower,
    Power,
    SimpleTrump,
    StealPowerPower,
    Teleport,
    TrumpList,
)
from ...cards.trumps.constants import TargetTypes
from ...cards.trumps.exceptions import TrumpHasNoEffect


class VoidPower(Power):
    '''Sample power to be used in tests.

    It exists to tests common behavior to all power. We cannot instansiate Power directly
    because it is abstract.
    '''

    def affect(self, player):  # noqa: F811
        raise NotImplementedError


def test_create_normal_power():
    power = VoidPower(passive=False)

    assert not power.passive
    assert power.duration == 0


def test_create_passive_power():
    power = VoidPower(passive=True)

    assert power.passive
    assert power.duration is None


def test_enable():
    trump = MagicMock()
    trump.args = {'cost': 1}
    power = VoidPower(trump_cost_delta=5, passive=True)

    power.setup([trump])

    assert trump.args == {'cost': 6}


def test_modify_card_colors(player):  # noqa: F811
    player.modify_card_colors = MagicMock()
    power = ModifyCardColorsPower(add_colors=['BLACK'], passive=True)

    power.affect(player=player)

    assert power.passive
    assert power.duration is None
    assert len(power._colors) == 1
    player.modify_card_colors.assert_called_once_with({'BLACK'}, filter_=None)


def test_modify_number_moves(player):  # noqa: F811
    player.modify_card_number_moves = MagicMock()
    power = ModifyCardNumberMovesPower(delta_moves=5, passive=True)

    power.affect(player=player)

    assert power.passive
    assert power.duration is None
    assert power._delta_moves == 5
    player.modify_card_number_moves.assert_called_once_with(5, filter_=None)


def test_prevent_trump_action(player, player2, mocker):  # noqa: F811
    '''Test how PreventTrumpAction and CannotBeAffectedByTrumps works together.

    GIVEN: a first player with Impassible power which prevents towers to be destroyed.
    GIVEN: a second player with Force of Nature which automatically destroys towers
    WHEN: the first player plays a tower against the second player
    THEN: the result is random.
    '''
    # Setup player 1.
    impassable_power = SimpleTrump(
        type='PreventTrumpAction',
        name='Impassable',
        args={
            'prevent_for_trumps': ['Force of nature'],
            'enable_for_trumps': ['Tower'],
            'name': 'Impassable',
            'passive': True,
        },
    )
    player._available_trumps = TrumpList([
        SimpleTrump(
            type='RemoveColor',
            name='Tower',
            args={
                'cost': 1,
                'name': 'Tower',
            },
        ),
    ])
    player._setup_power(impassable_power)
    player._enable_passive_power()
    trump_to_play = player._available_trumps['Tower', None]
    player._can_play = True
    # We will play many trumps here and we don't care.
    player.MAX_NUMBER_TRUMPS_PLAYED = float('inf')

    # Setup player 2
    force_of_nature_power = SimpleTrump(
        type='CannotBeAffectedByTrumps',
        name='Force of nature',
        args={
            'name': 'Force of nature',
            'passive': True,
            'trump_names': ['Tower'],
        },
    )
    player2._setup_power(force_of_nature_power)

    # In this case, whether the trump has an effect or not is random.
    # We mock the choice function to make it stable.
    mocker.patch('aot.cards.trumps.trumps.random.choice', return_value=False)
    with pytest.raises(TrumpHasNoEffect):
        player.play_trump(trump_to_play, target=player2)

    mocker.patch('aot.cards.trumps.trumps.random.choice', return_value=True)
    # Must not raise.
    player.play_trump(trump_to_play, target=player2)


def test_cannot_be_selected_active_power(player, player2):  # noqa: F811
    '''Test that we can use an active power (or trump) to prevent any trump action.

    GIVEN: a first player with "Night mist" which prevents any trump to affect it.
    GIVEN: a second player with a trump.
    WHEN: the second player tries to play a trump against the first player.
    THEN: the trump has no effect.
    '''
    # Setup player 1.
    night_mist = CannotBeAffectedByTrumps(
        name='Night Mist',
        must_target_player=False,
        passive=False,
        trump_names=None,
    )
    player._can_play = True
    player.play_trump(night_mist, target=player)
    # We will play many trumps here and we don't care.
    player.MAX_NUMBER_TRUMPS_PLAYED = float('inf')

    # Setup player 2.
    a_trump = SimpleTrump(
        type='RemoveColor',
        name='Tower',
        args={
            'cost': 1,
            'must_target_player': True,
            'name': 'Tower',
        },
    )
    player2._available_trumps = TrumpList([a_trump])
    trump_to_play = player2._available_trumps['Tower', None]
    player2._can_play = True

    with pytest.raises(TrumpHasNoEffect):
        player2.play_trump(trump_to_play, target=player)

    # Player 1 can still play trumps on itself.
    player.play_trump(night_mist, target=player)


def test_cannot_be_selected_active_power_with_special_action(player, player2):  # noqa: F811
    '''Test that we can use an active power (or trump) to prevent any special action.

    GIVEN: a first player with "Night mist" which prevents any trump to affect it.
    GIVEN: a second player with a special action.
    WHEN: the second player tries to play the special action against the first player.
    THEN: the special action has no effect.
    '''
    # Setup player 1.
    night_mist = CannotBeAffectedByTrumps(
        name='Night Mist',
        must_target_player=False,
        passive=False,
        trump_names=None,
    )
    player._can_play = True
    player.play_trump(night_mist, target=player)

    # Setup player 2.
    action = Teleport(
        name='Teleport',
        must_target_player=True,
    )

    with pytest.raises(TrumpHasNoEffect):
        player2.play_special_action(action, target=player)


def test_steal_power_target_type_reflect_target_type_stolen_power(player):  # noqa: F811
    power = StealPowerPower(passive=True)
    stolen_power = VoidPower(passive=False, trump_names=())

    power.affect(power=stolen_power)

    assert power.target_type != TargetTypes.trump
    assert power.target_type == stolen_power.target_type


def test_steal_power_affect_forwards_to_stolen_power(player):  # noqa: F811
    power = StealPowerPower()
    stolen_power = create_autospec(VoidPower)

    # Set the power stolen power to stolen_power
    power.affect(power=stolen_power)
    assert stolen_power.affect.call_count == 0

    power.affect(player=player)
    stolen_power.affect.assert_called_with(player)


def test_steal_power_properties_no_stolen_power():
    power = StealPowerPower(
        color=Color.BLUE,
        cost=1,
        description='Steal power desc',
        duration=2,
        must_target_player=True,
        name='Steal power',
        passive=False,
    )

    assert power.color == Color.BLUE
    assert power.cost == 1
    assert power.description == 'Steal power desc'
    assert power.duration == 2
    assert power.must_target_player
    assert power.name == 'Steal power'
    assert power.initiator is None
    assert not power.passive
    assert power.target_type == TargetTypes.trump


def test_steal_power_properties_setters_no_stolen_power(player):  # noqa: F811
    power = StealPowerPower(
        color=Color.BLUE,
        cost=1,
        description='Steal power desc',
        duration=2,
        must_target_player=True,
        name='Steal power',
        passive=False,
    )

    power.cost = 10
    power.duration = 20
    power.initiator = player

    assert power.cost == 10
    assert power.duration == 20
    assert power.initiator is player


def test_steal_power_properties_with_stolen_power(player):  # noqa: F811
    power = StealPowerPower(
        color=Color.BLUE,
        cost=1,
        description='Steal power desc',
        duration=2,
        must_target_player=True,
        name='Steal power',
        passive=False,
    )
    stolen_power = VoidPower(
        color=Color.YELLOW,
        cost=10,
        description='Stolen power desc',
        must_target_player=False,
        name='Stolen power',
        passive=True,
    )

    power.affect(power=stolen_power)

    assert power.color == Color.YELLOW
    assert power.cost == power.STOLEN_POWER_COST
    assert power.description == 'Stolen power desc'
    assert power.duration is None  # Trump is passive thus duration is None
    assert not power.must_target_player
    assert power.name == 'Stolen power'
    assert power.initiator is None
    assert power.passive
    assert power.target_type == TargetTypes.player


def test_steal_power_properties_setters_with_stolen_power(player):  # noqa: F811
    power = StealPowerPower(
        color=Color.BLUE,
        cost=1,
        description='Steal power desc',
        duration=2,
        must_target_player=True,
        name='Steal power',
        passive=False,
    )
    stolen_power = VoidPower(
        color=Color.YELLOW,
        cost=10,
        description='Stolen power desc',
        must_target_player=False,
        name='Stolen power',
        passive=True,
    )

    power.affect(power=stolen_power)

    power.cost = 100
    power.duration = 200
    power.initiator = player

    assert power.cost == power.STOLEN_POWER_COST
    assert power.duration == 200
    assert power.initiator is player
    assert stolen_power.cost == 100
    assert stolen_power.duration == 200
    assert stolen_power.initiator is player


def test_return_proper_trump_played_infos_on_steal():
    power = StealPowerPower(
        color=Color.BLUE,
        cost=1,
        description='Steal power desc',
        duration=2,
        must_target_player=True,
        name='Steal power',
        passive=False,
    )
    stolen_power = VoidPower(
        color=Color.YELLOW,
        cost=10,
        description='Stolen power desc',
        must_target_player=False,
        name='Stolen power',
        passive=True,
    )

    infos = power.affect(power=stolen_power)

    assert infos.name == 'Steal power'
    assert infos.description == 'Steal power desc'
    assert infos.cost == 1


def test_return_proper_trump_played_infos_after_steal(player):  # noqa: F811
    power = StealPowerPower(
        color=Color.BLUE,
        cost=1,
        description='Steal power desc',
        duration=2,
        must_target_player=True,
        name='Steal power',
        passive=False,
    )
    stolen_power = ModifyCardColorsPower(
        color=Color.YELLOW,
        cost=10,
        description='Stolen power desc',
        must_target_player=False,
        name='Stolen power',
        passive=True,
    )

    power.affect(power=stolen_power)
    infos = power.affect(player=player)

    assert infos.name == stolen_power.name
    assert infos.description == stolen_power.description
    assert infos.cost == power.STOLEN_POWER_COST
