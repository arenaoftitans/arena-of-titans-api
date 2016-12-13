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

import pickle

from aot.config import config
from aot.api.api_cache import ApiCache
from aot.test import (
    api_cache,
    api_cache_cls,
    game,
)
from copy import deepcopy
from unittest.mock import MagicMock


def setup_module():
    config.load_config('dev')


def test_connect_unix_socket(mock):
    cfg = {
        'cache': {
            'socket': '/var/run/redis/aot-api-staging-latest.sock',
            'host': '127.0.0.1',
            'server_port': '6379',
        }
    }
    redis = MagicMock()
    mock.patch('aot.api.api_cache.config', new=cfg)
    mock.patch('aot.api.api_cache.Redis', new=redis)

    ApiCache._get_redis_instance(new=True)

    redis.assert_called_once_with(unix_socket_path=cfg['cache']['socket'])


def test_connect_tcp_socket(mock):
    cfg = {
        'cache': {
            'host': '127.0.0.1',
            'port': '6379',
        }
    }
    redis = MagicMock()
    mock.patch('aot.api.api_cache.config', new=cfg)
    mock.patch('aot.api.api_cache.Redis', new=redis)

    ApiCache._get_redis_instance(new=True)

    redis.assert_called_once_with(host=cfg['cache']['host'], port=cfg['cache']['port'])


def test_test(api_cache, mock):
    now = MagicMock(return_value='the_date')
    datetime = MagicMock()
    datetime.now = now
    mock.patch('aot.api.api_cache.datetime', new=datetime)
    api_cache._cache.set = MagicMock()

    api_cache.test()

    api_cache._cache.set.assert_called_once_with('test', 'the_date')


def test_info(api_cache, mock):
    api_cache._cache.keys = MagicMock(return_value=[b'game:game_id', b'toto'])
    api_cache.get_players_ids = MagicMock(return_value=['id1', 'id2'])
    api_cache._cache.hget = MagicMock(return_value=b'True')

    infos = api_cache.info()

    api_cache._cache.keys.assert_called_once_with()
    assert infos == {
        'average_number_players': 2.0,
        'number_games': 1,
        'number_started_games': 1,
    }


def test_get_players_ids(api_cache):
    api_cache._cache.zrange = MagicMock(return_value=[b'id0', b'id1'])
    api_cache._game_id = None

    assert api_cache.get_players_ids('game_id') == ['id0', 'id1']

    api_cache._cache.zrange.assert_called_once_with('players:game_id', 0, -1)


def test_get_players_ids_without_game_id(api_cache):
    api_cache._cache.zrange = MagicMock(return_value=[b'id0', b'id1'])

    assert api_cache.get_players_ids() == ['id0', 'id1']

    api_cache._cache.zrange.assert_called_once_with('players:game_id', 0, -1)


def test_game_exists(api_cache, game):
    api_cache._cache.hget = MagicMock(return_value=None)
    assert not api_cache.game_exists('game_id')
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')

    api_cache._cache.hget = MagicMock(return_value=game)
    assert api_cache.game_exists('game_id')
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')


def test_has_opened_slots(mock, api_cache):
    api_cache._cache.lrange = MagicMock(return_value=[{'state': 'OPEN'}, {'state': 'CLOSED'}])

    assert api_cache.has_opened_slots('game_id')
    api_cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


def test_get_slots_with_game_id(mock, api_cache):
    slots = [
        {
            'state': 'OPEN',
            'player_id': 'id0',
        },
        {
            'state': 'CLOSED',
            'player_id': 'id1',
        }
    ]
    api_cache._cache.lrange = MagicMock(return_value=deepcopy(slots))

    assert api_cache.get_slots('game_id') == slots
    api_cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


def test_get_slots_without_game_id(mock, api_cache):
    slots = [
        {
            'state': 'OPEN',
            'player_id': 'id0',
        },
        {
            'state': 'CLOSED',
            'player_id': 'id1',
        }
    ]
    api_cache._cache.lrange = MagicMock(return_value=deepcopy(slots))

    assert api_cache.get_slots() == slots
    api_cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


def test_get_slots_exclude_player_ids(api_cache):
    slots = [
        {
            'state': 'OPEN',
            'player_id': 'id0',
        },
        {
            'state': 'CLOSED',
            'player_id': 'id1',
        }
    ]
    api_cache._cache.lrange = MagicMock(return_value=deepcopy(slots))
    for slot in slots:
        del slot['player_id']

    assert api_cache.get_slots('game_id', include_player_id=False) == slots
    api_cache._cache.lrange.assert_called_once_with('slots:game_id', 0, -1)


