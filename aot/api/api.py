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
import base64
import json
import uuid
from contextlib import asynccontextmanager

import daiquiri

from ..config import config
from ..game.config import GAME_CONFIGS
from ..game.utils import get_time
from .cache import Cache
from .game_factory import create_game_for_players
from .utils import (
    AotError,
    AotErrorToDisplay,
    AotFatalErrorToDisplay,
    RequestTypes,
    WsResponse,
    sanitize,
)
from .views import play_action, play_card, play_trump, view_possible_actions, view_possible_squares


class Api:
    # Class variables.
    INDEX_FIRST_PLAYER = 0
    MIN_ELAPSED_TIME_TO_CONSIDER = 8
    _clients_pending_disconnection = {}
    _clients_pending_reconnection = {}
    logger = daiquiri.getLogger(__name__)

    def __init__(self, *, default_id, loop):
        self._loop = loop
        self._game_id = None
        self._id = default_id
        self._must_save_game = True
        self._pending_ai = set()
        self._is_debug_mode_enabled = False
        self._cache = Cache()

    async def process_message(self, message):  # noqa: C901 (too complex)
        self.logger.debug(f"Received from player {self._id} in game {self._game_id}: {message}")

        try:
            self._message = message
            self._rt = self._message.get("rt", "")
            if "game_id" in self._message:
                self._game_id = self._message["game_id"]
                self._cache.init(game_id=self._game_id, player_id=self.id)

            response = ""
            if self._rt == "test":
                response = await self._test()
            elif self._rt == "info":
                response = await self._info()
            elif self._rt not in RequestTypes:
                raise AotError("unknown_request", {"rt": self._rt, "where": "on_message"})
            elif self._is_reconnecting:
                if await self._can_reconnect:
                    response = await self._reconnect()
                else:
                    raise AotErrorToDisplay("cannot_join")
            elif self._creating_new_game:
                response = await self._create_new_game()
            elif await self._creating_game:
                response = await self._process_create_game_request()
            else:
                response = await self._process_play_request()
        except AotError:
            raise
        except Exception:
            raise

        return response

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
        if await self._creating_game:
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
                self._must_save_game = False

    def _append_to_clients_pending_disconnection(self):
        self._clients_pending_disconnection_from_game.add(self.id)
        self._clients_pending_reconnection_from_game.discard(self.id)

    async def _reconnect(self):
        self._id = self._message["player_id"]
        self._game_id = self._message["game_id"]
        self._cache.init(game_id=self._game_id, player_id=self.id)

        self.logger.info(f"Reconnecting player {self.id} to game {self.game_id}")

        message = None

        if await self._creating_game:
            try:
                index = await self._cache.get_player_index()
            except IndexError:
                # We were disconnected and we must register again
                self._game_id = None
                index = -1
            finally:
                message = await self._get_initialized_game_message(index)
        else:
            async with self._load_game() as game:
                self._must_save_game = False
                self._append_to_clients_pending_reconnection()
                message = self._reconnect_to_game(game)
                if game.active_player.is_ai and self._game_id not in self._pending_ai:
                    self._play_ai_after_timeout(game)

        return WsResponse(send_to_current_player=[message])

    def _reconnect_to_game(self, game):
        player = [player for player in game.players if player and player.id == self.id][0]
        self.logger.debug(
            f"Game n°{self._game_id}: player n°{self.id} ({player.name}) was reconnected "
            f"to the game",
        )
        message = self._get_play_message(player, game)

        last_action = self._get_action_message(game.last_action)
        if game.active_player.has_special_actions:
            special_action = game.active_player.name_next_special_action
        else:
            special_action = None

        message["reconnect"] = {
            "players": [
                {
                    "index": player.index,
                    "name": player.name,
                    "square": player.current_square,
                    "hero": player.hero,
                }
                if player
                else None
                for player in game.players
            ],
            "trumps": player.trumps,
            "power": player.power,
            "index": player.index,
            "last_action": last_action,
            "special_action_name": special_action,
            "special_action_elapsed_time": get_time() - player.special_action_start_time,
            "history": [
                [self._get_action_message(action) for action in player.history] if player else None
                for player in game.players
            ],
            "game_over": game.is_over,
            "winners": game.winners,
        }

        return message

    def _append_to_clients_pending_reconnection(self):
        self._clients_pending_reconnection_from_game.add(self.id)
        self._clients_pending_disconnection_from_game.discard(self.id)

    async def _create_new_game(self):
        self._game_id = (
            base64.urlsafe_b64encode(uuid.uuid4().bytes).replace(b"=", b"").decode("ascii")
        )
        await self._initialize_cache(new_game=True)
        response = await self._get_initialized_game_message(self.INDEX_FIRST_PLAYER)
        return WsResponse(send_to_current_player=[response])

    async def _initialize_cache(self, new_game=False):
        self._cache.init(game_id=self._game_id, player_id=self._id)
        if new_game:
            game_config = GAME_CONFIGS["standard"]
            await self._cache.create_new_game(
                test=self._message.get("test", False), nb_slots=game_config["number_players"],
            )
        index = await self._affect_current_slot()
        await self._cache.save_session(index)
        return index

    async def _get_initialized_game_message(self, index):  # pragma: no cover
        initialized_game = {
            "rt": RequestTypes.GAME_INITIALIZED,
            "game_id": self._game_id,
            "player_id": self.id,
            "is_game_master": await self._cache.is_game_master(),
            "index": index,
            "slots": await self._cache.get_slots(include_player_id=False),
            "api_version": config["version"],
        }

        return initialized_game

    async def _affect_current_slot(self):
        player_name = sanitize(self._message.get("player_name", ""))
        hero = self._message.get("hero", "")
        return await self._cache.affect_next_slot(player_name, hero)

    async def _process_create_game_request(self):
        if not await self._current_request_allowed:
            raise AotErrorToDisplay("game_master_request", {"rt": self._rt})
        elif self._rt == RequestTypes.INIT_GAME:
            if await self._can_join:
                return await self._join()
            else:
                raise AotErrorToDisplay("cannot_join")
        elif self._rt == RequestTypes.SLOT_UPDATED:
            return await self._modify_slots()
        elif self._rt == RequestTypes.CREATE_GAME:
            return await self._create_game()
        else:
            raise AotError(
                "unknown_request", {"rt": self._rt, "where": "process_create_game_request"},
            )

    async def _join(self):
        index = await self._initialize_cache()
        response = await self._get_initialized_game_message(index)
        return WsResponse(
            send_to_current_player=[response],
            send_to_all_others=[
                {"rt": RequestTypes.SLOT_UPDATED, "slot": response["slots"][index]}
            ],
        )

    async def _modify_slots(self):
        slot = self._message.get("slot", None)
        if slot is not None and "player_name" in slot:
            slot["player_name"] = sanitize(slot["player_name"])
        if slot is None:
            raise AotErrorToDisplay("no_slot")
        elif await self._cache.slot_exists(slot):
            await self._cache.update_slot(slot)
            # The player_id is stored in the cache so we can know to which player which slot is
            # associated. We don't pass this information to the frontend. If the slot is new, it
            # doesn't have a player_id yet, so we have to check for its existance before attempting
            # to delete it.
            if "player_id" in slot:
                del slot["player_id"]
            response = {
                "rt": RequestTypes.SLOT_UPDATED,
                "slot": slot,
            }
            return WsResponse(send_to_all=[response])
        else:
            raise AotError("non-existent_slot")

    async def _create_game(self):
        number_players = await self._cache.number_taken_slots()
        create_game_request = self._message.get("create_game_request", None)
        if create_game_request is None:
            raise AotError("no_request")
        players_description = [
            player if player is not None and player.get("name", "") else None
            for player in create_game_request
        ]

        if not self._good_number_players_description(
            number_players, players_description
        ) or not self._good_number_player_registered(number_players):
            raise AotError("registered_different_description")

        await self._cache.game_has_started()
        return await self._initialize_game(players_description)

    def _good_number_player_registered(self, number_players):
        game_config = GAME_CONFIGS["standard"]
        return 2 <= number_players <= game_config["number_players"]

    def _good_number_players_description(self, number_players, players_description):
        return number_players == len([player for player in players_description if player])

    async def _initialize_game(self, players_description):
        slots = await self._cache.get_slots()
        for player in players_description:
            if player:
                index = player["index"]
                player["id"] = slots[index].get("player_id", None)
                player["is_ai"] = slots[index]["state"] == "AI"

        game = create_game_for_players(players_description)
        game.game_id = self._game_id
        self._is_debug_mode_enabled = (
            self._message.get("debug", False) and config["api"]["allow_debug"]
        )
        for player in game.players:
            if player is not None:
                player.is_connected = True

        await self._cache.save_game(game)
        return WsResponse(send_to_each_players=self._get_game_created_messages(game))

    def _get_game_created_messages(self, game):
        messages = {}
        for player in game.players:
            message = {
                "rt": RequestTypes.CREATE_GAME,
                "your_turn": game.active_player.id == player.id,
                "next_player": 0,
                "game_over": False,
                "winners": [],
                "players": [
                    {
                        "index": player.index,
                        "name": player.name,
                        "hero": player.hero,
                        "square": {"x": player.current_square.x, "y": player.current_square.y},
                    }
                    if player
                    else None
                    for player in game.players
                ],
                "active_trumps": self._get_active_trumps_message(game),
                "has_remaining_moves_to_play": player.has_remaining_moves_to_play,
                "trumps_statuses": player.trumps_statuses,
                "can_power_be_played": player.can_power_be_played,
                "gauge_value": player.gauge.value,
                "hand": [
                    {"name": card.name, "color": card.color, "description": card.description}
                    for card in player.hand
                ],
                "trumps": player.trumps,
                "power": player.power,
            }
            messages[player.id] = [message]
        return messages

    async def _process_play_request(self):
        async with self._load_game() as game:
            if self._is_player_id_correct(game):
                response = await self._play_game(game)
                if game.active_player.is_ai:
                    future_message = asyncio.Future(loop=self._loop)
                    self._play_ai_after_timeout(game, future_message)
                    response = response.add_future_message(future_message)
                return response
            elif game.active_player.is_ai:
                return self._play_ai(game)
            else:
                self._must_save_game = False
                # We have a not_your_turn error that is displayed sometimes
                # without an action for the player. We add logs to understand why.
                try:
                    player = game.get_player_by_id(self.id)
                    self.logger.warning(
                        "not_your_turn",
                        extra_data={
                            "player": f"Player ({self.id}): {player.name}",
                            "playload": json.dumps(self._message),
                        },
                    )
                # This may happen if self.id is not a valid id.
                # Since this is mostly for testing, we don't do anything about it.
                except KeyError:
                    pass
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
    async def _load_game(self):
        self._must_save_game = True
        game = await self._cache.get_game()
        self._disconnect_pending_players(game)
        self._reconnect_pending_players(game)

        try:
            yield game
        except Exception:
            self.logger.exception("Uncaught error while playing, will not save the loaded game")
            raise
        else:
            if self._must_save_game:
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

    def _is_player_id_correct(self, game):
        return self.id is not None and self.id == game.active_player.id

    async def _play_game(self, game):
        play_request = self._message.get("play_request", None)
        if play_request is None:
            raise AotError("no_request")
        elif self._rt == RequestTypes.VIEW_POSSIBLE_SQUARES:
            return self._view_possible_squares(game, play_request)
        elif self._rt == RequestTypes.PLAY:
            return await self._play(game, play_request)
        elif self._rt == RequestTypes.SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS:
            return await self._view_possible_actions(game, play_request)
        elif self._rt == RequestTypes.SPECIAL_ACTION_PLAY:
            return await self._play_special_action(game, play_request)
        elif self._rt == RequestTypes.PLAY_TRUMP:
            return await self._play_trump(game, play_request)
        else:
            raise AotError("unknown_request", {"rt": self._rt, "where": "play_game"})

    def _view_possible_squares(self, game, play_request):
        possible_squares = view_possible_squares(game, play_request)
        return WsResponse(
            send_to_current_player=[
                {"rt": RequestTypes.VIEW_POSSIBLE_SQUARES, "possible_squares": possible_squares}
            ]
        )

    async def _play(self, game, play_request):
        this_player, has_special_actions = play_card(game, play_request)
        play_messages = self._get_play_messages(game, this_player)
        if has_special_actions:
            play_messages.send_to_current_player.append(
                self._get_notify_special_action_message(game.active_player.name_next_special_action)
            )
        return play_messages

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

    def _get_notify_special_action_message(self, special_actions_name):
        return {
            "rt": RequestTypes.SPECIAL_ACTION_NOTIFY,
            "special_action_name": special_actions_name,
        }

    async def _view_possible_actions(self, game, play_request):
        message = view_possible_actions(game, play_request)
        message["rt"] = RequestTypes.SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS
        return WsResponse(send_to_current_player=message)

    async def _play_special_action(self, game, play_request):
        was_played, target = play_action(game, play_request)
        response = WsResponse()
        if was_played:
            response.send_to_all.append(
                self._get_player_played_special_action_message(game.active_player, target)
            )

        if game.active_player.has_special_actions:
            response.send_to_current_player.append(
                self._get_notify_special_action_message(game.active_player.name_next_special_action)
            )
        else:
            game.complete_special_actions()
            response.send_to_each_players.update(self._get_play_messages_for_all_players(game))
        return response

    def _get_player_played_special_action_message(self, player, target):  # pragma: no cover
        return {
            "rt": RequestTypes.SPECIAL_ACTION_PLAY,
            "player_index": player.index,
            "target_index": target.index,
            "new_square": {
                "x": target.current_square.x,
                "y": target.current_square.y,
                "color": target.current_square.color,
            },
            "special_action_name": player.last_action.special_action.name,
            "last_action": self._get_action_message(player.last_action),
        }

    async def _play_trump(self, game, play_request):
        target, context, rt = play_trump(game, play_request)

        common_message = {
            "rt": rt,
            "active_trumps": self._get_active_trumps_message(game),
            "player_index": game.active_player.index,
            "target_index": target.index,
            "trumps_statuses": game.active_player.trumps_statuses,
            "can_power_be_played": game.active_player.can_power_be_played,
            "last_action": self._get_action_message(game.active_player.last_action),
            "square": context.get("square"),
        }
        current_player_message = {
            **common_message,
            "gauge_value": game.active_player.gauge.value,
            "power": game.active_player.power,
        }

        return WsResponse(
            send_to_all_others=[common_message], send_to_current_player=[current_player_message],
        )

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
    async def _can_join(self):
        return await self._cache.game_exists(self._game_id) and await self._cache.has_opened_slots(
            self._game_id
        )

    @property
    def _clients_pending_reconnection_from_game(self):
        return self._clients_pending_reconnection.setdefault(self._game_id, set())

    @property
    def _clients_pending_disconnection_from_game(self):
        return self._clients_pending_disconnection.setdefault(self._game_id, set())

    @property
    async def _creating_game(self):
        return not await self._cache.has_game_started()

    @property
    def _creating_new_game(self):
        return self._game_id is None or (
            self._rt == RequestTypes.INIT_GAME and "game_id" not in self._message
        )

    @property
    async def _current_request_allowed(self):
        return await self._cache.is_game_master() or self._rt in (
            RequestTypes.SLOT_UPDATED,
            RequestTypes.INIT_GAME,
        )

    @property
    def _is_reconnecting(self):
        return (
            self._rt == RequestTypes.INIT_GAME
            and "player_id" in self._message
            and "game_id" in self._message
        )

    @property
    async def _can_reconnect(self):
        if self._message["player_id"] not in self._clients_pending_reconnection_from_game:
            raise AotFatalErrorToDisplay("player_already_connected")

        return await self._cache.is_member_game(
            self._message["game_id"], self._message["player_id"],
        )
