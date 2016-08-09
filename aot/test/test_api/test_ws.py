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

from aot.api.utils import RequestTypes
from aot.test import (
    api,
    game,
)
from unittest.mock import MagicMock


def test_onClose(api, game):
    api._cache = MagicMock()
    api._cache.get_game = MagicMock(return_value=game)
    api._clients[0] = None
    api._send_play_message = MagicMock()
    api._save_game = MagicMock()
    api._loop = MagicMock()

    player = game.active_player
    game.pass_turn = MagicMock()
    game.disconnect = MagicMock(return_value=player)

    api.onClose(True, 1001, None)

    assert 0 not in api._clients

    api._loop.call_later.assert_called_once_with(
        api.DISCONNECTED_TIMEOUT_WAIT,
        api._disconnect_player
    )
    api._disconnect_player()

    api._cache.get_game.assert_called_once_with()
    api._send_play_message.assert_called_once_with(game, player)
    api._save_game.assert_called_once_with(game)

    game.disconnect.assert_called_once_with(player.id)
    game.pass_turn.assert_called_once_with()


def test_onClose_creating_game(api, game):
    api._cache = MagicMock()
    slots = [
        {
            'index': 0,
            'player_id': 0,
        },
        {
            'index': 1,
            'player_id': 1,
        },
    ]
    api._cache.get_slots = MagicMock(return_value=slots)
    api._cache.has_game_started = MagicMock(return_value=False)
    api._modify_slots = MagicMock()
    api._clients[0] = None
    api._loop = MagicMock()

    api.onClose(True, 1001, None)

    assert 0 not in api._clients

    api._loop.call_later.assert_called_once_with(
        api.DISCONNECTED_TIMEOUT_WAIT,
        api._disconnect_player
    )
    api._disconnect_player()

    assert api._message == {
        'rt': RequestTypes.SLOT_UPDATED,
        'slot': {
            'index': 0,
            'state': 'OPEN',
        },
    }
    api._modify_slots.assert_called_once_with()


def test_reconnect_creating_game(api, game):
    timer = MagicMock()
    api._cache = MagicMock()
    api._cache.has_game_started = MagicMock(return_value=False)
    api._cache.get_player_index = MagicMock(return_value=0)
    api._reconnect_to_game = MagicMock()
    api._get_initialiazed_game_message = MagicMock()
    api._game_id = 'game-id'
    api._message = {
        'player_id': 'player_id',
        'game_id': 'game_id',
    }
    api._disconnect_timeouts['player_id'] = timer
    api.sendMessage = MagicMock()

    api._reconnect()

    timer.cancel.assert_called_once_with()
    api._get_initialiazed_game_message.assert_called_once_with(0)
    api._cache.init.assert_called_once_with(game_id='game_id', player_id='player_id')
    assert api.id == 'player_id'
    assert api._game_id == 'game_id'
    assert api.sendMessage.call_count == 1


def test_reconnect_creating_game_slot_freed(api, game):
    timer = MagicMock()
    api._cache = MagicMock()
    api._cache.has_game_started = MagicMock(return_value=False)
    api._cache.get_player_index = MagicMock(side_effect=IndexError)
    api._reconnect_to_game = MagicMock()
    api._get_initialiazed_game_message = MagicMock()
    api._game_id = 'game-id'
    api._message = {
        'player_id': 'player_id',
        'game_id': 'game_id',
    }
    api._disconnect_timeouts['player_id'] = timer
    api.sendMessage = MagicMock()

    api._reconnect()

    timer.cancel.assert_called_once_with()
    api._get_initialiazed_game_message.assert_called_once_with(-1)
    assert api._game_id is None
    assert api.sendMessage.call_count == 1


def test_reconnect_reconnect_to_game(api, game):
    timer = MagicMock()
    api._cache = MagicMock()
    api._cache.has_game_started = MagicMock(return_value=True)
    api._cache.get_game = MagicMock(return_value=game)
    api._reconnect_to_game = MagicMock()
    api._message = {
        'player_id': 'player_id',
        'game_id': 'game_id',
    }
    api._disconnect_timeouts['player_id'] = timer
    api.sendMessage = MagicMock()

    api._reconnect()

    timer.cancel.assert_called_once_with()
    api._reconnect_to_game.assert_called_once_with(game)
    api._cache.init.assert_called_once_with(game_id='game_id', player_id='player_id')
    assert api.id == 'player_id'
    assert api._game_id == 'game_id'
    assert api.sendMessage.call_count == 1


def test_reconnect_to_game(api, game):
    game.active_player._id = 'player_id'
    game.active_player.is_connected = False
    api.id = 'player_id'
    api._get_action_message = MagicMock()

    api._reconnect_to_game(game)

    assert game.active_player.is_connected
    api._get_action_message.assert_called_once_with(None)
