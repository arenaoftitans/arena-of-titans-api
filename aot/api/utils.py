from enum import Enum


class RequestTypes(Enum):
    CREATE_GAME = 'CREATE_GAME'
    GAME_INITIALIZED = 'GAME_INITIALIZED'
    ADD_SLOT = 'ADD_SLOT'
    SLOT_UPDATED = 'SLOT_UPDATED'
    PLAY = 'PLAY'
    VIEW_POSSIBLE_SQUARES = 'VIEW_POSSIBLE_SQUARES'
    PLAY_TRUMP = 'PLAY_TRUMP'


class SlotState(Enum):
    OPEN = 0
    CLOSED = 1
    RESERVED = 2
    TAKEN = 3


class Slot:
    rt = None
    player_name = ''
    player_id = ''
    index = -1
    state = SlotState.OPEN

    def __init__(self, data=None):
        if isinstance(data, dict):
            self.rt = data['rt']
            self.player_name = data['player_name']
            self.index = data['index']
            self.state = SlotState[data['state']]
