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

from ...config import config
from ..serializers import get_global_game_state, get_private_player_state
from ..utils import RequestTypes, WsResponse


def reconnect_to_game(request, game):
    player = [player for player in game.players if player and player.id == request["player_id"]][0]

    return WsResponse(
        send_to_current_player=[
            {
                "rt": RequestTypes.JOIN_GAME,
                "request": {
                    "game": get_global_game_state(game),
                    "player": get_private_player_state(game, player),
                },
            }
        ]
    )


async def reconnect_to_lobby(request, cache):
    try:
        index = await cache.get_player_index()
    except IndexError:
        return WsResponse(
            send_to_current_player=[
                {
                    "rt": RequestTypes.JOINED_LOBBY,
                    "request": {
                        "error": "cannot_join",
                        "must_register_again": True,
                        "game_id": request["game_id"],
                    },
                }
            ]
        )

    return WsResponse(
        send_to_current_player=[
            {
                "rt": RequestTypes.JOINED_LOBBY,
                "request": {
                    "game_id": request["game_id"],
                    "player_id": request["player_id"],
                    "is_game_master": await cache.is_game_master(),
                    "index": index,
                    "slots": await cache.get_slots(include_player_id=False),
                    "api_version": config["version"],
                },
            }
        ]
    )
