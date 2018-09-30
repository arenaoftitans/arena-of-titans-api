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

from unittest.mock import MagicMock

import pytest

from .. import (  # noqa: F401
    board,
    deck,
    game,
    player,
    player2,
)
from ...cards.trumps import (
    CannotBeAffectedByTrumps,
    ModifyCardColorsPower,
    ModifyCardNumberMovesPower,
    Power,
    SimpleTrump,
    TrumpList,
)
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

    power.affect(player)

    assert power.passive
    assert power.duration is None
    assert len(power._colors) == 1
    player.modify_card_colors.assert_called_once_with({'BLACK'}, filter_=None)


def test_modify_number_moves(player):  # noqa: F811
    player.modify_card_number_moves = MagicMock()
    power = ModifyCardNumberMovesPower(delta_moves=5, passive=True)

    power.affect(player)

    assert power.passive
    assert power.duration is None
    assert power._delta_moves == 5
    player.modify_card_number_moves.assert_called_once_with(5, filter_=None)


def test_prevent_trump_action(player, player2, mock):  # noqa: F811
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
    mock.patch('aot.cards.trumps.trumps.random.choice', return_value=False)
    with pytest.raises(TrumpHasNoEffect):
        player.play_trump(trump_to_play, target=player2)

    mock.patch('aot.cards.trumps.trumps.random.choice', return_value=True)
    # Must not raise.
    player.play_trump(trump_to_play, target=player2)
