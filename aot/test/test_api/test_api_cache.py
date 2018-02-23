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

from copy import deepcopy
from unittest.mock import MagicMock

import pytest

from .. import (  # noqa: F401
    api_cache,
    api_cache_cls,
    AsyncMagicMock,
    game,
)
from ...api.api_cache import ApiCache


def test_connect_tcp_socket(mock):  # noqa: F811
    cfg = {
        'cache': {
            'host': '127.0.0.1',
            'port': '6379',
        },
    }
    redis = MagicMock()
    mock.patch('aot.api.api_cache.config', new=cfg)
    mock.patch('aot.api.api_cache.Redis', new=redis)

    ApiCache._get_redis_instance(new=True)

    redis.assert_called_once_with(host=cfg['cache']['host'], port=cfg['cache']['port'])


@pytest.mark.asyncio  # noqa: F811
async def test_test(api_cache, mock):
    now = MagicMock(return_value='the_date')
    datetime = MagicMock()
    datetime.now = now
    mock.patch('aot.api.api_cache.datetime', new=datetime)
    api_cache._cache.set = AsyncMagicMock()

    await api_cache.test()

    api_cache._cache.set.assert_called_once_with('test', 'the_date')


@pytest.mark.asyncio  # noqa: F811
async def test_info(api_cache, mock):
    api_cache._cache.keys = AsyncMagicMock(return_value=[b'game:game_id', b'toto'])
    api_cache.get_players_ids = AsyncMagicMock(return_value=['id1', 'id2'])
    api_cache._cache.hget = AsyncMagicMock(return_value=b'True')

    infos = await api_cache.info()

    api_cache._cache.keys.assert_called_once_with()
    assert infos == {
        'average_number_players': 2.0,
        'number_games': 1,
        'number_started_games': 1,
    }


@pytest.mark.asyncio  # noqa: F811
async def test_get_players_ids(api_cache):
    api_cache._cache.zrange = AsyncMagicMock(return_value=[b'id0', b'id1'])
    api_cache._game_id = None

    results = await api_cache.get_players_ids('game_id')

    assert results == ['id0', 'id1']
    api_cache._cache.zrange.assert_called_once_with('players:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_get_players_ids_without_game_id(api_cache):
    api_cache._cache.zrange = AsyncMagicMock(return_value=[b'id0', b'id1'])

    results = await api_cache.get_players_ids()

    assert results == ['id0', 'id1']
    api_cache._cache.zrange.assert_called_once_with('players:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_game_exists(api_cache, game):
    api_cache._cache.hget = AsyncMagicMock(return_value=None)
    assert not await api_cache.game_exists('game_id')
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')

    api_cache._cache.hget = AsyncMagicMock(return_value=game)
    assert await api_cache.game_exists('game_id')
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')


@pytest.mark.asyncio  # noqa: F811
async def test_has_opened_slots(mock, api_cache):
    api_cache._cache.lrange = AsyncMagicMock(return_value=[{'state': 'OPEN'}, {'state': 'CLOSED'}])

    assert await api_cache.has_opened_slots('game_id')
    api_cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_get_slots_with_game_id(mock, api_cache):
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
    api_cache._cache.lrange = AsyncMagicMock(return_value=deepcopy(slots))

    results = await api_cache.get_slots('game_id')

    assert results == slots
    api_cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_get_slots_without_game_id(mock, api_cache):
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
    api_cache._cache.lrange = AsyncMagicMock(return_value=deepcopy(slots))

    results = await api_cache.get_slots()

    assert results == slots
    api_cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_get_slots_exclude_player_ids(api_cache):
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
    api_cache._cache.lrange = AsyncMagicMock(return_value=deepcopy(slots))
    for slot in slots:
        del slot['player_id']

    results = await api_cache.get_slots('game_id', include_player_id=False)

    assert results == slots
    api_cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


@pytest.mark.asyncio  # noqa: F811
async def test_is_member_game(api_cache):
    api_cache._cache.zrange = AsyncMagicMock(return_value=[b'id0', b'id1'])

    assert await api_cache.is_member_game('game_id', 'id0')
    assert not await api_cache.is_member_game('game_id', 'id100')


@pytest.mark.asyncio  # noqa: F811
async def test_create_new_game(api_cache):
    slots = []

    def add_slot_cache_side_effect(key, slot):
        assert key == 'slots:game_id'
        assert slot['index'] == len(slots)
        if len(slots) == 0:
            assert slot['player_id'] == 'player_id'
        else:
            assert not slot['player_id']

        slots.append(slot)

    api_cache._cache.rpush = AsyncMagicMock(side_effect=add_slot_cache_side_effect)
    api_cache._cache.hset = AsyncMagicMock()
    api_cache._cache.expire = AsyncMagicMock()
    api_cache.get_slots = AsyncMagicMock(return_value=slots)

    await api_cache.create_new_game()

    assert api_cache._cache.hset.call_count == 3
    assert api_cache._cache.rpush.call_count == 8
    assert api_cache._cache.expire.call_count == 2
    assert api_cache.get_slots.call_count == 8


@pytest.mark.asyncio  # noqa: F811
async def test_is_test(api_cache):
    api_cache._cache.hget = AsyncMagicMock(return_value=b'True')
    assert await api_cache.is_test()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'test')

    api_cache._cache.hget = AsyncMagicMock(return_value=b'False')
    assert not await api_cache.is_test()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'test')


