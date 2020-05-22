#
#  Copyright (C) 2015-2020 by Last Run Contributors.
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
import re
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


@pytest.fixture(scope="module")
def create_new_cache_instance(event_loop):
    """This is to prevent issues from interaction with the cache unit tests."""
    config.setup_config()
    Cache.create_new_instance(loop=event_loop)


class IntegrationTestsBase:
    game_master_id = "test-game-master-id"
    player_id = "player_id"
    game_id = "test-game-id"
    messages_folder = None

    @classmethod
    def setup_class(cls):
        daiquiri.setup(level=logging.DEBUG)

        cls.game_master_ws = AotWs()
        cls.game_master_ws._wskey = cls.game_master_id
        cls.game_master_ws.sendMessage = AsyncMock()

        cls.player_ws = AotWs()
        cls.player_ws._wskey = cls.player_id
        cls.player_ws.sendMessage = AsyncMock()

    @pytest.fixture(scope="function", autouse=True)
    def reset_send_message_calls(self, event_loop, create_new_cache_instance):
        self.game_master_ws.set_event_loop_for_testing(event_loop)
        self.player_ws.set_event_loop_for_testing(event_loop)

        self.game_master_ws.sendMessage.reset_mock()
        self.player_ws.sendMessage.reset_mock()

    def get_message(self, message_path):
        root = path.dirname(__file__)
        path_to_open = path.join(root, self.messages_folder, message_path)

        with open(path_to_open, "rb") as message_file:
            return message_file.read()

    def get_message_as_dict(self, message_path):
        root = path.dirname(__file__)
        path_to_open = path.join(root, self.messages_folder, message_path)

        with open(path_to_open, "r") as message_file:
            return json.load(message_file)

    def assert_calls_for_player(self, snapshot, nb_calls):
        self._assert_calls_for_send_message(
            self.player_ws.sendMessage, snapshot, nb_calls, "player"
        )

    def assert_calls_for_game_master(self, snapshot, nb_calls):
        self._assert_calls_for_send_message(
            self.game_master_ws.sendMessage, snapshot, nb_calls, "game_master"
        )

    def _assert_calls_for_send_message(self, send_message_mock, snapshot, nb_calls, receiver):
        assert len(send_message_mock.mock_calls) == nb_calls
        for index, response_call in enumerate(send_message_mock.mock_calls):
            assert len(response_call.args) == 1
            assert response_call.kwargs == {}
            response_message = re.sub(
                r'"elapsed_time": \d+', '"elapsed_time": 10', response_call.args[0].decode("utf-8")
            )
            response = json.loads(response_message)
            snapshot.assert_match(response, f"{receiver}-{index}")


