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

import asyncio
import json
import logging
import sys
from os import path
from unittest.mock import AsyncMock

import daiquiri
import pytest

from aot.api.cache import Cache
from aot.api.ws import AotWs
from aot.config import config


def mocked_choices(a_list, weights=None, k=None):
    k = k or len(a_list)
    return a_list[:k]


def mocked_sample_reversed(a_list: list, k: int):
    new_list = a_list.copy()
    new_list.reverse()
    return new_list


@pytest.fixture(scope="module")
def event_loop():
    """Change the scope of the fixture so all tests use the same loop."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


class TestCreateGame:
    game_master_id = "test-game-master-id"
    player_id = "player_id"
    game_id = "test-game-id"

    @classmethod
    def setup_class(cls):
        daiquiri.setup(level=logging.DEBUG)

        cls.game_master_ws = AotWs()
        cls.game_master_ws._wskey = cls.game_master_id
        cls.game_master_ws.sendMessage = AsyncMock()

        cls.player_ws = AotWs()
        cls.player_ws._wskey = cls.player_id
        cls.player_ws.sendMessage = AsyncMock()

        config.setup_config()

    @pytest.fixture(scope="function", autouse=True)
    def reset_send_message_calls(self, event_loop):
        self.game_master_ws.set_event_loop_for_testing(event_loop)
        self.player_ws.set_event_loop_for_testing(event_loop)

        self.game_master_ws.sendMessage.reset_mock()
        self.player_ws.sendMessage.reset_mock()

    def _get_message(self, message_path):
        root = path.dirname(__file__)
        messages_folder = "lobby_messages"
        path_to_open = path.join(root, messages_folder, message_path)

        with open(path_to_open, "rb") as message_file:
            return message_file.read()

    def _assert_calls_for_send_message(self, send_message_mock, snapshot, nb_calls, receiver):
        assert len(send_message_mock.mock_calls) == nb_calls
        for index, response_call in enumerate(send_message_mock.mock_calls):
            assert len(response_call.args) == 1
            assert response_call.kwargs == {}
            response = json.loads(response_call.args[0])
            snapshot.assert_match(response, f"{receiver}-{index}")

    @pytest.mark.integration
    @pytest.mark.dependency()
    @pytest.mark.asyncio
    async def test_create_lobby(self, mocker, snapshot):
        await Cache.clean_for_game(self.game_id)
        mocker.patch.object(
            sys.modules["aot.api.views.create_game"], "_create_game_id", return_value=self.game_id,
        )
        await self.game_master_ws.onOpen()

        await self.game_master_ws.onMessage(self._get_message("create_lobby.json"), is_binary=False)

        self._assert_calls_for_send_message(
            self.game_master_ws.sendMessage, snapshot, nb_calls=2, receiver="game_master"
        )

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_create_lobby"])
    @pytest.mark.asyncio
    async def test_join_game(self, snapshot):
        await self.player_ws.onOpen()

        await self.player_ws.onMessage(self._get_message("join_game.json"), is_binary=False)

        self._assert_calls_for_send_message(
            self.player_ws.sendMessage, snapshot, nb_calls=2, receiver="player"
        )
        self._assert_calls_for_send_message(
            self.game_master_ws.sendMessage, snapshot, nb_calls=1, receiver="game_master"
        )

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_join_game"])
    @pytest.mark.asyncio
    async def test_update_slot(self, snapshot):
        await self.player_ws.onMessage(
            self._get_message("update_player_slot.json"), is_binary=False
        )

        self._assert_calls_for_send_message(
            self.player_ws.sendMessage, snapshot, nb_calls=1, receiver="player"
        )
        self._assert_calls_for_send_message(
            self.game_master_ws.sendMessage, snapshot, nb_calls=1, receiver="game_master"
        )

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_update_slot"])
    @pytest.mark.asyncio
    async def test_player_close_slot(self, snapshot):
        await self.player_ws.onMessage(self._get_message("close_slot.json"), is_binary=False)

        self._assert_calls_for_send_message(
            self.player_ws.sendMessage, snapshot, nb_calls=1, receiver="player"
        )
        self._assert_calls_for_send_message(
            self.game_master_ws.sendMessage, snapshot, nb_calls=1, receiver="game_master"
        )

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_player_close_slot"])
    @pytest.mark.asyncio
    async def test_game_master_close_slot(self, snapshot):
        await self.game_master_ws.onMessage(self._get_message("close_slot.json"), is_binary=False)

        self._assert_calls_for_send_message(
            self.game_master_ws.sendMessage, snapshot, nb_calls=1, receiver="game_master"
        )
        self._assert_calls_for_send_message(
            self.player_ws.sendMessage, snapshot, nb_calls=1, receiver="player"
        )

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_game_master_close_slot"])
    @pytest.mark.asyncio
    async def test_player_create_game(self, snapshot):
        await self.player_ws.onMessage(self._get_message("create_game.json"), is_binary=False)

        self._assert_calls_for_send_message(
            self.player_ws.sendMessage, snapshot, nb_calls=1, receiver="player"
        )
        self._assert_calls_for_send_message(
            self.game_master_ws.sendMessage, snapshot, nb_calls=0, receiver="game_master"
        )

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_player_create_game"])
    @pytest.mark.asyncio
    async def test_game_master_create_game_missing_player(self, snapshot):
        await self.game_master_ws.onMessage(
            self._get_message("create_game_missing_player.json"), is_binary=False
        )

        self._assert_calls_for_send_message(
            self.game_master_ws.sendMessage, snapshot, nb_calls=1, receiver="game_master"
        )
        self._assert_calls_for_send_message(
            self.player_ws.sendMessage, snapshot, nb_calls=0, receiver="player"
        )

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_game_master_create_game_missing_player"])
    @pytest.mark.asyncio
    async def test_game_master_create_game(self, mocker, snapshot):
        mocker.patch("aot.api.game_factory.random.choices", mocked_choices)
        # We reverse a stable list of cards. Since it is stable, the Assassin are always first.
        # And they have special actions which makes them harder to handle in tests.
        mocker.patch("aot.game.cards.deck.random.sample", mocked_sample_reversed)

        await self.game_master_ws.onMessage(self._get_message("create_game.json"), is_binary=False)

        self._assert_calls_for_send_message(
            self.game_master_ws.sendMessage, snapshot, nb_calls=2, receiver="game_master"
        )
        self._assert_calls_for_send_message(
            self.player_ws.sendMessage, snapshot, nb_calls=2, receiver="player"
        )
