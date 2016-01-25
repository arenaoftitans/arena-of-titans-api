from enum import Enum

from aot.board import Square
from aot.cards.trumps import Trump


class RequestTypes(Enum):
    INIT_GAME = 'INIT_GAME'
    CREATE_GAME = 'CREATE_GAME'
    GAME_INITIALIZED = 'GAME_INITIALIZED'
    ADD_SLOT = 'ADD_SLOT'
    SLOT_UPDATED = 'SLOT_UPDATED'
    PLAY = 'PLAY'
    VIEW_POSSIBLE_SQUARES = 'VIEW_POSSIBLE_SQUARES'
    PLAY_TRUMP = 'PLAY_TRUMP'
    PLAYER_PLAYED = 'PLAYER_PLAYED'


class SlotState(Enum):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    RESERVED = 'RESERVED'
    TAKEN = 'TAKEN'


def to_json(python_object):
    if isinstance(python_object, Enum):
        return python_object.value
    elif isinstance(python_object, Square):
        return {
            'x': python_object.x,
            'y': python_object.y
        }
    elif isinstance(python_object, Trump):
        return {
            'cost': python_object.cost,
            'description': python_object.description,
            'duration': python_object.duration,
            'must_target_player': python_object.must_target_player,
            'name': python_object.name,
        }
    elif isinstance(python_object, set):
        return [to_json(element) for element in python_object]
    # Normally, this is unreachable
    raise TypeError(str(python_object) + ' is not JSON serializable')  # pragma: no cover