class TestCreateGame(IntegrationTestsBase):
    messages_folder = "lobby_messages"

    @pytest.mark.integration
    @pytest.mark.dependency()
    @pytest.mark.asyncio
    async def test_create_lobby(self, mocker, snapshot):
        await Cache.clean_for_game(self.game_id)
        mocker.patch.object(
            sys.modules["aot.api.views.create_game"], "_create_game_id", return_value=self.game_id,
        )
        await self.game_master_ws.onOpen()

        await self.game_master_ws.onMessage(self.get_message("create_lobby.json"), is_binary=False)

        self.assert_calls_for_game_master(snapshot, nb_calls=2)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_create_lobby"])
    @pytest.mark.asyncio
    async def test_join_game(self, snapshot):
        await self.player_ws.onOpen()

        await self.player_ws.onMessage(self.get_message("join_game.json"), is_binary=False)

        self.assert_calls_for_player(
            snapshot, nb_calls=2,
        )
        self.assert_calls_for_game_master(snapshot, nb_calls=1)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_join_game"])
    @pytest.mark.asyncio
    async def test_update_slot(self, snapshot):
        await self.player_ws.onMessage(self.get_message("update_player_slot.json"), is_binary=False)

        self.assert_calls_for_player(snapshot, nb_calls=1)
        self.assert_calls_for_game_master(snapshot, nb_calls=1)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_update_slot"])
    @pytest.mark.asyncio
    async def test_player_close_slot(self, snapshot):
        await self.player_ws.onMessage(self.get_message("close_slot.json"), is_binary=False)

        self.assert_calls_for_player(snapshot, nb_calls=1)
        self.assert_calls_for_game_master(snapshot, nb_calls=1)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_player_close_slot"])
    @pytest.mark.asyncio
    async def test_game_master_close_slot(self, snapshot):
        await self.game_master_ws.onMessage(self.get_message("close_slot.json"), is_binary=False)

        self.assert_calls_for_game_master(snapshot, nb_calls=1)
        self.assert_calls_for_player(snapshot, nb_calls=1)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_game_master_close_slot"])
    @pytest.mark.asyncio
    async def test_player_create_game(self, snapshot):
        await self.player_ws.onMessage(self.get_message("create_game.json"), is_binary=False)

        self.assert_calls_for_player(snapshot, nb_calls=1)
        self.assert_calls_for_game_master(snapshot, nb_calls=0)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_player_create_game"])
    @pytest.mark.asyncio
    async def test_game_master_create_game_missing_player(self, snapshot):
        await self.game_master_ws.onMessage(
            self.get_message("create_game_missing_player.json"), is_binary=False
        )

        self.assert_calls_for_game_master(snapshot, nb_calls=1)
        self.assert_calls_for_player(snapshot, nb_calls=0)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_game_master_create_game_missing_player"])
    @pytest.mark.asyncio
    async def test_game_master_create_game(self, mocker, snapshot):
        mocker.patch("aot.api.game_factory.random.choices", mocked_choices)
        # We reverse a stable list of cards. Since it is stable, the Assassin are always first.
        # And they have special actions which makes them harder to handle in tests.
        mocker.patch("aot.game.cards.deck.random.sample", mocked_sample_reversed)

        await self.game_master_ws.onMessage(self.get_message("create_game.json"), is_binary=False)

        self.assert_calls_for_game_master(snapshot, nb_calls=2)
        self.assert_calls_for_player(snapshot, nb_calls=2)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_game_master_create_game"])
    @pytest.mark.asyncio
    async def test_disconnect(self, mocker):
        # Pretend the game has not started since it makes disconnection testing way easier.
        mocker.patch.object(self.game_master_ws._api._cache, "has_game_started", return_value=False)
        mocker.patch.object(self.player_ws._api._cache, "has_game_started", return_value=False)

        assert len(AotWs._clients) == 2

        await self.game_master_ws.onClose(was_clean=True, code=1001, reason=None)
        await self.player_ws.onClose(was_clean=True, code=1001, reason=None)

        assert len(AotWs._clients) == 0


