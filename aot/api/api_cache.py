import pickle
import redis

import aot
from aot.api.utils import SlotState


class ApiCache:
    BOARD_KEY_TEMPLATE = 'board:{}'
    GAME_KEY_TEMPLATE = 'game:{}'
    PLAYERS_KEY_TEMPLATE = 'players:{}'
    SLOTS_KEY_TEMPLATE = 'slots:{}'

    GAME_MASTER_KEY = 'game_master'
    GAME_KEY = 'game'
    STARTED_KEY = 'started'

    GAME_STARTED = b'true'
    GAME_NOT_STARTED = b'false'
    #: Time in seconds after which the game is deleted (48h).
    GAME_EXPIRE = 2*24*60*60

    _cache = redis.Redis(host=aot.config['cache']['server_host'], port=aot.config['cache']['server_port'])

    def get_game(self, game_id):
        game_data = self._cache.hget(self.GAME_KEY_TEMPLATE.format(game_id), self.GAME_KEY)
        return pickle.loads(game_data)
    
    def save_session(self, game_id, session_id, player_index):
        self._cache.zadd(self.PLAYERS_KEY_TEMPLATE.format(game_id), session_id, player_index)

    def remove_session_id(self, game_id, session_id):
        self._cache.zrem(self.PLAYERS_KEY_TEMPLATE.format(game_id), session_id)

    def get_players_ids(self, game_id):
        return [id.decode('utf-8') for id in self._cache.zrange(self.PLAYERS_KEY_TEMPLATE.format(game_id), 0, -1)]

    def has_opened_slots(self, game_id):
        return len(self._get_opened_slots(game_id)) > 0

    def is_new_game(self, game_id):
        return len(self.get_players_ids(game_id)) == 0

    def is_game_master(self, game_id, session_id):
        return self._cache.hget(self.GAME_KEY_TEMPLATE.format(game_id), self.GAME_MASTER_KEY).decode('utf-8') ==\
            session_id

    def init(self, game_id, session_id):
        self._cache.hset(
            self.GAME_KEY_TEMPLATE.format(game_id),
            self.GAME_MASTER_KEY,
            session_id)
        self._cache.hset(
            self.GAME_KEY_TEMPLATE.format(game_id),
            self.STARTED_KEY,
            self.GAME_NOT_STARTED)
        self._init_first_slot(game_id, session_id)

    def _init_first_slot(self, game_id, session_id):
        slot = {
            'player_name': '',
            'player_id': session_id,
            'index': 0,
            'state': SlotState.OPEN.value
        }
        self.add_slot(game_id, slot)

    def add_slot(self, game_id, slot):
        self._cache.rpush(self.SLOTS_KEY_TEMPLATE.format(game_id), pickle.dumps(slot))

    def game_exists(self, game_id):
        return self._cache.hget(
            self.GAME_KEY_TEMPLATE.format(game_id),
            self.GAME_MASTER_KEY) is not None

    def affect_next_slot(self, game_id, session_id, player_name):
        opened_slots = self._get_opened_slots(game_id)
        next_available_slot = opened_slots[0]
        next_available_slot['player_id'] = session_id
        next_available_slot['state'] = SlotState.TAKEN.value
        next_available_slot['player_name'] = player_name
        self.update_slot(game_id, session_id, next_available_slot)

        return next_available_slot['index']
    
    def _get_opened_slots(self, game_id):
        slots = self.get_slots(game_id)
        return [slot for slot in slots if slot['state'] == SlotState.OPEN.value]

    def get_slots(self, game_id, include_player_id=True):
        slots = [pickle.loads(slot) for slot in self._cache.lrange(self.SLOTS_KEY_TEMPLATE.format(game_id), 0, -1)]
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

    def update_slot(self, game_id, session_id, slot):
        current_slot = self.get_slot(game_id, slot['index'])
        if current_slot.get('player_id', '') == session_id:
            slot['player_id'] = session_id
            self._save_slot(game_id, slot)
        elif self.is_game_master(game_id, session_id) and current_slot['state'] != SlotState.TAKEN.value:
            self._save_slot(game_id, slot)
        elif current_slot['state'] != SlotState.TAKEN.value and slot['state'] == SlotState.TAKEN.value:
            slot['player_id'] = session_id
            self._save_slot(game_id, slot)

    def get_slot(self, game_id, index):
        data = self._cache.lindex(self.SLOTS_KEY_TEMPLATE.format(game_id), index)
        return pickle.loads(data)

    def _save_slot(self, game_id, slot):
        self._cache.lset(self.SLOTS_KEY_TEMPLATE.format(game_id), slot['index'], pickle.dumps(slot))

    def has_game_started(self, game_id):
        return self._cache.hget(self.GAME_KEY_TEMPLATE.format(game_id), self.STARTED_KEY) == \
            self.GAME_STARTED

    def game_has_started(self, game_id):
        self._cache.hset(self.GAME_KEY_TEMPLATE.format(game_id), self.STARTED_KEY, self.GAME_STARTED)

    def save_game(self, game, game_id):
        self._cache.hset(self.GAME_KEY_TEMPLATE.format(game_id), self.GAME_KEY, pickle.dumps(game))
