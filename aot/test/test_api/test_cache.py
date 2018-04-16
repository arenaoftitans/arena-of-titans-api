################################################################################
# Copyright (C) 2016 by Arena of Titans Contributors.
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

import pickle  # noqa: B403 (bandit: pickle security issues)
from copy import deepcopy
from unittest.mock import MagicMock

import pytest

from .. import (  # noqa: F401
    AsyncMagicMock,
    cache,
    cache_cls,
    game,
)
from ...api.cache import Cache
from ...api.security import decode
from ...config import config


def dumps_list(cache, a_list):
    return [cache.dumps(elt) for elt in a_list]


def setup_module():
    config.setup_config()


def test_connect_tcp_socket(mock):  # noqa: F811
    cfg = {
        'cache': {
            'host': '127.0.0.1',
            'port': '6379',
            'timeout': 5,
        },
    }
    redis = MagicMock()
    mock.patch('aot.api.cache.config', new=cfg)
    mock.patch('aot.api.cache.Redis', new=redis)

    Cache._get_redis_instance(new=True)

    redis.assert_called_once_with(
        host=cfg['cache']['host'],
        port=cfg['cache']['port'],
        connect_timeout=cfg['cache']['timeout'],
        stream_timeout=cfg['cache']['timeout'],
    )


def test_dumps(cache):
    data = {
        'an_object': 'To pickle',
    }

    dump = cache.dumps(data)
    pickle_data = decode(dump)

    assert isinstance(dump, bytes)
    assert pickle_data == pickle.dumps(data)  # noqa: B301 (pickle usage)


def test_loads(cache):
    data = {
        'an_object': 'To pickle',
    }
    dump = cache.dumps(data)

    decoded_data = cache.loads(dump)

    assert decoded_data == data


@pytest.mark.asyncio  # noqa: F811
async def test_test(cache, mock):
    now = MagicMock(return_value='the_date')
    datetime = MagicMock()
    datetime.now = now
    mock.patch('aot.api.cache.datetime', new=datetime)
    cache._cache.set = AsyncMagicMock()

    await cache.test()

    cache._cache.set.assert_called_once_with('test', 'the_date')


@pytest.mark.asyncio  # noqa: F811
async def test_info(cache, mock):
    cache._cache.keys = AsyncMagicMock(return_value=[b'game:game_id', b'toto'])
    cache.get_players_ids = AsyncMagicMock(return_value=['id1', 'id2'])
    cache._cache.hget = AsyncMagicMock(return_value=b'True')

    infos = await cache.info()

    cache._cache.keys.assert_called_once_with()
    assert infos == {
        'average_number_players': 2.0,
        'number_games': 1,
        'number_started_games': 1,
    }


