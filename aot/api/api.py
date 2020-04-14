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

import asyncio
import json
from contextlib import asynccontextmanager

import daiquiri

from ..config import config
from ..utils import get_time, make_immutable
from .cache import Cache
from .utils import (
    AotError,
    AotErrorToDisplay,
    AotFatalErrorToDisplay,
    MustNotSaveGameError,
    RequestTypes,
    WsResponse,
)
from .views import (
    create_game,
    create_lobby,
    join_game,
    play_action,
    play_card,
    play_trump,
    reconnect_to_game,
    reconnect_to_lobby,
    update_slot,
    view_possible_actions,
    view_possible_squares,
)


class Api:
    # Class variables.
    INDEX_FIRST_PLAYER = 0
    MIN_ELAPSED_TIME_TO_CONSIDER = 8
    _clients_pending_disconnection = {}
    _clients_pending_reconnection = {}
    logger = daiquiri.getLogger(__name__)
    _lobby_request_types_to_views = make_immutable(
        {
            RequestTypes.CREATE_LOBBY: create_lobby,
            RequestTypes.JOIN_GAME: join_game,
            RequestTypes.UPDATE_SLOT: update_slot,
            RequestTypes.CREATE_GAME: create_game,
        }
    )
    _play_game_requests_to_views = make_immutable(
        {
            RequestTypes.VIEW_POSSIBLE_SQUARES: view_possible_squares,
            RequestTypes.PLAY: play_card,
            RequestTypes.SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS: view_possible_actions,
            RequestTypes.SPECIAL_ACTION_PLAY: play_action,
            RequestTypes.PLAY_TRUMP: play_trump,
        }
    )

    def __init__(self, *, default_id, loop):
        self._loop = loop
        self._game_id = None
        self._id = default_id
        self._pending_ai = set()
        self._is_debug_mode_enabled = False
        self._cache = Cache()
        self._utility_request_types_to_views = {
            "test": self._test,
            "info": self._info,
        }
        self._message = {}

    async def process_message(self, message):
        self.logger.debug(
            f"Possessing message of player {self._id} in game {self._game_id}: {message}"
        )

        self._message = message

        if self._request_type in self._utility_request_types_to_views:
            return await self._utility_request_types_to_views[self._request_type]()
        elif self._request_type == RequestTypes.RECONNECT:
            return await self._process_reconnect_request()
        elif self._request_type in self._lobby_request_types_to_views:
            return await self._process_lobby_request()
        elif self._request_type in self._play_game_requests_to_views:
            return await self._process_play_request()

        raise AotErrorToDisplay("unknown_request")

    async def _info(self):
        return WsResponse(
            send_to_current_player=[await self._cache.info()], include_number_connected_clients=True
        )

    async def _test(self):
        try:
            await self._cache.test()
        except Exception as e:
            self.logger.exception(e)
            return WsResponse(send_to_current_player=[{"success": False, "errors": str(e)}])
        else:
            return WsResponse(send_to_current_player=[{"success": True}])

    async def disconnect_player(self):
        if await self._has_game_started:
            return await self._free_slot()
        else:
            return await self._disconnect_player_from_game()

    async def _free_slot(self):
        slots = await self._cache.get_slots()
        slots = [slot for slot in slots if slot.get("player_id", None) == self.id]
        if slots:
            slot = slots[0]
            name = slot.get("player_name", None)
            self.logger.debug(
                f"Game n°{self._game_id}: slot for player n°{self.id} ({name}) was freed",
            )
            self._message = {
                "rt": RequestTypes.SLOT_UPDATED,
                "slot": {"index": slot["index"], "state": "OPEN"},
            }
            return await self._modify_slots()

    async def _disconnect_player_from_game(self):
        async with self._load_game() as game:
            if not game:
                return

            player = game.get_player_by_id(self.id)
            self.logger.debug(
                f"Game n°{self._game_id}: player n°{self.id} ({player.name}) was "
                "disconnected from the game",
            )
            if not game.is_over and player == game.active_player:
                player.is_connected = False
                game.pass_turn()
                message = self._get_play_messages(game, player)
                if game.active_player.is_ai:
                    future_message = asyncio.Future()
                    self._play_ai_after_timeout(game, future_message)
                    message.add_future_message(future_message)
                return message
            else:
                self._append_to_clients_pending_disconnection()
                raise MustNotSaveGameError

    def _append_to_clients_pending_disconnection(self):
        self._clients_pending_disconnection_from_game.add(self.id)
        self._clients_pending_reconnection_from_game.discard(self.id)

    async def _process_reconnect_request(self):
        if not await self._can_reconnect:
            raise AotErrorToDisplay("cannot_join")

        self._id = self._message["request"]["player_id"]
        self._game_id = self._message["request"]["game_id"]
        self._cache.init(game_id=self._game_id, player_id=self.id)

        self.logger.info(f"Trying to reconnect player {self.id} to game {self.game_id}")

        if not await self._has_game_started:
            return await reconnect_to_lobby(self._message["request"], self._cache)

        async with self._load_game(must_save=False) as game:
            self._append_to_clients_pending_reconnection()
            response = reconnect_to_game(self._message["request"], game)
            if game.active_player.is_ai and self._game_id not in self._pending_ai:
                future_message = asyncio.Future(loop=self._loop)
                self._play_ai_after_timeout(game, future_message)
                response.add_future_message(future_message)

        return response

    def _append_to_clients_pending_reconnection(self):
        self._clients_pending_reconnection_from_game.add(self.id)
        self._clients_pending_disconnection_from_game.discard(self.id)

    async def _process_lobby_request(self):
        if not await self._current_request_allowed:
            raise AotErrorToDisplay("game_master_request", {"rt": self._request_type})

        self._is_debug_mode_enabled = (
            self._message.get("debug", False) and config["api"]["allow_debug"]
        )

        self._message["player_id"] = self.id
        self._message["index_first_player"] = self.INDEX_FIRST_PLAYER

        response = self._lobby_request_types_to_views[self._request_type](
            self._message, self._cache
        )

        if self._request_type in (RequestTypes.CREATE_LOBBY, RequestTypes.JOIN_GAME):
            # The cache was initiated with the proper game id we couldn't know before.
            # Save it now.
            self._game_id = self._cache.game_id

        return response

    async def _process_play_request(self):
        async with self._load_game() as game:
            if self._is_this_player_turn(game):
                request = self._message.get("play_request", None)

                response = self._play_game_requests_to_views[self._request_type](request, game)
                if game.active_player.is_ai:
                    future_message = asyncio.Future(loop=self._loop)
                    self._play_ai_after_timeout(game, future_message)
                    response = response.add_future_message(future_message)
                return response
            elif game.active_player.is_ai:
                return self._play_ai(game)
            else:
                # We have a not_your_turn error that is displayed sometimes
                # without an action for the player. We add logs to understand why.
                player = game.get_player_by_id(self.id)
                self.logger.warning(
                    "not_your_turn",
                    extra_data={
                        "player": f"Player ({self.id}): {player.name}",
                        "playload": json.dumps(self._message),
                    },
                )
                if self._message and self._message.get("auto", False):
                    # It's an automated message, probably from a timer. Raise an error to quit
                    # here but don't display it.
                    raise AotError("not_your_turn")

                raise AotErrorToDisplay("not_your_turn")

    def _play_ai_after_timeout(self, game, future: asyncio.Future):
        if not game.is_over:
            self.logger.debug(f"Game n°{self._game_id}: schedule play for AI in {self._api_delay}")
            self._pending_ai.add(self._game_id)
            self._loop.call_later(
                self._api_delay,
                lambda: asyncio.ensure_future(self._play_scheduled_ai(future), loop=self._loop),
            )

    async def _play_scheduled_ai(self, future: asyncio.Future):
        response = await self._process_play_request()
        future.set_result(response)

    def _play_ai(self, game):
        self._pending_ai.discard(self._game_id)
        if game.active_player.is_ai:
            self.logger.debug("Playing AI.")
            this_player = game.active_player
            debug_message = {"player": this_player.name, "hand": this_player.hand_for_debug}
            game.play_auto()
            future_message = None
            if game.active_player.is_ai:
                future_message = asyncio.Future(loop=self._loop)
                self._play_ai_after_timeout(game, future_message)

            play_messages = self._get_play_messages(game, this_player)
            return play_messages.add_debug_message(debug_message).add_future_message(future_message)

    @asynccontextmanager
    async def _load_game(self, must_save=True):
        game = await self._cache.get_game()
        self._disconnect_pending_players(game)
        self._reconnect_pending_players(game)

        try:
            yield game
        except MustNotSaveGameError:
            self.logger.info("Action asked not to save the game.", exc_info=True)
        except Exception:
            self.logger.exception("Uncaught error while playing, will not save the loaded game")
            raise
        else:
            if must_save:
                await self._cache.save_game(game)

    def _disconnect_pending_players(self, game):
        self._change_players_connection_status(
            game, self._clients_pending_disconnection_from_game, is_connected=False,
        )

    def _change_players_connection_status(self, game, player_ids, is_connected):
        while len(player_ids) > 0:
            player_id = player_ids.pop()
            player = game.get_player_by_id(player_id)
            player.is_connected = is_connected

    def _reconnect_pending_players(self, game):
        self._change_players_connection_status(
            game, self._clients_pending_reconnection_from_game, is_connected=True,
        )

    def _is_this_player_turn(self, game):
        return self.id is not None and self.id == game.active_player.id

    def _get_play_messages(self, game, this_player):  # pragma: no cover
        game.add_action(this_player.last_action)
        return WsResponse(
            send_to_all=[self._get_player_played_message(this_player, game)],
            send_to_each_players=self._get_play_messages_for_all_players(game),
        )

    def _get_player_played_message(self, player, game):
        return {
            "rt": RequestTypes.PLAYER_PLAYED,
            "player_index": player.index,
            "new_square": {"x": player.current_square.x, "y": player.current_square.y},
            "has_remaining_moves_to_play": player.has_remaining_moves_to_play,
            "trumps_statuses": player.trumps_statuses,
            "can_power_be_played": player.can_power_be_played,
            "last_action": self._get_action_message(player.last_action),
            "game_over": game.is_over,
            "winners": game.winners,
        }

    def _get_action_message(self, action):  # pragma: no cover
        if action is not None:
            return {
                "description": action.description,
                "card": action.card,
                "trump": action.trump,
                "special_action": action.special_action,
                "player_name": action.player_name,
                "target_name": action.target_name,
                "target_index": action.target_index,
                "player_index": action.player_index,
            }

    def _get_play_messages_for_all_players(self, game):
        messages = {}

        for player in game.players:
            if player is not None:
                messages[player.id] = [self._get_play_message(player, game)]

        return messages

    def _get_play_message(self, player, game):
        # Since between the request arrives (game.active_player.turn_start_time) and the time we
        # get here some time has passed. Which means, the elapsed time sent to the frontend could
        # be greater than 0 at the beginning of a turn.
        elapsed_time = get_time() - game.active_player.turn_start_time
        if elapsed_time < self.MIN_ELAPSED_TIME_TO_CONSIDER:
            elapsed_time = 0

        return {
            "rt": RequestTypes.PLAY,
            "your_turn": player.id == game.active_player.id,
            "on_last_line": player.on_last_line,
            "has_won": player.has_won,
            "rank": player.rank,
            "next_player": game.active_player.index,
            "hand": [
                {"name": card.name, "color": card.color, "description": card.description}
                for card in player.hand
            ],
            "active_trumps": self._get_active_trumps_message(game),
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
        }

    def _get_active_trumps_message(self, game):
        return [
            {
                "player_index": game_player.index,
                "player_name": game_player.name,
                "trumps": game_player.trump_effects,
            }
            if game_player
            else None
            for game_player in game.players
        ]

    @property
    def id(self):
        return self._id

    @property
    def is_debug_mode_enabled(self):
        return self._is_debug_mode_enabled

    @property
    def game_id(self):
        return self._game_id

    @property
    async def player_ids(self):
        return await self._cache.get_players_ids()

    @property
    def _api_delay(self):
        return config["ai"]["delay"]

    @property
    def _clients_pending_reconnection_from_game(self):
        return self._clients_pending_reconnection.setdefault(self._game_id, set())

    @property
    def _clients_pending_disconnection_from_game(self):
        return self._clients_pending_disconnection.setdefault(self._game_id, set())

    @property
    async def _has_game_started(self):
        return await self._cache.has_game_started()

    @property
    async def _current_request_allowed(self):
        return await self._cache.is_game_master() or self._request_type in (
            RequestTypes.SLOT_UPDATED,
            RequestTypes.CREATE_LOBBY,
        )

    @property
    async def _can_reconnect(self):
        if self._message["player_id"] not in self._clients_pending_reconnection_from_game:
            raise AotFatalErrorToDisplay("player_already_connected")

        return await self._cache.is_member_game(
            self._message["game_id"], self._message["player_id"],
        )

    @property
    def _request_type(self):
        return self._message.get("rt")
