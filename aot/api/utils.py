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

import dataclasses
import math

import bleach

from aot.game.board import Square
from aot.game.trumps import Power
from aot.game.trumps.effects import TrumpEffect
from aot.game.utils import SimpleEnumMeta


class AotError(Exception):
    def __init__(self, msg, infos=None):
        super().__init__(msg)
        if infos is None:
            self.infos = {}
        else:
            self.infos = infos


class AotErrorToDisplay(AotError):
    pass


class AotFatalError(AotError):
    def __init__(self, msg, infos=None):
        super().__init__(msg, infos)


class AotFatalErrorToDisplay(AotFatalError, AotErrorToDisplay):
    pass


class RequestTypes(metaclass=SimpleEnumMeta):
    INIT_GAME = ()
    CREATE_GAME = ()
    GAME_INITIALIZED = ()
    SLOT_UPDATED = ()
    SPECIAL_ACTION_NOTIFY = ()
    SPECIAL_ACTION_PLAY = ()
    SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS = ()
    PLAY = ()
    VIEW_POSSIBLE_SQUARES = ()
    PLAY_TRUMP = ()
    PLAYER_PLAYED = ()
    TRUMP_HAS_NO_EFFECT = ()


class SlotState(metaclass=SimpleEnumMeta):
    OPEN = ()
    CLOSED = ()
    RESERVED = ()
    TAKEN = ()
    AI = ()


def sanitize(string):
    return bleach.clean(string, tags=[], strip=True)


def to_json(python_object):  # pragma: no cover
    if isinstance(python_object, SimpleEnumMeta):
        return python_object.value
    elif isinstance(python_object, Square):
        return {
            "x": python_object.x,
            "y": python_object.y,
        }
    elif isinstance(python_object, TrumpEffect):
        data = {
            "duration": python_object.duration if not math.isinf(python_object.duration) else None,
            "name": python_object.name,
            "color": python_object.color,
            "effect_type": python_object.effect_type,
        }
        return data
    elif isinstance(python_object, (set, frozenset)):
        return [to_json(element) for element in python_object]
    elif dataclasses.is_dataclass(python_object):
        # Our dataclasses may hold a reference to a class which we can't serialize into JSON.
        trump_like = {
            key: value
            for key, value in dataclasses.asdict(python_object).items()
            if not isinstance(value, type)
        }
        if isinstance(trump_like.get("trump_args"), dict):
            trump_like = {
                **trump_like,
                **trump_like["trump_args"],
            }
            del trump_like["trump_args"]
        if isinstance(python_object, Power):
            trump_like["is_power"] = True
            trump_like["passive"] = python_object.passive

        return trump_like

    # Normally, this is unreachable
    raise TypeError(str(python_object) + " is not JSON serializable")  # pragma: no cover
