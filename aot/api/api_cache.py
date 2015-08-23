import pickle
import redis

from aot.api.utils import SlotState


class ApiCache:
    BOARD_KEY_TEMPLATE = 'board:{}'
    GAME_KEY_TEMPLATE = 'game:{}'
    PLAYERS_KEY_TEMPLATE = 'players:{}'
    SLOTS_KEY_TEMPLATE = 'slots:{}'

    GAME_MASTER_KEY = 'game_master'
    GAME_KEY = 'game'
    STARTED_KEY = 'started'

    GAME_STARTED = 'true'
    GAME_NOT_STARTED = 'false'
    #: Time in seconds after which the game is deleted (48h).
    GAME_EXPIRE = 2*24*60*60

    SERVER_HOST = 'localhost'
    SERVER_PORT = 6379

    _redis = redis.Redis(host=ApiCache.SERVER_HOST, port=ApiCache.SERVER_PORT)

    def get_match(self, game_id):
        game_data = self._redis.get(GAME_KEY_TEMPLATE.format(game_id))
        return pickle.loads(game_data)
    
    def save_match(self, game, game_id):
        game_data = pickle.dumps(game)
        self._redis.set(GAME_KEY_TEMPLATE.format(game_id), game_data)

    def get_players_ids(self, game_id):
        return self._redis.smembers(self.PLAYERS_KEY_TEMPLATE.format(game_id))

    def has_opened_slots(self, game_id):
        return len(self._get_opened_slots(game_id)) > 0

    def is_new_game(self, game_id):
        return len(self._get_players_ids(game_id)) == 0

    def init(self, game_id, session_id):
        self._redis.hset(
            self.GAME_KEY_TEMPLATE.format(game_id),
            self.GAME_MASTER_KEY,
            session_id)
        self.save_session_id(game_id, session_id)
        self._redis.hset(
            self.GAME_KEY_TEMPLATE.format(game_id),
            self.STARTED_KEY,
            self.GAME_NOT_STARTED)
        self._init_first_slot(game_id, session_id)

    def _init_first_slot(self, game_id, session_id):
        slot = Slot()
        slot.player_id = session_id
        slot.state = SlotState.OPEN
        slot.index = i
        self._save_slot(game_id, slot)

    def save_session_id(self, game_id, session_id):
        self._redis.sadd(PLAYERS_KEY_TEMPLATE.format(game_id), session_id)

    def remove_session_id(self, game_id, session_id):
        self._redis.srem(PLAYERS_KEY_TEMPLATE.format(game_id), session_id)

    def game_exists(self, game_id):
        return self._redis.hget(
            self.GAME_KEY_TEMPLATE.format(game_id),
            self.GAME_MASTER_KEY) is not None

    def affect_next_slot(self, game_id, session_id):
        opened_slots = self._get_opened_slots(game_id)
        next_available_slot = opened_slots[0]
        next_available_slot.player = session_id
        next_available_slot.state = SlotState.TAKEN
        self.update_slot(game_id, session_id, next_available_slot)

        return next_available_slot.index
    
    def _get_opened_slots(self, game_id):
        slots = self.get_slots(game_id)
        return [slot for slot in slots in slot.is_open]

    def get_slots(self, game_id):
        return self._redis.lrange(self.SLOTS_KEY_TEMPLATE.format(game_id))

    def update_slot(self, game_id, session_id, slot):
        current_slot = self._get_slot(game_id, index)
        if current_slot.player_id == session_id:
            self._save_slot(game_id, slot)
        elif current_slot.state != SlotState.TAKEN:
            self._save_slot(game_id, slot)

    def _get_slot(self, game_id, index):
        return self._cache.lindex(self.SLOTS_KEY_TEMPLATE.format(game_id), index)

    def _save_slot(self, game_id, slot):
        self._cache.lset(self.SLOTS_KEY_TEMPLATE.format(game_id), slot.index, pickle.dumps(slot))

    def has_game_started(self, game_id):
        return self._cache.hget(self.GAME_KEY_TEMPLATE.format(game_id), self.STARTED_KEY) == \
            self.GAME_STARTED

    def game_has_started(self, game_id):
        self._cache.hset(self.GAME_KEY_TEMPLATE.format(game_id), self.STARTED_KEY, self.GAME_STARTED)

    def save_game(self, game, game_id):
        self._cache.hset(self.GAME_KEY_TEMPLATE.format(game_id), self.GAME_KEY, pickle.dumps(game))
