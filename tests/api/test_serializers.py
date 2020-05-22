#
#  Copyright (C) 2015-2020 by Arena of Titans Contributors.
#
#  This file is part of Arena of Titans.
#
#  Arena of Titans is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Arena of Titans is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
#

import json

import pytest

from aot.api.serializers import to_json
from aot.game.actions import Action


def _get_special_action_from_game(game):
    for card in game.active_player.deck:
        if card.special_actions:
            return card.special_actions[0]


@pytest.mark.parametrize(
    "action_builder",
    [
        pytest.param(
            lambda game: Action(
                initiator=game.active_player,
                target=game.active_player,
                description="played_trump",
                trump=game.active_player.available_trumps[0],
            ),
            id="trump_played",
        ),
        pytest.param(
            lambda game: Action(
                initiator=game.active_player,
                target=game.active_player,
                description="played_trump",
                trump=game.active_player.power,
            ),
            id="power_played",
        ),
        pytest.param(
            lambda game: Action(
                initiator=game.active_player,
                target=game.active_player,
                description="played_trump",
                special_action=_get_special_action_from_game(game),
            ),
            id="special_action",
        ),
    ],
)
def test_serialize_actions(game, snapshot, action_builder):
    action = action_builder(game)

    data = json.loads(json.dumps(action, default=to_json))

    snapshot.assert_match(data)
