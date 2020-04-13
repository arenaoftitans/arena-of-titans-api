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
from ..config import config
from ..utils import get_time
from .utils import RequestTypes


def get_global_game_message(game):
    return {
        "rt": RequestTypes.GAME_UPDATED,
        "request": _get_global_game_state(game),
    }


def _get_global_game_state(game):
    return {
        "actions": [],
        "is_over": game.is_over,
        "players": {player.index: _get_public_player_state(player) for player in game.players},
        "winners": game.winners,
    }


def _get_public_player_state(player):
    return {
        "active_trumps": player.trump_effects,
        "square": player.current_square,
    }


def get_private_player_messages_by_ids(game):
    messages = {}

    for player in game.players:
        if player is not None:
            messages[player.id] = [get_private_player_state(game, player)]

    return messages


def get_private_player_state(game, player):
    # Since between the request arrives (game.active_player.turn_start_time) and the time we
    # get here some time has passed. Which means, the elapsed time sent to the frontend could
    # be greater than 0 at the beginning of a turn.
    elapsed_time = get_time() - game.active_player.turn_start_time
    if elapsed_time < config["api"]["min_elapsed_time_to_consider"]:
        elapsed_time = 0

    return {
        "rt": RequestTypes.PLAYER_UPDATED,
        "request": {
            "your_turn": player.id == game.active_player.id,
            "on_last_line": player.on_last_line,
            "has_won": player.has_won,
            "rank": player.rank,
            "next_player": game.active_player.index,
            "hand": [
                {"name": card.name, "color": card.color, "description": card.description}
                for card in player.hand
            ],
            "active_trumps": [
                {
                    "player_index": game_player.index,
                    "player_name": game_player.name,
                    "trumps": game_player.trump_effects,
                }
                for game_player in game.players
            ],
            "trump_target_indexes": [
                player.index
                for player in game.players
                if player and player.can_be_targeted_by_trumps
            ],
            "has_remaining_moves_to_play": player.has_remaining_moves_to_play,
            "trumps_statuses": player.trumps_statuses,
            "can_power_be_played": player.can_power_be_played,
            "gauge_value": player.gauge.value,
            "elapsed_time": elapsed_time,
            "nb_turns": game.nb_turns,
            "power": player.power,
        },
    }
