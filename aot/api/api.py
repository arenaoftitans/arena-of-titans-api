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

from ..cards.trumps.constants import TargetTypes as TrumpsTargetTypes
from ..cards.trumps.exceptions import (
    GaugeTooLowToPlayTrump,
    MaxNumberAffectingTrumps,
    MaxNumberTrumpPlayed,
    TrumpHasNoEffect,
)
from ..config import config
from ..game import Player
from ..game.config import GAME_CONFIGS
from ..utils import get_time
from .game_factory import create_game_for_players
from .utils import AotError, AotErrorToDisplay, RequestTypes, sanitize
from .ws import AotWs


class Api(AotWs):
    # Class variables.
    INDEX_FIRST_PLAYER = 0
    MIN_ELAPSED_TIME_TO_CONSIDER = 8
    LOGGER = daiquiri.getLogger(__name__)
    _error_messages = {
        "cannot_join": "You cannot join this game. No slots opened.",
        "game_master_request": "Only the game master can use {rt} request.",
        "gauge_too_low": "trumps.gauge_too_low",
        "non-existent_slot": "Trying to update non existent slot.",
        "max_number_trumps": "trumps.max_number_trumps",
        "max_number_played_trumps": "trumps.max_number_played_trumps",
        "missing_action_name": "You must specify the name of the action you want to do",
        "missing_action_target": "You must specify the target for the action",
        "missing_trump_target": "You must specify a target player.",
        "no_action": "You have no special actions to do.",
        "no_slot": "No slot provided.",
        "not_your_turn": "Not your turn.",
        "no_request": "No request was provided",
        "player_already_connected": "errors.player_already_connected",
        "registered_different_description": "Number of registered players differs with number of "
        "players descriptions or too many/too few players are "
        "registered.",
        "unknown_error": "Unknown error.",
        "unknown_request": "Unknown request: {rt}.",
        "wrong_action": "You provided an invalid action name or you do not have any actions to "
        "play",
        "wrong_card": "This card doesn't exist or is not in your hand.",
        "wrong_square": "This square doesn't exist or you cannot move there yet.",
        "wrong_trump": "Unknown trump.",
        "wrong_trump_target": "Wrong target player index.",
    }

    # Instance variables
    _game_id = None
    _id = None
    _must_save_game = True
    _pending_ai = set()

    async def onMessage(self, payload, is_binary):  # noqa: C901 (too complex)
        self.LOGGER.debug(f"Received from {self.id}: {payload}")

        try:
            self._message = json.loads(payload.decode("utf-8"))
            self._rt = self._message.get("rt", "")
            if "game_id" in self._message:
                self._game_id = self._message["game_id"]
                self._cache.init(game_id=self._game_id, player_id=self.id)

            if self._rt == "test":
                await self._test()
            elif self._rt == "info":
                await self._info()
            elif self._rt not in RequestTypes:
                raise AotError("unknown_request", {"rt": self._rt, "where": "on_message"})
            elif self._is_reconnecting:
                if await self._can_reconnect:
                    await self._reconnect()
                else:
                    raise AotErrorToDisplay("cannot_join")
            elif self._creating_new_game:
                await self._create_new_game()
            elif await self._creating_game:
                await self._process_create_game_request()
            else:
                await self._process_play_request()
        except AotError as e:
            await self._send_error(e)
        except Exception:  # pragma: no cover
            self.LOGGER.exception("onMessage")

    async def _info(self):
        info = {
            # The client making the info request is in the clients dict. We must not count it.
            "number_connected_players": (len(self._clients) - 1),
        }
        info.update(await self._cache.info())

        await self.sendMessage(info)

    async def _test(self):
        try:
            await self._cache.test()
        except Exception as e:
            self.LOGGER.exception(e)
            await self.sendMessage({"success": False, "errors": str(e)})
        else:
            await self.sendMessage({"success": True})

    async def _create_new_game(self):
        self._game_id = (
            base64.urlsafe_b64encode(uuid.uuid4().bytes).replace(b"=", b"").decode("ascii")
        )
        await self._initialize_cache(new_game=True)
        response = await self._get_initialized_game_message(self.INDEX_FIRST_PLAYER)
        await self.sendMessage(response)

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
                await self._join()
            else:
                raise AotErrorToDisplay("cannot_join")
        elif self._rt == RequestTypes.SLOT_UPDATED:
            await self._modify_slots()
        elif self._rt == RequestTypes.CREATE_GAME:
            await self._create_game()
        else:  # pragma: no cover
            raise AotError(
                "unknown_request", {"rt": self._rt, "where": "process_create_game_request"},
            )

    async def _join(self):
        index = await self._initialize_cache()
        response = await self._get_initialized_game_message(index)
        await self.sendMessage(response)
        await self._send_updated_slot_new_player(response["slots"][index])

    async def _send_updated_slot_new_player(self, slot):
        message = {
            "rt": RequestTypes.SLOT_UPDATED,
            "slot": slot,
        }
        await self._send_all_others(message)

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
            await self._send_all(response)
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

        await self._initialize_game(players_description)
        await self._cache.game_has_started()

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
        game.is_debug = self._message.get("debug", False) and config["api"]["allow_debug"]
        for player in game.players:
            if player is not None and player.id in self._clients:
                player.is_connected = True

        await self._cache.save_game(game)
        await self._send_game_created_message(game)

    async def _send_game_created_message(self, game):  # pragma: no cover
        # Some session can be used for multiple players (mostly for debug purpose). We use the set
        # below to keep track of players' id and only send the first request for these sessions.
        # Otherwise, the list of cards for the first player to play would be overriden by the cards
        # of the last one.
        ids_message_sent = set()
        for player in game.players:
            if player is None or player.id in ids_message_sent:
                continue
            ids_message_sent.add(player.id)
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
            await self._send_to(message, player.id)

    async def _process_play_request(self):
        async with self._load_game() as game:
            if self._is_player_id_correct(game):
                await self._play_game(game)
                if game.active_player.is_ai:
                    self._play_ai_after_timeout(game)
            elif game.active_player.is_ai:
                await self._play_ai(game)
            else:
                self._must_save_game = False
                # We have a not_your_turn error that is displayed sometimes
                # without an action for the player. We add logs to understand why.
                try:
                    player = game.get_player_by_id(self.id)
                    self.LOGGER.warning(
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
                if self._message and self._message["auto"]:
                    # It's an automated message, probably from a timer. Raise an error to quit
                    # here but don't display it.
                    raise AotError("not_your_turn")

                raise AotErrorToDisplay("not_your_turn")

    def _play_ai_after_timeout(self, game):
        if not game.is_over:
            self.LOGGER.debug(f"Game n°{self._game_id}: schedule play for AI",)
            self._pending_ai.add(self._game_id)
            self._loop.call_later(
                self._api_delay, lambda: asyncio.ensure_future(self._process_play_request()),
            )

    async def _play_ai(self, game):
        self._pending_ai.discard(self._game_id)
        if game.active_player.is_ai:
            this_player = game.active_player
            if game.is_debug:
                await self._send_debug(
                    {"player": this_player.name, "hand": this_player.hand_for_debug}
                )
            game.play_auto()
            await self._send_play_message(game, this_player)
            if game.active_player.is_ai:
                self._play_ai_after_timeout(game)

    @asynccontextmanager
    async def _load_game(self):
        self._must_save_game = True
        game = await self._get_game()
        self._disconnect_pending_players(game)
        self._reconnect_pending_players(game)

        try:
            yield game
        except Exception:
            self.LOGGER.exception("Uncaught error while playing, will not save the loaded game")
            raise
        else:
            if self._must_save_game:
                await self._save_game(game)

    def _disconnect_pending_players(self, game):
        self._change_players_connection_status(
            game, self._clients_pending_disconnection_for_game, False,
        )

    def _change_players_connection_status(self, game, player_ids, status):
        while len(player_ids) > 0:
            player_id = player_ids.pop()
            player = game.get_player_by_id(player_id)
            player.is_connected = status

    def _reconnect_pending_players(self, game):
        self._change_players_connection_status(
            game, self._clients_pending_reconnection_for_game, True,
        )

    async def _get_game(self):
        return await self._cache.get_game()

    async def _save_game(self, game):
        await self._cache.save_game(game)

    def _is_player_id_correct(self, game):
        return self.id is not None and self.id == game.active_player.id

    async def _play_game(self, game):
        play_request = self._message.get("play_request", None)
        if play_request is None:
            raise AotError("no_request")
        elif self._rt == RequestTypes.VIEW_POSSIBLE_SQUARES:
            await self._view_possible_squares(game, play_request)
        elif self._rt == RequestTypes.PLAY:
            await self._play(game, play_request)
        elif self._rt == RequestTypes.SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS:
            await self._view_possible_actions(game, play_request)
        elif self._rt == RequestTypes.SPECIAL_ACTION_PLAY:
            await self._play_special_action(game, play_request)
        elif self._rt == RequestTypes.PLAY_TRUMP:
            await self._play_trump(game, play_request)
        else:
            raise AotError("unknown_request", {"rt": self._rt, "where": "play_game"})

    async def _view_possible_squares(self, game, play_request):
        card = self._get_card(game, play_request)
        if card is not None:
            possible_squares = game.view_possible_squares(card)
            await self.sendMessage(
                {"rt": RequestTypes.VIEW_POSSIBLE_SQUARES, "possible_squares": possible_squares}
            )
        else:
            raise AotErrorToDisplay("wrong_card")

    def _get_card(self, game, play_request):
        name = play_request.get("card_name", None)
        color = play_request.get("card_color", None)
        return game.active_player.get_card(name, color)

    async def _play(self, game, play_request):
        this_player = game.active_player
        has_special_actions = False
        if play_request.get("pass", False):
            game.pass_turn()
        elif play_request.get("discard", False):
            card = self._get_card(game, play_request)
            if card is None:
                raise AotErrorToDisplay("wrong_card")
            game.discard(card)
        else:
            card = self._get_card(game, play_request)
            square = self._get_square(play_request, game)
            if card is None:
                raise AotErrorToDisplay("wrong_card")
            elif square is None or not game.can_move(card, square):
                raise AotErrorToDisplay("wrong_square")
            has_special_actions = game.play_card(card, square)

        await self._send_play_message(game, this_player)
        if has_special_actions:
            await self._notify_special_action(game.active_player.name_next_special_action)

    def _get_square(self, play_request, game):
        x = play_request.get("x", None)
        y = play_request.get("y", None)
        return game.get_square(x, y)

    async def _send_play_message(self, game, this_player):  # pragma: no cover
        game.add_action(this_player.last_action)
        await self._send_player_played_message(this_player, game)

        await self._send_play_message_to_players(game)

    async def _send_player_played_message(self, player, game):  # pragma: no cover
        await self._send_all(
            {
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
        )

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

    async def _send_play_message_to_players(self, game):  # pragma: no cover
        for player in game.players:
            if player is not None and player.id in self._clients:
                await self._clients[player.id].sendMessage(self._get_play_message(player, game))

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
                "trumps": game_player.affecting_trumps,
            }
            if game_player
            else None
            for game_player in game.players
        ]

    async def _notify_special_action(self, special_actions_name):
        await self.sendMessage(
            {"rt": RequestTypes.SPECIAL_ACTION_NOTIFY, "special_action_name": special_actions_name}
        )

    async def _view_possible_actions(self, game, play_request):
        action, target_index = self._get_action(game, play_request)
        message = {
            "rt": RequestTypes.SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS,
            "special_action_name": action.name,
        }
        if action.require_target_square:
            message["possible_squares"] = action.view_possible_squares(game.players[target_index])

        await self.sendMessage(message)

    def _get_action(self, game, play_request):
        action_name = play_request.get("special_action_name", None)
        action_color = play_request.get("special_action_color", None)
        target_index = play_request.get("target_index", None)
        allow_no_target = play_request.get("cancel", False)

        if not action_name:
            raise AotError("missing_action_name")
        elif target_index is None and not allow_no_target:
            raise AotError("missing_action_target")

        try:
            return game.active_player.special_actions[action_name, action_color], target_index
        except IndexError:
            raise AotError("wrong_action")
        except TypeError as e:
            if str(e) == "'NoneType' object is not subscriptable":
                raise AotError("no_action")
            else:  # pragma: no cover
                raise e

    async def _play_special_action(self, game, play_request):
        action, target_index = self._get_action(game, play_request)
        if play_request.get("cancel", False):
            game.cancel_special_action(action)
        else:
            await self._play_special_action_on_target(game, play_request, action, target_index)

        if game.active_player.has_special_actions:
            await self._notify_special_action(game.active_player.name_next_special_action)
        else:
            game.complete_special_actions()
            await self._send_play_message_to_players(game)

    async def _play_special_action_on_target(self, game, play_request, action, target_index):
        kwargs = {}
        target = game.players[target_index]
        if action.require_target_square:
            kwargs["square"] = self._get_square(play_request, game)
            if kwargs["square"] is None:
                raise AotErrorToDisplay("wrong_square")

        game.play_special_action(action, target=target, action_args=kwargs)
        last_action = game.active_player.last_action
        game.add_action(last_action)
        await self._send_player_played_special_action(game.active_player, target)

    async def _send_player_played_special_action(self, player, target):  # pragma: no cover
        await self._send_all(
            {
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
        )

    async def _play_trump(self, game, play_request):
        try:
            trump = self._get_trump(
                game, play_request.get("name", None), play_request.get("color", None),
            )
        except IndexError:
            raise AotError("wrong_trump")

        if trump.must_target_player:
            trump.initiator = game.active_player.name

        target, target_index = self._get_trump_target(game, trump, play_request)

        await self._play_trump_with_target(game, trump, target, target_index)

    def _get_trump_target(self, game, trump, play_request):
        target_index = play_request.get("target_index", None)
        if trump.must_target_player and target_index is None:
            raise AotError("missing_trump_target")
        elif not trump.must_target_player:
            target_index = game.active_player.index

        if trump.target_type == TrumpsTargetTypes.board:
            target = {
                "x": play_request["square"]["x"],
                "y": play_request["square"]["y"],
                "color": play_request["square"]["color"],
            }
        elif trump.target_type in (TrumpsTargetTypes.player, TrumpsTargetTypes.trump):
            try:
                target = game.players[target_index]
            except IndexError:
                raise AotError("The target of this trump does not exist")
        else:
            raise AotError("invalid_trump")

        return target, target_index

    async def _play_trump_with_target(self, game, trump, target, target_index):
        """Play a trump on its target.

        Target represent what the trump will target (ie a player or a square)
        whereas the target_index represents the index of the player that was the target
        of the trump (the active player if the target is a square).

        TODO: improve this.
        """
        try:
            target_type = trump.target_type
            square = target if target_type == TrumpsTargetTypes.board else None
            game.play_trump(trump, target)
        except GaugeTooLowToPlayTrump:
            raise AotError("gauge_too_low")
        except MaxNumberTrumpPlayed:
            raise AotError(
                "max_number_played_trumps", infos={"num": Player.MAX_NUMBER_TRUMPS_PLAYED},
            )
        except MaxNumberAffectingTrumps:
            raise AotErrorToDisplay(
                "max_number_trumps", {"num": Player.MAX_NUMBER_AFFECTING_TRUMPS},
            )
        except TrumpHasNoEffect:
            game.add_action(game.active_player.last_action)
            await self._send_trump_played_message(
                game, target_index, rt=RequestTypes.TRUMP_HAS_NO_EFFECT,
            )
        else:
            game.add_action(game.active_player.last_action)
            await self._send_trump_played_message(
                game, target_index, square=square, target_type=target_type,
            )

    async def _send_trump_played_message(
        self, game, target_index, rt=RequestTypes.PLAY_TRUMP, square=None, target_type=None,
    ):  # pragma: no cover
        message = {
            "rt": rt,
            "active_trumps": self._get_active_trumps_message(game),
            "player_index": game.active_player.index,
            "target_index": target_index,
            "trumps_statuses": game.active_player.trumps_statuses,
            "can_power_be_played": game.active_player.can_power_be_played,
            "last_action": self._get_action_message(game.active_player.last_action),
            "square": square,
        }
        await self._send_all_others(message)
        message["gauge_value"] = game.active_player.gauge.value
        if target_type == TrumpsTargetTypes.trump:
            message["power"] = game.active_player.power
        await self.sendMessage(message)

    def _get_trump(self, game, trump_name, trump_color):
        return game.active_player.get_trump(trump_name, trump_color)

    @property
    def _api_delay(self):
        return config["ai"]["delay"]

    @property
    async def _can_join(self):
        return await self._cache.game_exists(self._game_id) and await self._cache.has_opened_slots(
            self._game_id
        )

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
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
