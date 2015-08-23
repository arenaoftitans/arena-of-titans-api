import json
import pytest
import redis
from websocket import create_connection

import aot


@pytest.yield_fixture(autouse=True)
def flush_cache():
    cache = redis.Redis(host=aot.config['cache']['server_host'], port=aot.config['cache']['server_port'])
    flush(cache)
    yield
    flush(cache)


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


def send(request_type, ws):
    with open('doc/api/requests/{}.json'.format(request_type)) as request_file:
        ws.send(request_file.read())


def get_response(request_type, ws):
    response = json.loads(ws.recv())
    with open('doc/api/responses/{}.json'.format(request_type)) as response_file:
        return response, json.load(response_file)


def test_game_initialization(player1):
    send('init_game', player1)
    response, expected_response = get_response('init_game', player1)
    assert 'player_id' in response
    assert len(response['player_id']) > 0
    # player_id is a random string, removing before testing equality
    del response['player_id']
    del expected_response['player_id']
    assert response == expected_response
