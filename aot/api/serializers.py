#
#  Copyright (C) 2015-2020 by Arena of Titans Contributors.
#
#  This file is part of Arena of Titans.
#
#  Arena of Titans is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Arena of Titans is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
#

import dataclasses
import math
from enum import Enum

from aot.game import Player
from aot.game.board import Board, Square
from aot.game.cards import Card
from aot.game.trumps import Power
from aot.game.trumps.effects import TrumpEffect

from ..config import config
from ..utils import get_time
from .utils import RequestTypes


def get_global_game_message(game):
    return {
        "rt": RequestTypes.GAME_UPDATED,
        "request": get_global_game_state(game),
    }


def get_global_game_state(game):
    return {
        "id": game.game_id,
        "actions": game.actions,
        "board": game.board,
        "is_over": game.is_over,
        "current_player_index": game.active_player.index,
        "nb_turns": game.nb_turns,
        "players": {player.index: _get_public_player_state(player) for player in game.players},
        "winners": game.winners,
    }


def _get_public_player_state(player):
    return {
        "active_trumps": player.trump_effects,
        "square": player.current_square,
        "name": player.name,
        "index": player.index,
        "hero": player.hero,
        "is_visible": player.is_visible,
    }


def get_private_player_messages_by_ids(game):
    messages = {}

    for player in game.players:
        if player is not None:
            messages[player.id] = [get_private_player_message(game, player)]

    return messages


def get_private_player_message(game, player):
    return {
        "rt": RequestTypes.PLAYER_UPDATED,
        "request": get_private_player_state(game, player),
    }


def get_private_player_state(game, player):
    # Since between the request arrives (game.active_player.turn_start_time) and the time we
    # get here some time has passed. Which means, the elapsed time sent to the frontend could
    # be greater than 0 at the beginning of a turn.
    elapsed_time = get_time() - game.active_player.turn_start_time
    if elapsed_time < config["api"]["min_elapsed_time_to_consider"]:
        elapsed_time = 0

    return {
        "name": player.name,
        "index": player.index,
        "id": player.id,
        "available_trumps": player.available_trumps,
        "hero": player.hero,
        "your_turn": player.id == game.active_player.id,
        "on_last_line": player.on_last_line,
        "has_won": player.has_won,
        "rank": player.rank,
        "hand": [
            {"name": card.name, "color": card.color, "description": card.description}
            for card in player.hand
        ],
        "active_trumps": player.trump_effects,
        "trump_target_indexes": [
            player.index for player in game.players if player and player.can_be_targeted_by_trumps
        ],
        "has_remaining_moves_to_play": player.has_remaining_moves_to_play,
        "trumps_statuses": player.trumps_statuses,
        "can_power_be_played": player.can_power_be_played,
        "gauge_value": player.gauge.value,
        "elapsed_time": elapsed_time,
        "power": player.power,
        "special_action": player.name_next_special_action,
    }


def to_json(python_object):  # noqa: C901 too complex
    if isinstance(python_object, Enum):
        return python_object.value
    elif isinstance(python_object, Square):
        return {
            "x": python_object.x,
            "y": python_object.y,
        }
    elif isinstance(python_object, Board):
        return {"updated_squares": python_object.updated_squares}
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
    elif isinstance(python_object, Player):
        return {
            "name": python_object.name,
            "index": python_object.index,
        }
    elif isinstance(python_object, Card):
        return {
            "name": python_object.name,
            "color": python_object.color,
        }
    elif isinstance(python_object, type):
        return python_object.__name__
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
