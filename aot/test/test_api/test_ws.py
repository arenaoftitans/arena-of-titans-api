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

from aot.test import (
    api,
)
from unittest.mock import MagicMock


def test_onMessage_unkwon_request_type(api):
    api._send_error = MagicMock()

    try:
        api.onMessage(b'{}', False)
    except AotError as e:
        assert str(e) == 'unknown_request'
        api._send_error.assert_called_once_with('ttt')


def test_onMessage_new_game(api):
    api._game_id = None
    api._create_new_game = MagicMock()
    api.sendMessage = MagicMock()

    api.onMessage(b'{"rt": "INIT_GAME"}', False)

    api._create_new_game.assert_called_once_with()


def test_onMessage_creating_game(api):
    api._process_create_game_request = MagicMock()
    api._cache = MagicMock()
    api._cache.has_game_started = MagicMock(return_value=False)
    api._game_id = 'game_id'
    api.sendMessage = MagicMock()

    api.onMessage(b'{"rt": "INIT_GAME", "game_id": "game_id"}', False)

    api._process_create_game_request.assert_called_once_with()


def test_onMessage_process_play_request(api):
    api._process_play_request = MagicMock()
    api._cache = MagicMock()
    api._cache.has_game_started = MagicMock(return_value=True)
    api._game_id = 'game_id'

    api.onMessage(b'{"rt": "VIEW_POSSIBLE_SQUARES", "game_id": "game_id"}', False)

    api._process_play_request.assert_called_once_with()