@pytest.mark.asyncio  # noqa: F811
async def test_get_game(api_cache, game):
    api_cache._cache.hget = AsyncMagicMock(return_value=game)
    assert await api_cache.get_game() == game
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game')

    api_cache._cache.hget = AsyncMagicMock(return_value=None)
    assert await api_cache.get_game() is None
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game')


@pytest.mark.asyncio  # noqa: F811
async def test_save_session(api_cache):
    api_cache._cache.zadd = AsyncMagicMock()
    api_cache._cache.expire = AsyncMagicMock()

    await api_cache.save_session(1)

    api_cache._cache.zadd.assert_called_once_with('players:game_id', 1, 'player_id')
    api_cache._cache.expire.call_count == 1


@pytest.mark.asyncio  # noqa: F811
async def test_get_player_index(api_cache):
    slots = [
        {
            'player_id': 'player_id',
            'index': 0,
        },
    ]
    api_cache.get_slots = AsyncMagicMock(return_value=deepcopy(slots))

    assert await api_cache.get_player_index() == 0


@pytest.mark.asyncio  # noqa: F811
async def test_is_game_master(api_cache):
    api_cache._cache.hget = AsyncMagicMock(return_value=b'player_id')
    assert await api_cache.is_game_master()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')

    api_cache._cache.hget = AsyncMagicMock(return_value=b'toto')
    assert not await api_cache.is_game_master()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')

    api_cache._cache.hget = AsyncMagicMock(return_value=None)
    assert not await api_cache.is_game_master()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')


@pytest.mark.asyncio  # noqa: F811
async def test_number_taken_slots(api_cache):
    slots = [{'state': 'TAKEN'}, {'state': 'OPEN'}, {'state': 'AI'}]
    api_cache.get_slots = AsyncMagicMock(return_value=deepcopy(slots))
    assert await api_cache.number_taken_slots() == 2


