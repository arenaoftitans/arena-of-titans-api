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

import asyncio
import json
import pytest
import redis
import websockets

import aot
from aot.api.utils import RequestTypes


def get_request(request_type):
    with open('doc/api/requests/{}.json'.format(request_type)) as request_file:
        return json.load(request_file)


def get_response(request_type):
    with open('doc/api/responses/{}.json'.format(request_type)) as response_file:
        return json.load(response_file)


@pytest.yield_fixture(autouse=True)
def flush_cache():
    cache = redis.Redis(
        host=aot.config['cache']['server_host'],
        port=aot.config['cache']['server_port'])
    flush(cache)
    yield
    flush(cache)


def flush(cache):
    cache.execute_command('FLUSHALL')


@pytest.yield_fixture
def players(event_loop):
    players = Players(event_loop)
    yield players
    if not event_loop.is_closed():
        event_loop.run_until_complete(players.close())


@pytest.fixture
def player1(players, event_loop):
    event_loop.run_until_complete(players[0].connect())
    return players[0]


@pytest.fixture
def player2(players, event_loop):
    players.add()
    event_loop.run_until_complete(players[1].connect())
    return players[1]


@asyncio.coroutine
def create_game(*players, with_holes=False):
    player1 = players[0]
    if not player1.is_connected:
        yield from player1.connect()
    yield from player1.send('init_game', message_override={'test': True})
    yield from player1.recv()

    if with_holes:
        msg = {
            'slot': {
                'player_name': '',
                'state': 'CLOSED',
                'index': 1
            }
        }
        yield from player1.send('update_slot2', message_override=msg)
        yield from player1.recv()

    game_id = yield from player1.get_game_id()
    if with_holes:
        index = 2
    else:
        index = 1
    for player in players[1:]:
        if not player.is_connected:
            yield from player.connect()
        index += 1
        yield from player.connect()
        msg = {
            'game_id': game_id,
            'player_name': 'Player ' + str(index),
        }
        yield from player.send('join_game', message_override=msg)
        yield from player.recv()

    create_game_msg = get_request('create_game')
    if with_holes:
        create_game_msg['create_game_request'].insert(1, None)

    if len(players) > 2:
        for i in range(2, len(players)):
            create_game_msg['create_game_request'].append({
                'index': i,
                'hero': 'daemon',
                'name': 'Player ' + str(i + 1)
            })

    # Correct player indexes (expect 1st) if there is holes
    if with_holes:
        for player_description in create_game_msg['create_game_request'][1:]:
            if player_description:
                player_description['index'] += 1

    yield from player1.send('create_game', message_override=create_game_msg)


class Players:
    def __init__(self, event_loop):
        self._players = []
        self._event_loop = event_loop
        self.add()

    def add(self):
        next_index = len(self._players)
        player = PlayerWs(next_index, self.on_send, self._event_loop)
        self._players.append(player)
        return player

    def on_send(self, request_name, sender_index):
        for player in self._players:
            # view_possible_squares responses are only send to the sender, we must not increase
            # the recieve_index for the others.
            if request_name == 'view_possible_squares' and player.index != sender_index:
                continue

            if player.has_joined_game:
                player.recieve_index += 1

    @asyncio.coroutine
    def close(self):
        return [player.close() for player in self._players]

    @property
    def players(self):
        return self._players

    def __getitem__(self, index):
        return self._players[index]

    def __len__(self):
        return len(self._players)


class PlayerWs:
    def __init__(self, index, on_send, event_loop):
        self.index = index
        self.on_send = on_send
        self.has_joined_game = False
        self.recieve_index = 0
        self.number_asked = 0
        self.ws = None
        self._game_id = None
        self._player_id = None
        self._event_loop = event_loop

    @asyncio.coroutine
    def connect(self):
        ws_endpoint = 'ws://{host}:{port}'.format(
            host=aot.config['api']['host'],
            port=aot.config['api']['ws_port'])
        self.ws = yield from websockets.connect(ws_endpoint, loop=self._event_loop)

    @asyncio.coroutine
    def send(self, request_name=None, message_override=dict(), message=None):
        if request_name == 'init_game' or request_name == 'join_game':
            self.has_joined_game = True
        if message is None:
            message = get_request(request_name)
        for key, value in message_override.items():
            message[key] = value
        self.on_send(request_name, self.index)
        yield from self.ws.send(json.dumps(message).encode('utf-8'))

    @asyncio.coroutine
    def recv(self, response_name=None):
        must_increase_recieve_index = False
        for i in range(self.number_asked, self.recieve_index):
            self.number_asked += 1
            resp = None
            while resp is None:
                resp = yield from self.ws.recv()
                resp = json.loads(resp)

            if 'rt' in resp and resp['rt'] == RequestTypes.GAME_INITIALIZED:
                self._game_id = resp['game_id']
                self._player_id = resp['player_id']
            elif 'rt' in resp and resp['rt'] == RequestTypes.PLAYER_PLAYED:
                # Each PLAYER_PLAYED request is followed by the play request which update cards,
                # trumps, … for the current player. So we need to increase the recieve_index by
                # one to correctly get it.
                must_increase_recieve_index = True

            # If at this stage, _game_id is still None, something went wrong and resp is most
            # likely an error.
            if self._game_id is None:
                break

        if must_increase_recieve_index:
            self.recieve_index += 1

        if response_name:
            return resp, get_response(response_name)
        else:
            return resp

    @asyncio.coroutine
    def get_game_id(self):
        if self._game_id is None:
            yield from self.recv()
        return self._game_id

    @asyncio.coroutine
    def get_player_id(self):
        if self._player_id is None:
            yield from self.recv()
        return self._player_id

    @asyncio.coroutine
    def close(self):
        yield from self.ws.close()

    @property
    def is_connected(self):
        return self.ws is not None
