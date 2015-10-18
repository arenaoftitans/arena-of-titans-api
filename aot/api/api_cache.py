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

    # redis connection used by methods.
    _cache = redis.Redis(
        host=aot.config['cache']['server_host'],
        port=aot.config['cache']['server_port'])

    @classmethod
    def is_new_game(cls, game_id):
        return len(cls._get_players_ids(game_id)) == 0

    @classmethod
    def _get_players_ids(cls, game_id):
        ids = cls._cache.zrange(cls.PLAYERS_KEY_TEMPLATE.format(game_id), 0, -1)
        return [id.decode('utf-8') for id in ids]

    @classmethod
    def game_exists(cls, game_id):
        return cls._cache.hget(
            cls.GAME_KEY_TEMPLATE.format(game_id),
            cls.GAME_MASTER_KEY) is not None

    @classmethod
    def has_opened_slots(cls, game_id):
        return len(cls._get_opened_slots(game_id)) > 0

    @classmethod
    def _get_opened_slots(cls, game_id):
        slots = cls._get_slots(game_id)
        return [slot for slot in slots if slot['state'] == SlotState.OPEN.value]

    @classmethod
    def _get_slots(cls, game_id, include_player_id=True):
        raw_slots = cls._cache.lrange(cls.SLOTS_KEY_TEMPLATE.format(game_id), 0, -1)
        slots = [pickle.loads(slot) for slot in raw_slots]
        if not include_player_id:
            slots = cls._remove_player_id(slots)
        return slots

    @staticmethod
    def _remove_player_id(slots):
        corrected_slots = []
        for slot in slots:
            if 'player_id' in slot:
                del slot['player_id']
            corrected_slots.append(slot)
        return corrected_slots

    @classmethod
    def is_member_game(cls, game_id, player_id):
        return player_id in cls._get_players_ids(game_id)

    def __init__(self, game_id, player_id):
        self._cache = redis.Redis(
            host=aot.config['cache']['server_host'],
            port=aot.config['cache']['server_port'])
        self._game_id = game_id
        self._player_id = player_id

    def create_new_game(self):
        self._cache.hset(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.GAME_MASTER_KEY,
            self._player_id)
        self._cache.hset(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.STARTED_KEY,
            self.GAME_NOT_STARTED)
        self._init_first_slot()

    def _init_first_slot(self):
        slot = {
            'player_name': '',
            'player_id': self._player_id,
            'index': 0,
            'state': SlotState.OPEN.value
        }
        self.add_slot(slot)

    def add_slot(self, slot):
        if slot['state'] == SlotState.TAKEN.value:
            slot['player_id'] = self._player_id
        self._cache.rpush(self.SLOTS_KEY_TEMPLATE.format(self._game_id), pickle.dumps(slot))

    def get_game(self):
        game_data = self._cache.hget(self.GAME_KEY_TEMPLATE.format(self._game_id), self.GAME_KEY)
        return pickle.loads(game_data)

    def save_session(self, player_index):
        self._cache.zadd(
            self.PLAYERS_KEY_TEMPLATE.format(self._game_id),
            self._player_id, player_index)

    def get_players_ids(self):
        return ApiCache._get_players_ids(self._game_id)

    def get_slots(self, include_player_id=True):
        return ApiCache._get_slots(self._game_id, include_player_id=include_player_id)

    def get_player_index(self):
        slot = [slot for slot in self.get_slots() if slot['player_id'] == self._player_id][0]
        return slot['index']

    def is_game_master(self):
        game_master_id = self._cache.hget(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.GAME_MASTER_KEY).decode('utf-8')
        return game_master_id == self._player_id

    def number_taken_slots(self):
        return len(self._get_taken_slots())

    def _get_taken_slots(self,):
        slots = self.get_slots()
        return [slot for slot in slots if slot['state'] == SlotState.TAKEN.value]

    def affect_next_slot(self, player_name):
        opened_slots = ApiCache._get_opened_slots(self._game_id)
        next_available_slot = opened_slots[0]
        next_available_slot['player_id'] = self._player_id
        next_available_slot['state'] = SlotState.TAKEN.value
        next_available_slot['player_name'] = player_name
        self.update_slot(next_available_slot)

        return next_available_slot['index']

    def update_slot(self, slot):
        current_slot = self.get_slot(slot['index'])
        if current_slot.get('player_id', '') == self._player_id:
            slot['player_id'] = self._player_id
            self._save_slot(slot)
        elif self.is_game_master() and current_slot['state'] != SlotState.TAKEN.value:
            self._save_slot(slot)
        elif current_slot['state'] != SlotState.TAKEN.value and \
                slot['state'] == SlotState.TAKEN.value:
            slot['player_id'] = self._player_id
            self._save_slot(slot)

    def _save_slot(self, slot):
        self._cache.lset(
            self.SLOTS_KEY_TEMPLATE.format(self._game_id),
            slot['index'],
            pickle.dumps(slot))

    def slot_exists(self, slot):
        return self._get_raw_slot(slot['index'], self._game_id) is not None

    @classmethod
    def _get_raw_slot(cls, index, game_id):
        return cls._cache.lindex(cls.SLOTS_KEY_TEMPLATE.format(game_id), index)

    @classmethod
    def get_slot_from_game_id(cls, index, game_id):
        data = cls._get_raw_slot(index, game_id)
        return pickle.loads(data)

    def get_slot(self, index):
        data = self._get_raw_slot(index, self._game_id)
        return pickle.loads(data)

    def has_game_started(self):
        game_started = self._cache.hget(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.STARTED_KEY)
        return game_started == self.GAME_STARTED

    def game_has_started(self):
        self._cache.hset(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.STARTED_KEY,
            self.GAME_STARTED)

    def save_game(self, game):
        self._cache.hset(
            self.GAME_KEY_TEMPLATE.format(self._game_id),
            self.GAME_KEY,
            pickle.dumps(game))
