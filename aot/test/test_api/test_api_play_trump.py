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

import pytest

from aot.api.utils import (
    AotError,
    AotErrorToDisplay,
)
from aot.api.utils import RequestTypes
from aot.test import (
    api,
    game,
)
from unittest.mock import MagicMock


def test_play_trump_wrong_trump(api, game):
    with pytest.raises(AotError) as e:
        api._play_trump(game, {})

    assert 'wrong_trump' in str(e)


def test_play_trump_missing_target(api, game):
    for trump in game.active_player.trumps:
        if trump['must_target_player']:
            break

    with pytest.raises(AotError) as e:
        api._play_trump(game, {
            'name': trump['name'],
        })

    assert 'missing_trump_target' in str(e)


def test_play_trump_with_wrong_target(api, game):
    for trump in game.active_player.trumps:
        if trump['must_target_player']:
            break

    with pytest.raises(AotError) as e:
        api._play_trump(game, {
            'name': trump['name'],
            'target_index': 10,
        })

    assert 'wrong_trump_target' in str(e)


def test_play_trump_max_number_trumps_played(api, game):
    trump = game.active_player.trumps[0]
    trump['must_target_player'] = True
    game.active_player.play_trump = MagicMock(return_value=False)
    game.active_player._can_play = False

    with pytest.raises(AotError) as e:
        api._play_trump(game, {
            'name': trump['name'],
            'target_index': 0,
        })

    assert 'max_number_played_trumps' in str(e)


def test_play_trump_max_number_affecting_trumps(api, game):
    trump = game.active_player.trumps[0]
    trump['must_target_player'] = True
    game.active_player.play_trump = MagicMock(return_value=False)

    with pytest.raises(AotError) as e:
        api._play_trump(game, {
            'name': trump['name'],
            'target_index': 0,
        })

    assert 'max_number_trumps' in str(e)


def test_play_trump_with_target(api, game):
    for trump in game.active_player.trumps:
        if trump['must_target_player']:
            break
    api._send_all = MagicMock()
    game.add_action = MagicMock()

    api._play_trump(game, {
        'name': trump['name'],
        'target_index': 0,
    })

    assert api._send_all.call_count == 1
    assert game.add_action.call_count == 1


def test_play_trump_without_target(api, game):
    for trump in game.active_player.trumps:
        if not trump['must_target_player']:
            break
    api._send_all = MagicMock()
    game.add_action = MagicMock()

    api._play_trump(game, {
        'name': trump['name'],
    })

    assert api._send_all.call_count == 1
    assert game.add_action.call_count == 1
