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

from ... import get_game
from ...api.utils import (
    AotError,
    AotErrorToDisplay,
    RequestTypes,
)
from ...test import (  # noqa: F401
    AsyncMagicMock,
    api,
    game,
)


@pytest.mark.asyncio  # noqa: F811
async def test_test_success(api):
    api._cache = MagicMock()
    api._cache.test = AsyncMagicMock()
    api.sendMessage = MagicMock()

    await api.onMessage(b'{"rt": "test"}', False)

    api._cache.test.assert_called_once_with()
    api.sendMessage.assert_called_once_with({
        'success': True,
    })


@pytest.mark.asyncio  # noqa: F811
async def test_test_failure(api):
    def cache_test():
        raise Exception('Error in redis')

    api._cache = MagicMock()
    api._cache.test = MagicMock(side_effect=cache_test)
    api.sendMessage = MagicMock()

    await api.onMessage(b'{"rt": "test"}', False)

    api._cache.test.assert_called_once_with()
    api.sendMessage.assert_called_once_with({
        'success': False,
        'errors': 'Error in redis',
    })


@pytest.mark.asyncio  # noqa: F811
async def test_info(api):
    api._clients = {
        'client',
        'info_request',
    }
    api._cache = MagicMock()
    api._cache.info = AsyncMagicMock(return_value={'success': True})
    api.sendMessage = MagicMock()

    await api.onMessage(b'{"rt": "info"}', False)

    api._cache.info.assert_called_once_with()
    api.sendMessage.assert_called_once_with({
        'success': True,
        'number_connected_players': 1,
    })


@pytest.mark.asyncio  # noqa: F811
async def test_onMessage_unkwon_request_type(api):
    api.sendMessage = AsyncMagicMock()

    await api.onMessage(b'{}', False)

    api.sendMessage.assert_called_once_with({
        'error': 'Unknown request: .',
        'extra_data': {'rt': ''},
        'is_fatal': False,
    })


@pytest.mark.asyncio  # noqa: F811
async def test_onMessage_reconnect(api):
    api._reconnect = AsyncMagicMock()
    api._cache = MagicMock()
    api._cache.is_member_game = AsyncMagicMock(return_value=True)

    await api.onMessage(
        b'{"rt": "INIT_GAME", "player_id": "player_id", "game_id": "game_id"}',
        False,
    )

    api._cache.is_member_game.assert_called_once_with('game_id', 'player_id')
    api._reconnect.assert_called_once_with()


@pytest.mark.asyncio  # noqa: F811
async def test_onMessage_reconnect_cannot_join(api):
    api._reconnect = AsyncMagicMock()
    api._cache = MagicMock()
    api._cache.is_member_game = AsyncMagicMock(return_value=False)
    api.sendMessage = AsyncMagicMock()

    await api.onMessage(
        b'{"rt": "INIT_GAME", "player_id": "player_id", "game_id": "game_id"}',
        False,
    )

    api._cache.is_member_game.assert_called_once_with('game_id', 'player_id')
    assert api._reconnect.call_count == 0
    api.sendMessage.assert_called_once_with({
        'error_to_display': 'You cannot join this game. No slots opened.',
        'is_fatal': False,
    })


@pytest.mark.asyncio  # noqa: F811
async def test_onMessage_reconnect_while_already_connected(api):
    api._reconnect = AsyncMagicMock()
    api._cache = MagicMock()
    api.sendMessage = AsyncMagicMock()
    api._clients['player_id'] = MagicMock()

    await api.onMessage(
        b'{"rt": "INIT_GAME", "player_id": "player_id", "game_id": "game_id"}',
        False,
    )

    assert api._reconnect.call_count == 0
    api.sendMessage.assert_called_once_with({
        'error_to_display': 'errors.player_already_connected',
        'is_fatal': True,
    })


@pytest.mark.asyncio  # noqa: F811
async def test_onMessage_new_game(api):
    api._game_id = None
    api._create_new_game = MagicMock()
    api.sendMessage = MagicMock()

    await api.onMessage(b'{"rt": "INIT_GAME"}', False)

    api._create_new_game.assert_called_once_with()


@pytest.mark.asyncio  # noqa: F811
async def test_onMessage_creating_game(api):
    api._process_create_game_request = MagicMock()
    api._cache = MagicMock()
    api._cache.has_game_started = AsyncMagicMock(return_value=False)
    api._game_id = 'game_id'
    api.sendMessage = MagicMock()

    await api.onMessage(b'{"rt": "INIT_GAME", "game_id": "game_id"}', False)

    api._process_create_game_request.assert_called_once_with()


@pytest.mark.asyncio  # noqa: F811
async def test_onMessage_process_play_request(api):
    api._process_play_request = MagicMock()
    api._cache = MagicMock()
    api._cache.has_game_started = AsyncMagicMock(return_value=True)
    api._game_id = 'game_id'

    await api.onMessage(b'{"rt": "VIEW_POSSIBLE_SQUARES", "game_id": "game_id"}', False)

    api._process_play_request.assert_called_once_with()


