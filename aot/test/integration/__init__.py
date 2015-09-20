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
    players = Players()
    yield players
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
def create_game(*players):
    player1 = players[0]
    yield from player1.send('init_game')
    for i in range(len(players)):
        msg = {
            "index": i + 1,
            "state": "OPEN",
            "player_name": ""
        }
        yield from player1.send('add_slot', message_override={'slot': msg})

    game_id = yield from player1.get_game_id()
    for player in players[1:]:
        yield from player.connect()
        yield from player.send('join_game', message_override={'game_id': game_id})

    yield from player1.send('create_game')


class Players:
    def __init__(self):
        self._players = []
        self.add()

    def add(self):
        next_index = len(self._players)
        self._players.append(PlayerWs(next_index, self.on_send))

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


class PlayerWs:
    def __init__(self, index, on_send):
        self.index = index
        self.on_send = on_send
        self.has_joined_game = False
        self.recieve_index = 0
        self.number_asked = 0
        self._game_id = None

    @asyncio.coroutine
    def connect(self):
        ws_endpoint = 'ws://{host}:{port}'.format(
            host=aot.config['api']['host'],
            port=aot.config['api']['ws_port'])
        self.ws = yield from websockets.connect(ws_endpoint)

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
                print(self.index, resp)

            if 'rt' in resp and resp['rt'] == RequestTypes.GAME_INITIALIZED.value:
                self._game_id = resp['game_id']
            elif 'rt' in resp and resp['rt'] == RequestTypes.PLAYER_MOVED.value:
                # Each PLAYER_MOVED request is followed by the play request which update cards,
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
    def close(self):
        yield from self.ws.close()