def test_is_member_game(api_cache):
    api_cache._cache.zrange = MagicMock(return_value=[b'id0', b'id1'])

    assert api_cache.is_member_game('game_id', 'id0')
    assert not api_cache.is_member_game('game_id', 'id100')


def test_create_new_game(api_cache):
    slots = []

    def add_slot_cache_side_effect(key, slot):
        assert key == 'slots:game_id'
        assert slot['index'] == len(slots)
        if len(slots) == 0:
            assert slot['player_id'] == 'player_id'
        else:
            assert not slot['player_id']

        slots.append(slot)

    api_cache._cache.rpush = MagicMock(side_effect=add_slot_cache_side_effect)
    api_cache.get_slots = MagicMock(return_value=slots)

    api_cache.create_new_game()

    assert api_cache._cache.hset.call_count == 3
    assert api_cache._cache.rpush.call_count == 8


def test_is_test(api_cache):
    api_cache._cache.hget = MagicMock(return_value=b'True')
    assert api_cache.is_test()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'test')

    api_cache._cache.hget = MagicMock(return_value=b'False')
    assert not api_cache.is_test()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'test')


def test_get_game(api_cache, game):
    api_cache._cache.hget = MagicMock(return_value=game)
    assert api_cache.get_game() == game
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game')

    api_cache._cache.hget = MagicMock(return_value=None)
    assert api_cache.get_game() is None
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game')


def test_save_session(api_cache):
    api_cache.save_session(1)

    api_cache._cache.zadd.assert_called_once_with('players:game_id', 'player_id', 1)


def test_get_player_index(api_cache):
    slots = [
        {
            'player_id': 'player_id',
            'index': 0,
        },
    ]
    api_cache.get_slots = MagicMock(return_value=deepcopy(slots))

    assert api_cache.get_player_index() == 0


def test_is_game_master(api_cache):
    api_cache._cache.hget = MagicMock(return_value=b'player_id')
    assert api_cache.is_game_master()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')

    api_cache._cache.hget = MagicMock(return_value=b'toto')
    assert not api_cache.is_game_master()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')

    api_cache._cache.hget = MagicMock(return_value=None)
    assert not api_cache.is_game_master()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'game_master')


def test_number_taken_slots(api_cache):
    slots = [{'state': 'TAKEN'}, {'state': 'OPEN'}, {'state': 'AI'}]
    api_cache.get_slots = MagicMock(return_value=deepcopy(slots))
    assert api_cache.number_taken_slots() == 2


def test_affect_next_slot(api_cache):
    slots = [{'state': 'TAKEN'}, {'state': 'OPEN', 'index': 1}, {'state': 'AI'}]
    api_cache.get_slots = MagicMock(return_value=deepcopy(slots))
    api_cache.update_slot = MagicMock()
    slot = slots[1]
    slot['player_id'] = 'player_id'
    slot['state'] = 'TAKEN'
    slot['player_name'] = 'Player'
    slot['hero'] = 'daemon'

    assert api_cache.affect_next_slot('Player', 'daemon') == 1
    api_cache.update_slot.assert_called_once_with(slot)


def test_update_slot_free(api_cache):
    cache_slot = {
        'state': 'TAKEN',
        'player_id': 'player_id',
        'index': 0,
    }
    api_cache.get_slot = MagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = MagicMock()
    slot = {
        'player_id': 'player_id',
        'index': 0,
        'state': 'OPEN',
    }
    del cache_slot['player_id']
    cache_slot['state'] = 'OPEN'

    api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


def test_update_slot_close(api_cache):
    cache_slot = {
        'state': 'AI',
        'player_name': 'AI 2',
        'index': 0,
    }
    api_cache.get_slot = MagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = MagicMock()
    api_cache.is_game_master = MagicMock(return_value=True)
    slot = {
        'index': 0,
        'state': 'CLOSED',
        'player_name': 'AI 2',
    }
    del cache_slot['player_name']
    cache_slot['state'] = 'CLOSED'

    api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


