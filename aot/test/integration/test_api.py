import asyncio
import json
import pytest
import redis

import aot


from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

class ApiTestClient(WebSocketClientProtocol):
    #: Contains the list of all event loops, so we can stop them. Player 0 is players[0], …
    players = []
    #: Contains the list of messages to be sent when the websocket opens. One per player, if a
    #: player has nothing to send, set to None.
    on_open_messages = []
    #: Same as above except that this time, it contains a list of messages for each player.
    on_message_messages = []
    #: Same as above but contains a function that checks whether the response is correct
    on_message_checks = []
    #: Errors
    success = True

    def onOpen(self):
        self._index = len(self.players) - 1
        self._on_message_messages_index = 0
        self._on_message_messages = self.on_message_messages[self._index]
        self._on_open_message = self.on_open_messages[self._index]
        self._on_message_checks = self.on_message_checks[self._index]
        self._me = self.players[self._index]
        if self._on_open_message is not None:
            self.sendMessage(self.on_open_messages[self._index])

    def sendMessage(self, message):
        if isinstance(message, str):
            message = message.encode('utf-8')
        elif isinstance(message, dict):
            message = json.dumps(message).encode('utf-8')
        if isinstance(message, bytes):
            super().sendMessage(message)

    def onMessage(self, payload, isBinary):
        message = json.loads(payload.decode('utf-8'))
        if self._on_message_checks[self._on_message_messages_index] is not None:
            try:
                self._on_message_checks[self._on_message_messages_index](message)
            except Exception as e:
                ApiTestClient.success = False
                self.stop()
                raise e
        if self._on_message_messages_index == len(self._on_message_messages):
            self.stop()
        elif self._on_message_messages[self._on_message_messages_index] is not None:
            self.sendMessage(self._on_message_messages[self._on_message_messages_index])
        self._on_message_messages_index += 1

    def stop(self):
        self.sendClose()
        self._me.stop()



@pytest.yield_fixture(autouse=True)
def flush_cache():
    cache = redis.Redis(host=aot.config['cache']['server_host'], port=aot.config['cache']['server_port'])
    flush(cache)
    yield
    flush(cache)


@pytest.fixture(autouse=True)
def clear_players():
    ApiTestClient.players = []


def flush(cache):
    cache.execute_command('FLUSHALL')


@pytest.yield_fixture
def player1():
    ws_endpoint = 'ws://{host}:{port}'.format(
        host=aot.config['api']['host'],
        port=aot.config['api']['ws_port'])
    ws = create_connection(ws_endpoint)
    yield ws
    ws.close()


def get_request(request_type):
    with open('doc/api/requests/{}.json'.format(request_type)) as request_file:
        return json.load(request_file)


def get_response(request_type):
    with open('doc/api/responses/{}.json'.format(request_type)) as response_file:
        return json.load(response_file)


def test_game_initialization():
    ws_endpoint = 'ws://{host}:{port}'.format(
        host=aot.config['api']['host'],
        port=aot.config['api']['ws_port'])
    factory = WebSocketClientFactory(ws_endpoint, debug=True)
    factory.protocol = ApiTestClient

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, aot.config['api']['host'], aot.config['api']['ws_port'])

    ApiTestClient.players.append(loop)
    ApiTestClient.on_open_messages.append(get_request('init_game'))
    def test_init_game(response):
        expected_response = get_response('init_game')
        assert 'player_id' in response
        assert len(response['player_id']) > 0
        # player_id is a random string, removing before testing equality
        del response['player_id']
        del expected_response['player_id']
        assert response == expected_response
    ApiTestClient.on_message_messages.append([None])
    ApiTestClient.on_message_checks.append([test_init_game, None])

    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
    assert ApiTestClient.success


import websockets
import logging
logging.basicConfig(level=logging.DEBUG)

class PlayerWs:
    def __init__(self):
        self.recieve_index = 0

    @asyncio.coroutine
    def connect(self):
        ws_endpoint = 'ws://{host}:{port}'.format(
            host=aot.config['api']['host'],
            port=aot.config['api']['ws_port'])
        self.ws = yield from websockets.connect(ws_endpoint)

    @asyncio.coroutine
    def send(self, message, increment=True):
        if increment:
            self.recieve_index += 1
        yield from self.ws.send(message)

    @asyncio.coroutine
    def recv(self):
        for _ in range(self.recieve_index):
            resp = yield from self.ws.recv()
        return json.loads(resp)


@pytest.mark.asyncio
def test_game_init():
    player1 = PlayerWs()
    yield from player1.connect()
    yield from player1.send(json.dumps(get_request('init_game')).encode('utf-8'))
    response = yield from player1.recv()
    expected_response = get_response('init_game')
    assert 'player_id' in response
    assert len(response['player_id']) > 0
    # player_id is a random string, removing before testing equality
    del response['player_id']
    del expected_response['player_id']


def test_add_slot():
    ws_endpoint = 'ws://{host}:{port}'.format(
        host=aot.config['api']['host'],
        port=aot.config['api']['ws_port'])