def test_new_game_no_game_id(api):  # noqa: F811
    api._game_id = None
    assert api._creating_new_game


def test_new_game_with_game_id(api):  # noqa: F811
    api._game_id = 'game_id'
    assert not api._creating_new_game


def test_new_game_request_on_old_connection(api):  # noqa: F811
    api._game_id = 'game_id'
    api._rt = 'INIT_GAME'
    api._message = {}
    assert api._creating_new_game


@pytest.mark.asyncio  # noqa: F811
async def test_create_new_game(api, mock):
    api._cache = MagicMock()
    api._cache.create_new_game = AsyncMagicMock()
    api._cache.save_session = AsyncMagicMock()
    api._get_initialiazed_game_message = AsyncMagicMock()
    api._cache.affect_next_slot = AsyncMagicMock(return_value=api.INDEX_FIRST_PLAYER)
    api._message = {
        'player_name': 'Game Master',
        'hero': 'daemon',
    }
    api.sendMessage = AsyncMagicMock()

    await api._create_new_game()

    assert isinstance(api._game_id, str)
    assert len(api._game_id) == 22
    api._cache.create_new_game.assert_called_once_with(test=False)
    api._cache.affect_next_slot.assert_called_once_with(
        api._message['player_name'],
        api._message['hero'],
    )
    api._cache.save_session.assert_called_once_with(api.INDEX_FIRST_PLAYER)
    api._get_initialiazed_game_message.assert_called_once_with(api.INDEX_FIRST_PLAYER)
    assert api.sendMessage.call_count == 1


@pytest.mark.asyncio  # noqa: F811
async def test_process_create_game_request_not_allowed(api):
    api._cache = MagicMock()
    api._cache.is_game_master = AsyncMagicMock(return_value=False)
    api._rt = RequestTypes.CREATE_GAME

    with pytest.raises(AotErrorToDisplay) as e:
        await api._process_create_game_request()

    assert 'game_master_request' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_process_create_game_request_update_slot_not_game_master(api):
    api._cache = MagicMock()
    api._cache.is_game_master = AsyncMagicMock(return_value=False)
    api._rt = RequestTypes.SLOT_UPDATED
    api._modify_slots = AsyncMagicMock()

    await api._process_create_game_request()

    api._modify_slots.assert_called_once_with()


@pytest.mark.asyncio  # noqa: F811
async def test_process_create_game_request_update_slot_game_master(api):
    api._cache = MagicMock()
    api._cache.is_game_master = AsyncMagicMock(return_value=True)
    api._rt = RequestTypes.SLOT_UPDATED
    api._modify_slots = AsyncMagicMock()

    await api._process_create_game_request()

    api._modify_slots.assert_called_once_with()


@pytest.mark.asyncio  # noqa: F811
async def test_process_create_game_request_join_cannot_join(api):
    api._rt = RequestTypes.INIT_GAME
    api._cache = MagicMock()
    api._cache.game_exists = AsyncMagicMock(return_value=False)
    api._cache.is_game_master = AsyncMagicMock(return_value=False)

    with pytest.raises(AotError) as e:
        await api._process_create_game_request()

    assert 'cannot_join' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_process_create_game_request_join(api):
    api._rt = RequestTypes.INIT_GAME
    api._cache = MagicMock()
    api._cache.game_exists = AsyncMagicMock(return_value=True)
    api._cache.has_opened_slots = AsyncMagicMock(return_value=True)
    api._cache.is_game_master = AsyncMagicMock(return_value=False)
    api._join = AsyncMagicMock()

    await api._process_create_game_request()

    api._join.assert_called_once_with()


@pytest.mark.asyncio  # noqa: F811
async def test_process_create_game_request_create_game(api):
    api._cache = MagicMock()
    api._cache.is_game_master = AsyncMagicMock(return_value=True)
    api._rt = RequestTypes.CREATE_GAME
    api._create_game = AsyncMagicMock()

    await api._process_create_game_request()

    api._create_game.assert_called_once_with()


@pytest.mark.asyncio  # noqa: F811
async def test_join(api):
    game_message = {
        'slots': [
            None,
            {
                'state': 'TAKEN',
            },
        ],
    }
    api._get_initialiazed_game_message = AsyncMagicMock(return_value=game_message)
    api.sendMessage = AsyncMagicMock()
    api._send_all_others = AsyncMagicMock()
    api._cache = MagicMock()
    api._cache.affect_next_slot = AsyncMagicMock(return_value=1)
    api._cache.save_session = AsyncMagicMock()
    api.id = 'player_id'
    api._game_id = 'game_id'
    api._message = {
        'hero': 'daemon',
        'player_name': 'Player 2',
    }

    await api._join()

    api._cache.init.assert_called_once_with(game_id='game_id', player_id='player_id')
    assert api._cache.create_new_game.call_count == 0
    api._cache.affect_next_slot.assert_called_once_with('Player 2', 'daemon')
    api._cache.save_session.assert_called_once_with(1)
    api._get_initialiazed_game_message.assert_called_once_with(1)
    api.sendMessage.assert_called_once_with(game_message)
    api._send_all_others.assert_called_once_with({
        'rt': RequestTypes.SLOT_UPDATED,
        'slot': game_message['slots'][1],
    })


