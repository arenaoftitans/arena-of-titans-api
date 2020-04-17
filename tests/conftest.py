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

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from aot.api import Api
from aot.api.cache import Cache
from aot.api.game_factory import build_cards_list, build_trumps_list, create_game_for_players
from aot.game import Player
from aot.game.board import Board
from aot.game.cards import Deck
from aot.game.config import TEST_CONFIG
from aot.game.trumps import Gauge


def aredis():
    redis = MagicMock()
    redis.keys = AsyncMock()
    return redis


def mocked_choices(a_list, weights=None, k=None):
    k = k or len(a_list)
    return a_list[:k]


def mocked_sample_reversed(a_list: list, k: int):
    new_list = a_list.copy()
    new_list.reverse()
    return new_list


@pytest.fixture
def board():
    return Board(TEST_CONFIG["board"])


@pytest.fixture
def deck(board):
    cards = build_cards_list(TEST_CONFIG, board)
    return Deck(cards)


@pytest.fixture
def player(mocker, board, deck):
    mocker.patch("aot.api.game_factory.random.choices", mocked_choices)
    player = Player(
        "Player",
        None,
        0,
        board,
        deck,
        MagicMock(),
        available_trumps=build_trumps_list(TEST_CONFIG),
    )
    player.is_connected = True
    return player


@pytest.fixture
def player2(mocker, board, deck):
    mocker.patch("aot.api.game_factory.random.choices", mocked_choices)
    player = Player(
        "Player 2",
        None,
        1,
        board,
        deck,
        MagicMock(),
        available_trumps=build_trumps_list(TEST_CONFIG),
    )
    player.is_connected = True
    return player


@pytest.fixture
def game(mocker):
    mocker.patch("aot.api.game_factory.random.choices", mocked_choices)
    # We reverse a stable list of cards. Since it is stable, the Assassin are always first. And they
    # have special actions which makes them harder to handle in tests.
    mocker.patch("aot.game.cards.deck.random.sample", mocked_sample_reversed)
    players_description = [
        {"name": "Player {}".format(i), "index": i, "id": i, "hero": "Ulya"}
        for i in range(TEST_CONFIG["number_players"])
    ]
    g = create_game_for_players(players_description, name="test", game_id="game_id")
    for player in g.players:
        player.is_connected = True

    return g


@pytest.fixture
def gauge():
    return Gauge(None)


@pytest.fixture
def api(mocker):
    mocker.patch("aot.api.Api._api_delay", new_callable=PropertyMock, return_value=10)
    a = Api()
    a._id = 0
    a._clients_pending_disconnection = {}
    a._clients_pending_reconnection = {}
    a._pending_ai = set()

    return a


@pytest.fixture
def cache(mocker):
    mocker.patch("aot.api.cache.Redis", site_effect=aredis())
    cache = Cache()
    cache.init("game_id", "player_id")
    cache._cache = MagicMock()
    return cache


@pytest.fixture
def cache_cls(mocker):
    mocker.patch("aot.api.cache.Redis", site_effect=MagicMock())

    return Cache
