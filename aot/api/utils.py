from enum import Enum


class RequestTypes(Enum):
    INIT_GAME = 'INIT_GAME'
    CREATE_GAME = 'CREATE_GAME'
    GAME_INITIALIZED = 'GAME_INITIALIZED'
    ADD_SLOT = 'ADD_SLOT'
    SLOT_UPDATED = 'SLOT_UPDATED'
    PLAY = 'PLAY'
    VIEW_POSSIBLE_SQUARES = 'VIEW_POSSIBLE_SQUARES'
    PLAY_TRUMP = 'PLAY_TRUMP'


class SlotState(Enum):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    RESERVED = 'RESERVED'
    TAKEN = 'TAKEN'


def to_json(python_object):
    if isinstance(python_object, Enum):
        return python_object.value
    raise TypeError(repr(python_object) + ' is not JSON serializable')
