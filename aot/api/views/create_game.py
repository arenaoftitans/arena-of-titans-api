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

import base64
import uuid

from ...config import config
from ...game.config import GAME_CONFIGS
from ..game_factory import create_game_for_players
from ..serializers import get_player_states_by_ids
from ..utils import AotError, AotErrorToDisplay, RequestTypes, SlotState, WsResponse, sanitize


async def create_lobby(request, cache):
    game_id = base64.urlsafe_b64encode(uuid.uuid4().bytes).replace(b"=", b"").decode("ascii")
    request["game_id"] = game_id
    cache.init(game_id=game_id, player_id=request["player_id"])
    game_config = GAME_CONFIGS["standard"]
    await cache.create_new_game(
        test=request.get("test", False), nb_slots=game_config["number_players"],
    )

    return join_game(request, cache)


async def create_game(request, cache):
    registered_number_players = await cache.number_taken_slots()
    submitted_player_descriptions = [
        player if player is not None and player.get("name", "") else None
        for player in request["players"]
    ]

    if not _has_submitted_good_number_player_descriptions(
        registered_number_players, submitted_player_descriptions
    ) or not _has_enough_players_registered(registered_number_players):
        raise AotError("registered_different_description")

    await cache.game_has_started()
    return await _initialize_game(cache, submitted_player_descriptions)


def _has_submitted_good_number_player_descriptions(number_players, players_description):
    return number_players == len([player for player in players_description if player])


def _has_enough_players_registered(number_players):
    game_config = GAME_CONFIGS["standard"]
    return 2 <= number_players <= game_config["number_players"]


async def _initialize_game(cache, submitted_player_descriptions):
    slots = await cache.get_slots()
    for player in submitted_player_descriptions:
        if player:
            index = player["index"]
            player["id"] = slots[index].get("player_id", None)
            player["is_ai"] = slots[index]["state"] == SlotState.AI

    game = create_game_for_players(submitted_player_descriptions)
    for player in game.players:
        if player is not None:
            player.is_connected = True

    await cache.save_game(game)
    return WsResponse(send_to_each_players=get_player_states_by_ids(game))


async def join_game(request, cache):
    if not await _can_join(request, cache):
        raise AotErrorToDisplay("cannot_join")

    cache.init(game_id=request["game_id"], player_id=request["player_id"])
    player_name = sanitize(request["player_name"])
    index = await cache.affect_next_slot(player_name, request["hero"])
    await cache.save_session(index)

    return WsResponse(
        send_to_current_player=[
            {
                "rt": RequestTypes.GAME_INITIALIZED,
                "game_id": request["game_id"],
                "player_id": request["player_id"],
                "is_game_master": await cache.is_game_master(),
                "index": index,
                "slots": await cache.get_slots(include_player_id=False),
                "api_version": config["version"],
            }
        ]
    )


async def _can_join(request, cache):
    return await cache.game_exists(request["game_id"]) and await cache.has_opened_slots(
        request["game_id"]
    )


async def update_slot(request, cache):
    slot = request["slot"]
    if not await cache.slot_exists(slot):
        raise AotError("non-existent_slot")

    if "player_name" in slot:
        slot["player_name"] = sanitize(slot["player_name"])

    if await cache.slot_exists(slot):
        await cache.update_slot(slot)
        # The player_id is stored in the cache so we can know to which player which slot is
        # associated. We don't pass this information to the frontend. If the slot is new, it
        # doesn't have a player_id yet, so we have to check for its existence before attempting
        # to delete it.
        if "player_id" in slot:
            del slot["player_id"]
        response = {
            "rt": RequestTypes.SLOT_UPDATED,
            "slot": slot,
        }
        return WsResponse(send_to_all=[response])
