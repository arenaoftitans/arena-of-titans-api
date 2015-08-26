import asyncio
import pytest
import redis

import aot
from aot.test.integration import PlayerWs


@pytest.yield_fixture(autouse=True)
def flush_cache():
    cache = redis.Redis(host=aot.config['cache']['server_host'], port=aot.config['cache']['server_port'])
    flush(cache)
    yield
    flush(cache)


def flush(cache):
    cache.execute_command('FLUSHALL')


@pytest.fixture
def player1():
    player = PlayerWs()
    return player


@pytest.mark.asyncio
def test_game_init(player1):
    yield from asyncio.wait([player1.connect()])
    yield from player1.send('init_game')
    response, expected_response = yield from player1.recv('init_game')
    assert 'player_id' in response
    assert len(response['player_id']) > 0
    # player_id is a random string, removing before testing equality
    del response['player_id']
    del expected_response['player_id']
    yield from player1.close()
