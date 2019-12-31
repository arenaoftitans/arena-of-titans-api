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

from ..api import Api
from ..api.cache import Cache
from ..api.game_factory import build_cards_list, build_trumps_list, create_game_for_players
from ..board import Board
from ..cards import Deck
from ..cards.trumps import Gauge
from ..game import Player
from ..game.config import TEST_CONFIG


class AsyncMagicMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


def aredis():
    redis = MagicMock()
    redis.keys = AsyncMagicMock()
    return redis


def mocked_choices(a_list, weights=None, k=None):
    k = k or len(a_list)
    return a_list[:k]


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
        "Player", None, 0, board, deck, MagicMock(), trumps=build_trumps_list(TEST_CONFIG),
    )
    player.is_connected = True
    return player


@pytest.fixture
def player2(mocker, board, deck):
    mocker.patch("aot.api.game_factory.random.choices", mocked_choices)
    player = Player(
        "Player 2", None, 1, board, deck, MagicMock(), trumps=build_trumps_list(TEST_CONFIG),
    )
    player.is_connected = True
    return player


@pytest.fixture
def game(mocker):
    mocker.patch("aot.api.game_factory.random.choices", mocked_choices)
    players_description = [
        {"name": "Player {}".format(i), "index": i, "id": i, "hero": "Ulya"}
        for i in range(TEST_CONFIG["number_players"])
    ]
    g = create_game_for_players(players_description, name="test")
    for player in g.players:
        player.is_connected = True

    return g


@pytest.fixture
def gauge():
    return Gauge(None)


@pytest.fixture
def api():
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
