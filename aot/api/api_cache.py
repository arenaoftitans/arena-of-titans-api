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

import pickle

from copy import deepcopy
from datetime import datetime

from aredis import StrictRedis as Redis

from .utils import SlotState
from .. import get_number_players
from ..config import config


class ApiCache:
    GAME_KEY_TEMPLATE = 'game:{}'
    PLAYERS_KEY_TEMPLATE = 'players:{}'
    SLOTS_KEY_TEMPLATE = 'slots:{}'

    GAME_MASTER_KEY = 'game_master'
    GAME_KEY = 'game'
    STARTED_KEY = 'started'
    TEST_KEY = 'test'

    GAME_STARTED = b'true'
    GAME_NOT_STARTED = b'false'
    #: Time in seconds after which the game is deleted (48h).
    GAME_EXPIRE = 2 * 24 * 60 * 60
    _cache = None

    # Instance variables
    _game_id = ''
    _player_id = ''

    @classmethod
    def _get_redis_instance(cls, new=False):
        if new:
            socket = config['cache'].get('socket', None)
            if socket:
                kwargs = {
                    'unix_socket_path': socket,
                }
            else:
                kwargs = {
                    'host': config['cache']['host'],
                    'port': config['cache']['port'],
                }
            return Redis(**kwargs)
        else:  # pragma: no cover
            if cls._cache is None:
                cls._cache = cls._get_redis_instance(new=True)
            return cls._cache

    def __init__(self):
        self._cache = self._get_redis_instance(new=True)

    async def test(self):
        await self._cache.set(self.TEST_KEY, str(datetime.now()))

    async def info(self):
        infos = {}
        for key in await self._cache.keys():
            key = key.decode('utf-8')
            if key.startswith('game:'):
                _, game_id = key.split(':')
                self._game_id = game_id
                infos['number_games'] = infos.get('number_games', 0) + 1
                infos['average_number_players'] = \
                    infos.get('average_number_players', 0) + \
                    len(await self.get_players_ids(game_id))
                if self.has_game_started:
                    infos['number_started_games'] = infos.get('number_started_games', 0) + 1

        infos['average_number_players'] = \
            infos.get('average_number_players', 0) / infos.get('number_games', 1)
        return infos

    def init(self, game_id=None, player_id=None):
        self._game_id = game_id
        self._player_id = player_id

    async def get_players_ids(self, game_id=None):
        if game_id is None:
            game_id = self._game_id
        ids = await self._cache.zrange(self.PLAYERS_KEY_TEMPLATE.format(game_id), 0, -1)
        return [id.decode('utf-8') for id in ids]

    async def game_exists(self, game_id):
        return await self._cache.hget(
            self.GAME_KEY_TEMPLATE.format(game_id),
            self.GAME_MASTER_KEY) is not None

    async def has_opened_slots(self, game_id):
        return len(await self._get_opened_slots(game_id)) > 0

    async def _get_opened_slots(self, game_id):
        slots = await self.get_slots(game_id=game_id)
        return [slot for slot in slots if slot['state'] == SlotState.OPEN]

    async def get_slots(self, game_id=None, include_player_id=True):
        if game_id is None:
            game_id = self._game_id
        raw_slots = await self._cache.lrange(self.SLOTS_KEY_TEMPLATE.format(game_id), 0, -1)
        slots = [pickle.loads(slot) for slot in raw_slots]
        if not include_player_id:
            slots = self._remove_player_id(slots)
        return slots

    def _remove_player_id(self, slots):
        corrected_slots = []
        for slot in slots:
            if 'player_id' in slot:
                del slot['player_id']
            corrected_slots.append(slot)
        return corrected_slots

    async def is_member_game(self, game_id, player_id):
        return player_id in await self.get_players_ids(game_id)

    async def create_new_game(self, test=False):
        await self._cache.hset(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.GAME_MASTER_KEY,
            self._player_id)
        await self._cache.hset(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.STARTED_KEY,
            self.GAME_NOT_STARTED)
        await self._cache.hset(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            'test',
            test)
        await self._init_slots()
        await self._cache.expire(self.SLOTS_KEY_TEMPLATE.format(self._game_id), self.GAME_EXPIRE)
        await self._cache.expire(self.GAME_KEY_TEMPLATE.format(self._game_id), self.GAME_EXPIRE)

    async def _init_slots(self):
        slot = {
            'player_name': '',
            'player_id': self._player_id,
            'index': 0,
            'state': SlotState.OPEN,
        }
        await self._add_slot(slot)

        slot['player_id'] = ''
        index = 0
        while not await self._max_number_slots_reached():
            index += 1
            slot['index'] = index
            await self._add_slot(slot)

    async def _add_slot(self, slot):
        slot = deepcopy(slot)
        await self._cache.rpush(self.SLOTS_KEY_TEMPLATE.format(self._game_id), pickle.dumps(slot))

    async def _max_number_slots_reached(self):
        return len(await self.get_slots()) == get_number_players()

    async def is_test(self):
        value = await self._cache.hget(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            'test')
        return value.decode('utf-8') == 'True'

    async def get_game(self):
        game_data = await self._cache.hget(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.GAME_KEY,
        )
        if game_data:
            return pickle.loads(game_data)

    async def save_session(self, player_index):
        await self._cache.zadd(
            self.PLAYERS_KEY_TEMPLATE.format(self._game_id),
            player_index,
            self._player_id,
        )
        await self._cache.expire(self.PLAYERS_KEY_TEMPLATE.format(self._game_id), self.GAME_EXPIRE)

    async def get_player_index(self):
        slot = [slot for slot in await self.get_slots()
                if slot.get('player_id', None) == self._player_id][0]
        return slot['index']

    async def is_game_master(self):
        game_master_id = await self._cache.hget(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.GAME_MASTER_KEY,
        )
        return game_master_id is not None and game_master_id.decode('utf-8') == self._player_id

    async def number_taken_slots(self):
        return len(await self._get_taken_slots())

    async def _get_taken_slots(self,):
        slots = await self.get_slots()
        return [slot for slot in slots
                if slot['state'] in (SlotState.TAKEN, SlotState.AI)]

    async def affect_next_slot(self, player_name, hero):
        opened_slots = await self._get_opened_slots(self._game_id)
        next_available_slot = opened_slots[0]
        next_available_slot['player_id'] = self._player_id
        next_available_slot['state'] = SlotState.TAKEN
        next_available_slot['player_name'] = player_name
        next_available_slot['hero'] = hero
        await self.update_slot(next_available_slot)

        return next_available_slot['index']

    async def update_slot(self, slot):
        current_slot = await self.get_slot(slot['index'])
        if current_slot['state'] == SlotState.OPEN and slot['state'] == SlotState.TAKEN:
            slot['player_id'] = self._player_id
            await self._save_slot(slot)
        elif current_slot.get('player_id', '') == self._player_id:
            # If new value is OPEN, we are freeing the slot and mustn't add the player id.
            if slot['state'] != SlotState.OPEN:
                slot['player_id'] = self._player_id
            elif 'player_id' in slot:
                del slot['player_id']
            await self._save_slot(slot)
        elif await self.is_game_master() and current_slot['state'] != SlotState.TAKEN:
            # If we are closing the slot, we remove the name of the previous player.
            if slot['state'] in (SlotState.CLOSED, SlotState.OPEN) and 'player_name' in slot:
                del slot['player_name']

            await self._save_slot(slot)

    async def _save_slot(self, slot):
        await self._cache.lset(
            self.SLOTS_KEY_TEMPLATE.format(self._game_id),
            slot['index'],
            pickle.dumps(slot))

    async def slot_exists(self, slot):
        return await self._get_raw_slot(slot['index'], self._game_id) is not None

    async def _get_raw_slot(self, index, game_id):
        # This method is used in class methods, therefore, we must rely on
        # _get_redis_instance to get the proper cache object
        cache = self._get_redis_instance()
        return await cache.lindex(self.SLOTS_KEY_TEMPLATE.format(game_id), index)

    @classmethod
    async def get_slot_from_game_id(cls, index, game_id):
        data = await cls._get_raw_slot(cls, index, game_id)
        return pickle.loads(data)

    async def get_slot(self, index):
        data = await self._get_raw_slot(index, self._game_id)
        return pickle.loads(data)

    async def has_game_started(self):
        game_started = await self._cache.hget(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.STARTED_KEY,
        )
        return game_started == self.GAME_STARTED

    async def game_has_started(self):
        await self._cache.hset(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.STARTED_KEY,
            self.GAME_STARTED,
        )

    async def save_game(self, game):
        await self._cache.hset(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.GAME_KEY,
            pickle.dumps(game),
        )
