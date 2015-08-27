import asyncio
import logging
import pytest
import redis

import aot
from aot.api.api_cache import ApiCache
from aot.test.integration import PlayerWs


logging.basicConfig(level=logging.DEBUG)


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


@pytest.fixture
def cache():
    return ApiCache()


@pytest.mark.asyncio
def test_game_init(player1):
    yield from asyncio.wait([player1.connect()])
    yield from player1.send('init_game')
    response, expected_response = yield from player1.recv('init_game')
    assert 'game_id' in response
    assert len(response['game_id']) > 0
    # game_id is random, values from response and expected_response cannot be equal
    del response['game_id']
    del expected_response['game_id']
    assert response == expected_response
    yield from asyncio.wait([player1.close()])


@pytest.mark.asyncio
def test_add_slot(player1):
    yield from asyncio.wait([player1.connect()])
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    response, expected_response = yield from player1.recv('add_slot')
    assert response == expected_response
    yield from asyncio.wait([player1.close()])


@pytest.mark.asyncio
def test_update_slot(player1, cache):
    # Update his/her slot
    yield from asyncio.wait([player1.connect()])
    yield from player1.send('init_game')
    yield from player1.recv()
    yield from player1.send('update_slot')
    response, expected_response = yield from player1.recv('update_slot')
    assert response == expected_response
    # Check object in db. Player 1 took the slot, so it must have its id
    saved_slot0 = cache.get_slot(player1.game_id, 0)
    assert 'player_id' in saved_slot0
    assert len(saved_slot0['player_id']) > 0
    # Player id never appears during communications
    player1_id = saved_slot0['player_id']
    del saved_slot0['player_id']
    assert saved_slot0 == response['slot']

    # Update status second slot which has no player_id
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')
    response, expected_response = yield from player1.recv('update_slot2')
    assert response == expected_response
    # Check in db
    saved_slot0['player_id'] = player1_id
    assert saved_slot0 == cache.get_slot(player1.game_id, 0)
    saved_slot1 = cache.get_slot(player1.game_id, 1)
    assert 'player_id' not in saved_slot1
    assert saved_slot1 == response['slot']
    yield from asyncio.wait([player1.close()])
