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

import pytest

from aot.api.utils import RequestTypes
from aot.test import (
    api,
    game,
)
from unittest.mock import MagicMock


class ApiCacheStub:
    def __init__(self, *args, **kwargs):
        pass


@pytest.fixture(autouse=True)
def set_magic_mocks_on_api_cache():
    ApiCacheStub.create_new_game = MagicMock()
    ApiCacheStub.affect_next_slot = MagicMock()
    ApiCacheStub.save_session = MagicMock()
    ApiCacheStub.is_game_master = MagicMock()
    ApiCacheStub.get_slots = MagicMock()


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
    api._send_play_message.assert_called_once_with(player, game)
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
    api._creating_game = MagicMock(return_value=True)
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

    assert api.message == {
        'rt': RequestTypes.SLOT_UPDATED,
        'slot': {
            'index': 0,
            'state': 'OPEN',
        },
    }
    api._modify_slots.assert_called_once_with(RequestTypes.SLOT_UPDATED)


def test_reconnect_creating_game(api, game):
    timer = MagicMock()
    api._creating_game = MagicMock(return_value=True)
    api._reconnect_to_game = MagicMock()
    api._get_initialiazed_game_message = MagicMock()
    api._game_id = 'game-id'
    api.message = {
        'player_id': 0,
    }
    api._disconnect_timeouts[0] = timer
    api._reconnect()

    timer.cancel.assert_called_once_with()
    api._get_initialiazed_game_message.assert_called_once_with(-1)


def test_reconnect_to_game(api, game):
    timer = MagicMock()
    api._creating_game = MagicMock(return_value=False)
    api._reconnect_to_game = MagicMock()
    api._game_id = 'game-id'
    api.message = {
        'player_id': 0,
    }
    api._disconnect_timeouts[0] = timer
    api._reconnect()

    timer.cancel.assert_called_once_with()
    api._reconnect_to_game.assert_called_once_with(None)


def test_initialize_connection_new_game(api, game, mock):
    mock.patch('aot.api.api.ApiCache', side_effect=ApiCacheStub)
    api.message = {
        'rt': 'INIT_GAME',
    }
    api.sendMessage = MagicMock()
    api._can_join = MagicMock(return_value=True)
    api._is_reconnecting = MagicMock(return_value=False)

    api._initialize_connection()

    assert api._game_id
    assert api.sendMessage.call_count == 1
    assert ApiCacheStub.create_new_game.call_count == 1