@pytest.mark.asyncio  # noqa: F811
async def test_affect_next_slot(api_cache):
    slots = [{'state': 'TAKEN'}, {'state': 'OPEN', 'index': 1}, {'state': 'AI'}]
    api_cache.get_slots = AsyncMagicMock(return_value=deepcopy(slots))
    api_cache.update_slot = AsyncMagicMock()
    slot = slots[1]
    slot['player_id'] = 'player_id'
    slot['state'] = 'TAKEN'
    slot['player_name'] = 'Player'
    slot['hero'] = 'daemon'

    assert await api_cache.affect_next_slot('Player', 'daemon') == 1
    api_cache.update_slot.assert_called_once_with(slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_free(api_cache):
    cache_slot = {
        'state': 'TAKEN',
        'player_id': 'player_id',
        'index': 0,
    }
    api_cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = AsyncMagicMock()
    slot = {
        'player_id': 'player_id',
        'index': 0,
        'state': 'OPEN',
    }
    del cache_slot['player_id']
    cache_slot['state'] = 'OPEN'

    await api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_close(api_cache):
    cache_slot = {
        'state': 'AI',
        'player_name': 'AI 2',
        'index': 0,
    }
    api_cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = AsyncMagicMock()
    api_cache.is_game_master = AsyncMagicMock(return_value=True)
    slot = {
        'index': 0,
        'state': 'CLOSED',
        'player_name': 'AI 2',
    }
    del cache_slot['player_name']
    cache_slot['state'] = 'CLOSED'

    await api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_open(api_cache):
    cache_slot = {
        'state': 'AI',
        'player_name': 'AI 2',
        'index': 0,
    }
    api_cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = AsyncMagicMock()
    api_cache.is_game_master = AsyncMagicMock(return_value=True)
    slot = {
        'index': 0,
        'state': 'OPEN',
        'player_name': 'AI 2',
    }
    del cache_slot['player_name']
    cache_slot['state'] = 'OPEN'

    await api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_update_not_game_master(api_cache):
    cache_slot = {
        'state': 'TAKEN',
        'player_id': 'player_id',
        'index': 0,
    }
    api_cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = AsyncMagicMock()
    slot = {
        'player_id': 'player_id',
        'hero': 'daemon',
        'index': 0,
        'state': 'TAKEN',
    }
    cache_slot['hero'] = 'daemon'

    await api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_update_game_master(api_cache):
    cache_slot = {
        'state': 'OPEN',
        'index': 0,
    }
    api_cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = AsyncMagicMock()
    api_cache.is_game_master = AsyncMagicMock(return_value=True)
    slot = {
        'state': 'AI',
        'index': 0,
    }
    cache_slot['state'] = 'AI'

    await api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_update_game_master_taken(api_cache):
    cache_slot = {
        'state': 'TAKEN',
        'index': 0,
    }
    api_cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = AsyncMagicMock()
    api_cache.is_game_master = AsyncMagicMock(return_value=True)
    slot = {
        'state': 'AI',
        'index': 0,
    }
    cache_slot['state'] = 'AI'

    await api_cache.update_slot(slot)

    assert api_cache._save_slot.call_count == 0


@pytest.mark.asyncio  # noqa: F811
async def test_update_slot_take(api_cache):
    cache_slot = {
        'state': 'OPEN',
        'index': 0,
    }
    api_cache.get_slot = AsyncMagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = AsyncMagicMock()
    slot = {
        'state': 'TAKEN',
        'player_id': 'player_id',
        'index': 0,
    }
    cache_slot['player_id'] = 'player_id'
    cache_slot['state'] = 'TAKEN'

    await api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


@pytest.mark.asyncio  # noqa: F811
async def test_save_slot(api_cache):
    slot = {
        'state': 'TAKEN',
        'index': 0,
    }
    api_cache._cache.lset = AsyncMagicMock()

    await api_cache._save_slot(slot)

    api_cache._cache.lset.assert_called_once_with('slots:game_id', 0, slot)


@pytest.mark.asyncio  # noqa: F811
async def test_slot_exists(api_cache):
    slot = {
        'index': 0,
    }
    cache = MagicMock()
    cache.lindex = AsyncMagicMock(return_value=None)
    api_cache._get_redis_instance = MagicMock(return_value=cache)
    assert not await api_cache.slot_exists(slot)
    cache.lindex.assert_called_once_with('slots:game_id', 0)

    cache = MagicMock()
    cache.lindex = AsyncMagicMock(return_value=slot)
    api_cache._get_redis_instance = MagicMock(return_value=cache)
    assert await api_cache.slot_exists(slot)
    cache.lindex.assert_called_once_with('slots:game_id', 0)


@pytest.mark.asyncio  # noqa: F811
async def test_get_slot_from_game_id(api_cache_cls):
    slot = {
        'index': 0,
    }
    cache = MagicMock()
    cache.lindex = AsyncMagicMock(return_value=slot)
    api_cache_cls._get_redis_instance = MagicMock(return_value=cache)

    assert await api_cache_cls.get_slot_from_game_id(0, 'game_id') == slot
    cache.lindex.assert_called_once_with('slots:game_id', 0)


@pytest.mark.asyncio  # noqa: F811
async def test_get_slot(api_cache):
    slot = {
        'index': 0,
    }
    cache = MagicMock()
    cache.lindex = AsyncMagicMock(return_value=slot)
    api_cache._get_redis_instance = MagicMock(return_value=cache)

    assert await api_cache.get_slot(0) == slot


@pytest.mark.asyncio  # noqa: F811
async def test_has_game_started(api_cache):
    api_cache._cache.hget = AsyncMagicMock(return_value=b'true')
    assert await api_cache.has_game_started()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'started')

    api_cache._cache.hget = AsyncMagicMock(return_value=b'false')
    assert not await api_cache.has_game_started()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'started')


@pytest.mark.asyncio  # noqa: F811
async def test_game_has_started(api_cache):
    api_cache._cache.hset = AsyncMagicMock()

    await api_cache.game_has_started()

    api_cache._cache.hset.assert_called_once_with('game:game_id', 'started', b'true')


@pytest.mark.asyncio  # noqa: F811
async def test_save_game(api_cache, game):
    api_cache._cache.hset = AsyncMagicMock()

    await api_cache.save_game(game)

    api_cache._cache.hset.assert_called_once_with('game:game_id', 'game', game)