@pytest.mark.asyncio  # noqa: F811
async def test_get_players_ids(cache):
    cache._cache.zrange = AsyncMagicMock(return_value=[b'id0', b'id1'])
    cache._game_id = None

    results = await cache.get_players_ids('game_id')

    assert results == ['id0', 'id1']
    cache._cache.zrange.assert_called_once_with('players:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_get_players_ids_without_game_id(cache):
    cache._cache.zrange = AsyncMagicMock(return_value=[b'id0', b'id1'])

    results = await cache.get_players_ids()

    assert results == ['id0', 'id1']
    cache._cache.zrange.assert_called_once_with('players:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_game_exists(cache, game):
    cache._cache.hget = AsyncMagicMock(return_value=None)
    assert not await cache.game_exists('game_id')
    cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')

    cache._cache.hget = AsyncMagicMock(return_value=game)
    assert await cache.game_exists('game_id')
    cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')


@pytest.mark.asyncio  # noqa: F811
async def test_has_opened_slots(mock, cache):
    cache._cache.lrange = AsyncMagicMock(
        return_value=dumps_list(cache, [
            {'state': 'OPEN'},
            {'state': 'CLOSED'},
        ]),
    )

    assert await cache.has_opened_slots('game_id')
    cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_get_slots_with_game_id(mock, cache):
    slots = [
        {
            'state': 'OPEN',
            'player_id': 'id0',
        },
        {
            'state': 'CLOSED',
            'player_id': 'id1',
        },
    ]
    cache._cache.lrange = AsyncMagicMock(return_value=dumps_list(cache, slots))

    results = await cache.get_slots('game_id')

    assert results == slots
    cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_get_slots_without_game_id(mock, cache):
    slots = [
        {
            'state': 'OPEN',
            'player_id': 'id0',
        },
        {
            'state': 'CLOSED',
            'player_id': 'id1',
        },
    ]
    cache._cache.lrange = AsyncMagicMock(return_value=dumps_list(cache, slots))

    results = await cache.get_slots()

    assert results == slots
    cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_get_slots_exclude_player_ids(cache):
    slots = [
        {
            'state': 'OPEN',
            'player_id': 'id0',
        },
        {
            'state': 'CLOSED',
            'player_id': 'id1',
        },
    ]
    cache._cache.lrange = AsyncMagicMock(return_value=dumps_list(cache, slots))
    for slot in slots:
        del slot['player_id']

    results = await cache.get_slots('game_id', include_player_id=False)

    assert results == slots
    cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_is_member_game(cache):
    cache._cache.zrange = AsyncMagicMock(return_value=[b'id0', b'id1'])

    assert await cache.is_member_game('game_id', 'id0')
    assert not await cache.is_member_game('game_id', 'id100')


@pytest.mark.asyncio  # noqa: F811
async def test_create_new_game(cache):
    slots = []

    def add_slot_cache_side_effect(key, dumped_slot):
        slot = cache.loads(dumped_slot)
        assert key == 'slots:game_id'
        assert slot['index'] == len(slots)
        if len(slots) == 0:
            assert slot['player_id'] == 'player_id'
        else:
            assert not slot['player_id']

        slots.append(slot)

    cache._cache.rpush = AsyncMagicMock(side_effect=add_slot_cache_side_effect)
    cache._cache.hset = AsyncMagicMock()
    cache._cache.expire = AsyncMagicMock()
    cache.get_slots = AsyncMagicMock(return_value=slots)

    await cache.create_new_game()

    assert cache._cache.hset.call_count == 3
    assert cache._cache.rpush.call_count == 8
    assert cache._cache.expire.call_count == 2
    assert cache.get_slots.call_count == 8


@pytest.mark.asyncio  # noqa: F811
async def test_is_test(cache):
    cache._cache.hget = AsyncMagicMock(return_value=b'True')
    assert await cache.is_test()
    cache._cache.hget.assert_called_once_with('game:game_id', 'test')

    cache._cache.hget = AsyncMagicMock(return_value=b'False')
    assert not await cache.is_test()
    cache._cache.hget.assert_called_once_with('game:game_id', 'test')


@pytest.mark.asyncio  # noqa: F811
async def test_get_game(cache, game):
    game.game_id = 'game-id'

    cache._cache.hget = AsyncMagicMock(return_value=cache.dumps(game))
    assert await cache.get_game() == game
    cache._cache.hget.assert_called_once_with('game:game_id', 'game')

    cache._cache.hget = AsyncMagicMock(return_value=None)
    assert await cache.get_game() is None
    cache._cache.hget.assert_called_once_with('game:game_id', 'game')


@pytest.mark.asyncio  # noqa: F811
async def test_save_session(cache):
    cache._cache.zadd = AsyncMagicMock()
    cache._cache.expire = AsyncMagicMock()

    await cache.save_session(1)

    cache._cache.zadd.assert_called_once_with('players:game_id', 1, 'player_id')
    cache._cache.expire.call_count == 1


@pytest.mark.asyncio  # noqa: F811
async def test_get_player_index(cache):
    slots = [
        {
            'player_id': 'player_id',
            'index': 0,
        },
    ]
    cache.get_slots = AsyncMagicMock(return_value=deepcopy(slots))

    assert await cache.get_player_index() == 0


@pytest.mark.asyncio  # noqa: F811
async def test_is_game_master(cache):
    cache._cache.hget = AsyncMagicMock(return_value=b'player_id')
    assert await cache.is_game_master()
    cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')

    cache._cache.hget = AsyncMagicMock(return_value=b'toto')
    assert not await cache.is_game_master()
    cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')

    cache._cache.hget = AsyncMagicMock(return_value=None)
    assert not await cache.is_game_master()
    cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')


@pytest.mark.asyncio  # noqa: F811
async def test_number_taken_slots(cache):
    slots = [{'state': 'TAKEN'}, {'state': 'OPEN'}, {'state': 'AI'}]
    cache.get_slots = AsyncMagicMock(return_value=deepcopy(slots))
    assert await cache.number_taken_slots() == 2


@pytest.mark.asyncio  # noqa: F811
async def test_affect_next_slot(cache):
    slots = [{'state': 'TAKEN'}, {'state': 'OPEN', 'index': 1}, {'state': 'AI'}]
    cache.get_slots = AsyncMagicMock(return_value=deepcopy(slots))
    cache.update_slot = AsyncMagicMock()
    slot = slots[1]
    slot['player_id'] = 'player_id'
    slot['state'] = 'TAKEN'
    slot['player_name'] = 'Player'
    slot['hero'] = 'daemon'

    assert await cache.affect_next_slot('Player', 'daemon') == 1
    cache.update_slot.assert_called_once_with(slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_free(cache):
    cache_slot = {
        'state': 'TAKEN',
        'player_id': 'player_id',
        'index': 0,
    }
    cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    cache._save_slot = AsyncMagicMock()
    slot = {
        'player_id': 'player_id',
        'index': 0,
        'state': 'OPEN',
    }
    del cache_slot['player_id']
    cache_slot['state'] = 'OPEN'

    await cache.update_slot(slot)

    cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_close(cache):
    cache_slot = {
        'state': 'AI',
        'player_name': 'AI 2',
        'index': 0,
    }
    cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    cache._save_slot = AsyncMagicMock()
    cache.is_game_master = AsyncMagicMock(return_value=True)
    slot = {
        'index': 0,
        'state': 'CLOSED',
        'player_name': 'AI 2',
    }
    del cache_slot['player_name']
    cache_slot['state'] = 'CLOSED'

    await cache.update_slot(slot)

    cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_open(cache):
    cache_slot = {
        'state': 'AI',
        'player_name': 'AI 2',
        'index': 0,
    }
    cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    cache._save_slot = AsyncMagicMock()
    cache.is_game_master = AsyncMagicMock(return_value=True)
    slot = {
        'index': 0,
        'state': 'OPEN',
        'player_name': 'AI 2',
    }
    del cache_slot['player_name']
    cache_slot['state'] = 'OPEN'

    await cache.update_slot(slot)

    cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_update_not_game_master(cache):
    cache_slot = {
        'state': 'TAKEN',
        'player_id': 'player_id',
        'index': 0,
    }
    cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    cache._save_slot = AsyncMagicMock()
    slot = {
        'player_id': 'player_id',
        'hero': 'daemon',
        'index': 0,
        'state': 'TAKEN',
    }
    cache_slot['hero'] = 'daemon'

    await cache.update_slot(slot)

    cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_update_game_master(cache):
    cache_slot = {
        'state': 'OPEN',
        'index': 0,
    }
    cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    cache._save_slot = AsyncMagicMock()
    cache.is_game_master = AsyncMagicMock(return_value=True)
    slot = {
        'state': 'AI',
        'index': 0,
    }
    cache_slot['state'] = 'AI'

    await cache.update_slot(slot)

    cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_update_game_master_taken(cache):
    cache_slot = {
        'state': 'TAKEN',
        'index': 0,
    }
    cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    cache._save_slot = AsyncMagicMock()
    cache.is_game_master = AsyncMagicMock(return_value=True)
    slot = {
        'state': 'AI',
        'index': 0,
    }
    cache_slot['state'] = 'AI'

    await cache.update_slot(slot)

    assert cache._save_slot.call_count == 0


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_take(cache):
    cache_slot = {
        'state': 'OPEN',
        'index': 0,
    }
    cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    cache._save_slot = AsyncMagicMock()
    slot = {
        'state': 'TAKEN',
        'player_id': 'player_id',
        'index': 0,
    }
    cache_slot['player_id'] = 'player_id'
    cache_slot['state'] = 'TAKEN'

    await cache.update_slot(slot)

    cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_save_slot(cache):
    slot = {
        'state': 'TAKEN',
        'index': 0,
    }
    cache._cache.lset = AsyncMagicMock()

    await cache._save_slot(slot)

    cache._cache.lset.assert_called_once_with(
        'slots:game_id',
        0,
        cache.dumps(slot),
    )


@pytest.mark.asyncio  # noqa: F811
async def test_slot_exists(cache):
    slot = {
        'index': 0,
    }
    cache.lindex = AsyncMagicMock(return_value=None)
    cache._get_redis_instance = MagicMock(return_value=cache)
    assert not await cache.slot_exists(slot)
    cache.lindex.assert_called_once_with('slots:game_id', 0)

    cache.lindex = AsyncMagicMock(return_value=slot)
    cache._get_redis_instance = MagicMock(return_value=cache)
    assert await cache.slot_exists(slot)
    cache.lindex.assert_called_once_with('slots:game_id', 0)


@pytest.mark.asyncio  # noqa: F811
async def test_get_slot_from_game_id(cache_cls):
    slot = {
        'index': 0,
    }
    cache.lindex = AsyncMagicMock(return_value=cache_cls.dumps(slot))
    cache_cls._get_redis_instance = MagicMock(return_value=cache)

    assert await cache_cls.get_slot_from_game_id(0, 'game_id') == slot
    cache.lindex.assert_called_once_with('slots:game_id', 0)


@pytest.mark.asyncio  # noqa: F811
async def test_get_slot(cache):
    slot = {
        'index': 0,
    }
    cache.lindex = AsyncMagicMock(return_value=cache.dumps(slot))
    cache._get_redis_instance = MagicMock(return_value=cache)

    assert await cache.get_slot(0) == slot


@pytest.mark.asyncio  # noqa: F811
async def test_has_game_started(cache):
    cache._cache.hget = AsyncMagicMock(return_value=b'true')
    assert await cache.has_game_started()
    cache._cache.hget.assert_called_once_with('game:game_id', 'started')

    cache._cache.hget = AsyncMagicMock(return_value=b'false')
    assert not await cache.has_game_started()
    cache._cache.hget.assert_called_once_with('game:game_id', 'started')


@pytest.mark.asyncio  # noqa: F811
async def test_game_has_started(cache):
    cache._cache.hset = AsyncMagicMock()

    await cache.game_has_started()

    cache._cache.hset.assert_called_once_with('game:game_id', 'started', b'true')


@pytest.mark.asyncio  # noqa: F811
async def test_save_game(cache, game):
    cache._cache.hset = AsyncMagicMock()

    await cache.save_game(game)

    cache._cache.hset.assert_called_once_with('game:game_id', 'game', cache.dumps(game))