@pytest.mark.asyncio  # noqa: F811
async def test_modify_slots_empty_request(api):
    api._message = {}

    with pytest.raises(AotErrorToDisplay) as e:
        await api._modify_slots()

    assert 'no_slot' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_modify_slots_inexistant_slot(api):
    api._message = {
        'slot': {},
    }
    api._cache = MagicMock()
    api._cache.slot_exists = AsyncMagicMock(return_value=False)

    with pytest.raises(AotError) as e:
        await api._modify_slots()

    assert 'inexistant_slot' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_modify_slots(api):
    api._send_all = AsyncMagicMock()
    api._cache = MagicMock()
    api._cache.slot_exists = AsyncMagicMock(return_value=True)
    api._cache.update_slot = AsyncMagicMock()
    slot = {
        'player_id': 'player_id',
    }
    api._message = {
        'slot': slot,
    }

    await api._modify_slots()

    api._cache.update_slot.assert_called_once_with(slot)
    assert api._send_all.call_count == 1


@pytest.mark.asyncio  # noqa: F811
async def test_create_game_no_create_game_request(api):
    api._cache = MagicMock()
    api._cache.number_taken_slots = AsyncMagicMock(return_value=2)
    api._message = {
    }

    with pytest.raises(AotError) as e:
        await api._create_game()

    assert 'no_request' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_create_game_too_many_players(api):
    api._cache = MagicMock()
    api._cache.number_taken_slots = AsyncMagicMock(return_value=9)
    api._message = {
        'create_game_request': [{'name': i} for i in range(9)],
    }

    with pytest.raises(AotError) as e:
        await api._create_game()

    assert 'registered_different_description' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_create_game_too_few_players(api):
    api._cache = MagicMock()
    api._cache.number_taken_slots = AsyncMagicMock(return_value=1)
    api._message = {
        'create_game_request': [{'name': 0}],
    }

    with pytest.raises(AotError) as e:
        await api._create_game()

    assert 'registered_different_description' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_create_game_wrong_registration(api):
    api._cache = MagicMock()
    api._cache.number_taken_slots = AsyncMagicMock(return_value=2)
    api._message = {
        'create_game_request': [],
    }

    with pytest.raises(AotError) as e:
        await api._create_game()

    assert 'registered_different_description' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_create_game(mock, api):
    create_game_request = [
        {
            'name': str(i),
            'index': i,
            'id': str(i),
            'hero': 'Ulya',
        } for i in range(3)
    ]
    slots = [
        {'state': None},
        None,
        {'state': None},
    ]
    create_game_request[1] = None

    game = get_game(create_game_request)  # noqa: 811
    mock.patch('aot.api.api.get_game', return_value=game)
    api._cache = MagicMock()
    api._send_to = AsyncMagicMock()
    api._send_game_created_message = AsyncMagicMock()
    api._cache.number_taken_slots = AsyncMagicMock(return_value=2)
    api._cache.get_slots = AsyncMagicMock(return_value=slots)
    api._cache.is_test = AsyncMagicMock(return_value=False)
    api._cache.save_game = AsyncMagicMock()
    api._cache.game_has_started = AsyncMagicMock(return_value=False)
    api._message = {
        'create_game_request': create_game_request,
    }
    api._clients['0'] = None

    await api._create_game()

    api._cache.save_game.assert_called_once_with(game)
    api._send_game_created_message.assert_called_once_with(game)
    api._send_to.call_count == 2
    assert game.players[0].is_connected
    assert game.players[1] is None
    assert not game.players[2].is_connected


def test_disconnect_pending_players(api, game):  # noqa: F811
    api._clients_pending_disconnection = {
        'game_id': [0, 1],
    }
    api._game_id = 'game_id'
    game.players[0].is_connected = True
    game.players[1].is_connected = True

    api._disconnect_pending_players(game)

    assert len(api._clients_pending_disconnection) == 1
    assert len(api._clients_pending_disconnection['game_id']) == 0
    assert not game.players[0].is_connected
    assert not game.players[1].is_connected


def test_reconnect_pending_players(api, game):  # noqa: F811
    api._clients_pending_reconnection = {
        'game_id': [0, 1],
    }
    api._game_id = 'game_id'
    game.players[0].is_connected = False
    game.players[1].is_connected = False

    api._reconnect_pending_players(game)

    assert len(api._clients_pending_reconnection) == 1
    assert len(api._clients_pending_reconnection['game_id']) == 0
    assert game.players[0].is_connected
    assert game.players[1].is_connected


@pytest.mark.asyncio  # noqa: F811
async def test_notify_special_actions(api, game):
    api.sendMessage = AsyncMagicMock()

    await api._notify_special_action('action')

    api.sendMessage.assert_called_once_with({
        'rt': RequestTypes.SPECIAL_ACTION_NOTIFY,
        'special_action_name': 'action',
    })
