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

from aot import (
    get_board,
    get_game,
    get_cards_list,
    get_number_players,
    get_trumps_list,
)
from aot.api import Api
from aot.api.api_cache import ApiCache
from aot.cards import Deck
from aot.cards.trumps import Gauge
from aot.game import Player
from unittest.mock import MagicMock


class PickleStub:
    @classmethod
    def loads(cls, arg):
        return arg

    @classmethod
    def dumps(cls, arg):
        return arg


@pytest.fixture
def board():
    return get_board()


@pytest.fixture
def deck(board):
    cards = get_cards_list(board)
    return Deck(cards)


@pytest.fixture
def player(board, deck):
    player = Player(None, None, 0, board, deck, MagicMock(), trumps=get_trumps_list(test=True))
    player.is_connected = True
    return player


@pytest.fixture
def game():
    players_description = [{
        'name': 'Player {}'.format(i),
        'index': i,
        'id': i,
    } for i in range(get_number_players())]
    g = get_game(players_description, test=True)
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
def api_cache(mock):
    mock.patch('aot.api.api_cache.Redis', site_effect=MagicMock())
    mock.patch('aot.api.api_cache.pickle', PickleStub)
    cache = ApiCache()
    cache.init('game_id', 'player_id')
    cache._cache = MagicMock()
    return cache


@pytest.fixture
def api_cache_cls(mock):
    mock.patch('aot.api.api_cache.Redis', site_effect=MagicMock())
    mock.patch('aot.api.api_cache.pickle', PickleStub)

    return ApiCache
