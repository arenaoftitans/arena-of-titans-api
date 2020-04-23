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

from ..utils import make_immutable
from .serializers import get_global_game_message, get_private_player_messages_by_ids, to_json
from .utils import AotError, AotErrorToDisplay, MustNotSaveGameError, RequestTypes, WsResponse
from .views import (
    create_game,
    create_lobby,
    free_slot,
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
            RequestTypes.PLAY_CARD: play_card,
            RequestTypes.SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS: view_possible_actions,
            RequestTypes.SPECIAL_ACTION_PLAY: play_action,
            RequestTypes.PLAY_TRUMP: play_trump,
        }
    )

    def __init__(self, *, default_id, loop, ai_delay, cache):
        self._loop = loop
        self._game_id = None
        self._id = default_id
        self._pending_ai = set()
        self._cache = cache
        self._ai_delay = ai_delay
        self._utility_request_types_to_views = {
            RequestTypes.TEST: self._test,
            RequestTypes.INFO: self._info,
        }
        self._message = {}

    async def process_message(self, message):
        self.logger.debug(
            f"Processing message of player {self._id} in game {self._game_id}: {message}"
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
        if not await self._has_game_started:
            self.logger.debug(f"Freeing slot for player {self.id} in game {self.game_id}")
            return await free_slot(
                {"player_id": self.id, "game_id": self.game_id, "free": True}, self._cache
            )

        return await self._disconnect_player_from_game()

    async def _disconnect_player_from_game(self):
        async with self._load_game() as game:
            player = game.get_player_by_id(self.id)
            self.logger.debug(
                f"Game n°{self._game_id}: player n°{self.id} ({player.name}) was "
                "disconnected from the game",
            )
            if game.is_over or player != game.active_player:
                self._append_to_clients_pending_disconnection()
                raise MustNotSaveGameError

            player.is_connected = False
            game.pass_turn()
            response = WsResponse(send_to_all=[get_global_game_message(game)])
            if game.active_player.is_ai:
                response = response.add_future_message(self._schedule_play_ai(game))
            return response

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
                response = response.add_future_message(self._schedule_play_ai(game))

        return response

    def _append_to_clients_pending_reconnection(self):
        self._clients_pending_reconnection_from_game.add(self.id)
        self._clients_pending_disconnection_from_game.discard(self.id)

    async def _process_lobby_request(self):
        if not await self._is_lobby_request_allowed:
            raise AotErrorToDisplay("game_master_request", {"rt": self._request_type})

        request = self._message["request"]
        request["player_id"] = self.id
        request["index_first_player"] = self.INDEX_FIRST_PLAYER

        response = await self._lobby_request_types_to_views[self._request_type](
            request, self._cache
        )

        if self._request_type in (RequestTypes.CREATE_LOBBY, RequestTypes.JOIN_GAME):
            # The cache was initiated with the proper game id we couldn't know before.
            # Save it now.
            self._game_id = self._cache.game_id

        return response

    async def _process_play_request(self):
        async with self._load_game() as game:
            if self._is_this_player_turn(game):
                response = self._play_game_requests_to_views[self._request_type](
                    self._message["request"], game
                )
                if game.active_player.is_ai:
                    response = response.add_future_message(self._schedule_play_ai(game))
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
                        "playload": json.dumps(self._message, default=to_json),
                    },
                )
                if self._message and self._message.get("request", {}).get("auto", False):
                    # It's an automated message, probably from a timer. Raise an error to quit
                    # here but don't display it.
                    raise AotError("not_your_turn")

                raise AotErrorToDisplay("not_your_turn")

    def _schedule_play_ai(self, game):
        if game.is_over:
            self.logger.debug(f"Game n°{self.game_id} is over, not scheduling AI.")
            return
        elif self.game_id in self._pending_ai:
            self.logger.debug(f"IA is already scheduled for game {self.game_id}")
            return

        self.logger.debug(f"Game n°{self._game_id}: schedule play for AI in {self._ai_delay}")
        self._pending_ai.add(self.game_id)
        future_message = asyncio.Future(loop=self._loop)
        self._loop.call_later(
            self._ai_delay,
            lambda: asyncio.ensure_future(self._play_scheduled_ai(future_message), loop=self._loop),
        )
        return future_message

    async def _play_scheduled_ai(self, future: asyncio.Future):
        response = await self._process_play_request()
        future.set_result(response)

    def _play_ai(self, game):
        self._pending_ai.discard(self._game_id)
        if not game.active_player.is_ai:
            self.logger.debug("It is not an AI turn, cannot play AI.")
            return

        self.logger.debug("Playing AI.")
        this_player = game.active_player
        game.play_auto()
        future_message = None
        if game.active_player.is_ai:
            future_message = self._schedule_play_ai(game)

        return WsResponse(
            send_to_all=[get_global_game_message(game)],
            send_to_each_players=get_private_player_messages_by_ids(game),
            send_debug=[{"player": this_player.name, "hand": this_player.hand_for_debug}],
            future_message=future_message,
        )

    @asynccontextmanager
    async def _load_game(self, must_save=True):
        game = await self._cache.get_game()

        if game is None:
            raise AotError("game_does_not_exist")

        try:
            yield game
            self._disconnect_pending_players(game)
            self._reconnect_pending_players(game)
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

    @property
    def id(self):
        return self._id

    @property
    def game_id(self):
        return self._game_id

    @property
    async def player_ids(self):
        return await self._cache.get_players_ids()

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
    async def _is_lobby_request_allowed(self):
        return await self._cache.is_game_master() or self._request_type != RequestTypes.CREATE_GAME

    @property
    async def _can_reconnect(self):
        return await self._cache.is_member_game(
            self._message["request"]["game_id"], self._message["request"]["player_id"],
        )

    @property
    def _request_type(self):
        return self._message.get("rt")