class TestPlayGame(IntegrationTestsBase):
    messages_folder = "play_messages"

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestCreateGame::test_disconnect"])
    @pytest.mark.asyncio
    async def test_reconnect_game_master(self, snapshot):
        self.game_master_ws._wskey = "tmp-key"

        await self.game_master_ws.onOpen()
        await self.game_master_ws.onMessage(self.get_message("reconnect.json"), is_binary=False)

        self.assert_calls_for_game_master(snapshot, nb_calls=1)
        assert self.game_master_ws.id == self.game_master_id

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestPlayGame::test_reconnect_game_master"])
    @pytest.mark.asyncio
    async def test_reconnect_player_wrong_game_id(self, snapshot):
        self.player_ws._wskey = "tmp-key"

        await self.player_ws.onOpen()

        message = self.get_message_as_dict("reconnect.json")
        message["request"]["game_id"] = "toto"
        await self.player_ws.onMessage(json.dumps(message).encode("utf-8"), is_binary=False)

        self.assert_calls_for_player(snapshot, nb_calls=1)
        self.assert_calls_for_game_master(snapshot, nb_calls=0)
        await self.player_ws.onClose(was_clean=True, code=1001, reason=None)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestPlayGame::test_reconnect_player_wrong_game_id"])
    @pytest.mark.asyncio
    async def test_reconnect_player_wrong_player_id(self, snapshot):
        self.player_ws._wskey = "tmp-key"

        await self.player_ws.onOpen()

        message = self.get_message_as_dict("reconnect.json")
        message["request"]["player_id"] = "toto"
        await self.player_ws.onMessage(json.dumps(message).encode("utf-8"), is_binary=False)

        self.assert_calls_for_player(snapshot, nb_calls=1)
        self.assert_calls_for_game_master(snapshot, nb_calls=0)
        await self.player_ws.onClose(was_clean=True, code=1001, reason=None)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestPlayGame::test_reconnect_player_wrong_player_id"])
    @pytest.mark.asyncio
    async def test_reconnect_player(self, snapshot):
        self.player_ws._wskey = "tmp-key"
        await self.player_ws.onOpen()

        message = self.get_message_as_dict("reconnect.json")
        message["request"]["player_id"] = self.player_id
        await self.player_ws.onMessage(json.dumps(message).encode("utf-8"), is_binary=False)

        self.assert_calls_for_player(snapshot, nb_calls=1)
        self.assert_calls_for_game_master(snapshot, nb_calls=0)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestPlayGame::test_reconnect_player"])
    @pytest.mark.asyncio
    async def test_reconnect_player_already_connected(self, snapshot):
        message = self.get_message_as_dict("reconnect.json")
        message["request"]["player_id"] = self.player_id
        await self.player_ws.onMessage(json.dumps(message).encode("utf-8"), is_binary=False)

        self.assert_calls_for_player(snapshot, nb_calls=1)
        self.assert_calls_for_game_master(snapshot, nb_calls=0)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestPlayGame::test_reconnect_player_already_connected"])
    @pytest.mark.asyncio
    async def test_play_card_not_your_turn(self, snapshot):
        await self.player_ws.onMessage(self.get_message("play_card.json"), is_binary=False)

        self.assert_calls_for_player(snapshot, nb_calls=1)
        self.assert_calls_for_game_master(snapshot, nb_calls=0)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestPlayGame::test_play_card_not_your_turn"])
    @pytest.mark.asyncio
    async def test_play_card_not_in_hand(self, snapshot):
        message = self.get_message_as_dict("play_card.json")
        message["request"]["card_name"] = "Assassin"

        await self.game_master_ws.onMessage(json.dumps(message).encode("utf-8"), is_binary=False)

        self.assert_calls_for_game_master(snapshot, nb_calls=1)
        self.assert_calls_for_player(snapshot, nb_calls=0)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestPlayGame::test_play_card_not_in_hand"])
    @pytest.mark.asyncio
    async def test_play_card_wrong_square(self, snapshot):
        message = self.get_message_as_dict("play_card.json")
        message["request"]["x"] = 0
        message["request"]["y"] = 0

        await self.game_master_ws.onMessage(json.dumps(message).encode("utf-8"), is_binary=False)

        self.assert_calls_for_game_master(snapshot, nb_calls=1)
        self.assert_calls_for_player(snapshot, nb_calls=0)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestPlayGame::test_play_card_not_in_hand"])
    @pytest.mark.asyncio
    async def test_view_possible_squares(self, snapshot):
        await self.game_master_ws.onMessage(
            self.get_message("view_possible_squares.json"), is_binary=False
        )

        self.assert_calls_for_game_master(snapshot, nb_calls=1)
        self.assert_calls_for_player(snapshot, nb_calls=0)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestPlayGame::test_view_possible_squares"])
    @pytest.mark.asyncio
    async def test_play_card(self, snapshot):
        await self.game_master_ws.onMessage(self.get_message("play_card.json"), is_binary=False)

        self.assert_calls_for_game_master(snapshot, nb_calls=2)
        self.assert_calls_for_player(snapshot, nb_calls=2)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestPlayGame::test_play_card"])
    @pytest.mark.asyncio
    async def test_discard_card(self, snapshot):
        await self.game_master_ws.onMessage(self.get_message("discard_card.json"), is_binary=False)

        self.assert_calls_for_game_master(snapshot, nb_calls=2)
        self.assert_calls_for_player(snapshot, nb_calls=2)

    @pytest.mark.integration
    @pytest.mark.dependency(depends=["TestPlayGame::test_discard_card"])
    @pytest.mark.asyncio
    async def test_pass_turn(self, snapshot):
        await self.player_ws.onMessage(self.get_message("pass_turn.json"), is_binary=False)

        self.assert_calls_for_player(snapshot, nb_calls=2)
        self.assert_calls_for_game_master(snapshot, nb_calls=2)