def test_update_slot_open(api_cache):
    cache_slot = {
        'state': 'AI',
        'player_name': 'AI 2',
        'index': 0,
    }
    api_cache.get_slot = MagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = MagicMock()
    api_cache.is_game_master = MagicMock(return_value=True)
    slot = {
        'index': 0,
        'state': 'OPEN',
        'player_name': 'AI 2',
    }
    del cache_slot['player_name']
    cache_slot['state'] = 'OPEN'

    api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


def test_update_slot_update_not_game_master(api_cache):
    cache_slot = {
        'state': 'TAKEN',
        'player_id': 'player_id',
        'index': 0,
    }
    api_cache.get_slot = MagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = MagicMock()
    slot = {
        'player_id': 'player_id',
        'hero': 'daemon',
        'index': 0,
        'state': 'TAKEN',
    }
    cache_slot['hero'] = 'daemon'

    api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


def test_update_slot_update_game_master(api_cache):
    cache_slot = {
        'state': 'OPEN',
        'index': 0,
    }
    api_cache.get_slot = MagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = MagicMock()
    api_cache.is_game_master = MagicMock(return_value=True)
    slot = {
        'state': 'AI',
        'index': 0,
    }
    cache_slot['state'] = 'AI'

    api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


def test_update_slot_update_game_master_taken(api_cache):
    cache_slot = {
        'state': 'TAKEN',
        'index': 0,
    }
    api_cache.get_slot = MagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = MagicMock()
    api_cache.is_game_master = MagicMock(return_value=True)
    slot = {
        'state': 'AI',
        'index': 0,
    }
    cache_slot['state'] = 'AI'

    api_cache.update_slot(slot)

    assert api_cache._save_slot.call_count == 0


def test_update_slot_take(api_cache):
    cache_slot = {
        'state': 'OPEN',
        'index': 0,
    }
    api_cache.get_slot = MagicMock(return_value=deepcopy(cache_slot))
    api_cache._save_slot = MagicMock()
    slot = {
        'state': 'TAKEN',
        'player_id': 'player_id',
        'index': 0,
    }
    cache_slot['player_id'] = 'player_id'
    cache_slot['state'] = 'TAKEN'

    api_cache.update_slot(slot)

    api_cache._save_slot.assert_called_once_with(cache_slot)


def test_save_slot(api_cache):
    slot = {
        'state': 'TAKEN',
        'index': 0,
    }

    api_cache._save_slot(slot)

    api_cache._cache.lset.assert_called_once_with('slots:game_id', 0, slot)


def test_slot_exists(api_cache):
    slot = {
        'index': 0,
    }
    cache = MagicMock()
    cache.lindex = MagicMock(return_value=None)
    api_cache._get_redis_instance = MagicMock(return_value=cache)
    assert not api_cache.slot_exists(slot)
    cache.lindex.assert_called_once_with('slots:game_id', 0)

    cache = MagicMock()
    cache.lindex = MagicMock(return_value=slot)
    api_cache._get_redis_instance = MagicMock(return_value=cache)
    assert api_cache.slot_exists(slot)
    cache.lindex.assert_called_once_with('slots:game_id', 0)


def test_get_slot_from_game_id(api_cache_cls):
    slot = {
        'index': 0,
    }
    cache = MagicMock()
    cache.lindex = MagicMock(return_value=slot)
    api_cache_cls._get_redis_instance = MagicMock(return_value=cache)

    assert api_cache_cls.get_slot_from_game_id(0, 'game_id') == slot
    cache.lindex.assert_called_once_with('slots:game_id', 0)


def test_get_slot(api_cache):
    slot = {
        'index': 0,
    }
    cache = MagicMock()
    cache.lindex = MagicMock(return_value=slot)
    api_cache._get_redis_instance = MagicMock(return_value=cache)

    assert api_cache.get_slot(0) == slot


def test_has_game_started(api_cache):
    api_cache._cache.hget = MagicMock(return_value=b'true')
    assert api_cache.has_game_started()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'started')

    api_cache._cache.hget = MagicMock(return_value=b'false')
    assert not api_cache.has_game_started()
    api_cache._cache.hget.assert_called_once_with('game:game_id', 'started')


def test_game_has_started(api_cache):
    api_cache.game_has_started()

    api_cache._cache.hset.assert_called_once_with('game:game_id', 'started', b'true')


def test_save_game(api_cache, game):
    api_cache.save_game(game)

    api_cache._cache.hset.assert_called_once_with('game:game_id', 'game', game)
