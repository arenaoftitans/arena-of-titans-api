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
)
from unittest.mock import MagicMock


def test_new_game_no_game_id(api):
    api._game_id = None
    assert api._creating_new_game


def test_new_game_with_game_id(api):
    api._game_id = 'game_id'
    assert not api._creating_new_game


def test_new_game_request_on_old_connection(api):
    api._game_id = 'game_id'
    api._rt = 'INIT_GAME'
    api._message = {}
    assert api._creating_new_game


def test_onMessage_new_game(api):
    api._game_id = None
    api._create_new_game = MagicMock()
    api.sendMessage = MagicMock()

    api.onMessage(b'{}', False)

    api._create_new_game.assert_called_once_with()
    assert api.sendMessage.call_count == 1


def test_onMessage_creating_game(api):
    api._process_create_game_request = MagicMock()
    api._cache = MagicMock()
    api._cache.has_game_started = MagicMock(return_value=False)
    api._game_id = 'game_id'
    api.sendMessage = MagicMock()

    api.onMessage(b'{}', False)

    api._process_create_game_request.assert_called_once_with()
    assert api.sendMessage.call_count == 1


def test_create_new_game(api, mock):
    api_cache = MagicMock()
    mock.patch('aot.api.api.ApiCache', return_value=api_cache)
    api._get_initialiazed_game_message = MagicMock()
    api_cache.affect_next_slot = MagicMock(return_value=api.INDEX_FIRST_PLAYER)
    api._message = {
        'player_name': 'Game Master',
        'hero': 'daemon',
    }

    api._create_new_game()

    assert isinstance(api._game_id, str)
    assert len(api._game_id) == 22
    api_cache.create_new_game.assert_called_once_with(test=False)
    api_cache.affect_next_slot.assert_called_once_with(
        api._message['player_name'],
        api._message['hero'],
    )
    api_cache.save_session.assert_called_once_with(api.INDEX_FIRST_PLAYER)
    api._get_initialiazed_game_message.assert_called_once_with(api.INDEX_FIRST_PLAYER)
