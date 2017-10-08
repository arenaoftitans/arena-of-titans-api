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

from .. import (  # noqa: F401
    board,
    deck,
    game,
    player,
)
from ...cards.trumps import (
    ModifyCardNumberMovesPower,
    Power,
)


def test_create_normal_power():
    power = Power(passive=False)

    assert not power.passive
    assert power.duration == 0


def test_create_passive_power():
    power = Power(passive=True)

    assert power.passive
    assert power.duration is None


def test_enable():
    trump = MagicMock()
    trump.args = {'cost': 1}
    power = Power(trump_cost_delta=5)

    power.setup([trump])

    assert trump.args == {'cost': 6}


def test_modify_number_moves(player):  # noqa: F811
    player.modify_card_number_moves = MagicMock()
    power = ModifyCardNumberMovesPower(delta_moves=5, passive=True)

    power.affect(player)

    assert power.passive
    assert power.duration is None
    assert power._delta_moves == 5
    player.modify_card_number_moves.assert_called_once_with(5, card_filter=None)
