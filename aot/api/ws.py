################################################################################
# Copyright (C) 2016 by Arena of Titans Contributors.
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

import daiquiri
from autobahn.asyncio.websocket import WebSocketServerProtocol
from autobahn.exception import Disconnected

from ..config import config
from .api import Api as AotApi
from .cache import Cache
from .serializers import to_json
from .utils import (
    AotError,
    AotErrorToDisplay,
    AotFatalError,
    AotFatalErrorToDisplay,
    RequestTypes,
    WsResponse,
)
from .validation import ValidationError, validate


class AotWs(WebSocketServerProtocol):
    # Class variables.
    DISCONNECTED_TIMEOUT_WAIT = 10  # In seconds.
    logger = daiquiri.getLogger(__name__)
    _clients = {}
    _disconnect_timeouts = {}
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

    # Instance variables.
    _api = None
    _loop = None
    _id = None

    def set_event_loop_for_testing(self, event_loop):
        self._loop = event_loop

    async def onOpen(self):
        self._id = self._wskey
        self._clients[self.id] = self
        if self._loop is None:
            self._loop = asyncio.get_event_loop()
        self._api = AotApi(
            default_id=self.id,
            loop=self._loop,
            cache=Cache(loop=self._loop),
            ai_delay=config["ai"]["delay"],
        )

    async def onMessage(self, payload, is_binary):
        message = {}

        try:
            message = json.loads(payload.decode("utf-8"))
            self.logger.debug(f"Received message from {self.id}: {message}")
            validated_message = validate(message)
            self._check_reconnect(validated_message)
            response = await self._api.process_message(validated_message)
            self._handle_id_change()
        except AotError as e:
            await self._send_error(e, message)
        except ValidationError as e:
            await self._send_response(WsResponse(send_to_current_player=[{"errors": e.errors}]))
        except Exception:
            self.logger.exception("Unexpected error while processing message.")
        else:
            self._cancel_disconnect_player()
            await self._send_response(response)

    def _check_reconnect(self, validated_message):
        if (
            validated_message.get("rt") == RequestTypes.RECONNECT
            and validated_message.get("request", {}).get("player_id") in self._clients
        ):
            raise AotFatalErrorToDisplay("player_already_connected")

    def _handle_id_change(self):
        # If the player reconnected, its id won't be _wskey (the id of the websocket) but the true
        # id of the player (the one it had before being disconnected). To avoid issues when sending
        # messages, we need to update the id here:
        if self.id == self._api.id:
            return

        self.logger.info(
            f"Player reconnected to an existing game. "
            f"Its id was updated from {self.id} to {self._api.id}"
        )
        self._clients.pop(self.id, None)
        self._id = self._api.id
        self._clients[self.id] = self

    async def _send_response(self, response: WsResponse):
        if response.include_number_connected_clients:
            # The client making the info request is in the clients dict. We must not count it.
            response.send_to_current_player[0]["number_connected_players"] = len(self._clients) - 1

        sent_responses = []
        if response.future_message:
            response.future_message.add_done_callback(
                lambda future: asyncio.ensure_future(
                    self._send_response(future.result()), loop=self._loop
                )
            )
        if response.send_to_all:
            sent_responses.append(self._send_to_all(response.send_to_all))
        if response.send_to_all_others:
            sent_responses.append(
                self._send_to_all(response.send_to_all_others, excluded_players={self.id})
            )
        if response.send_to_current_player:
            sent_responses.append(self.send_messages(response.send_to_current_player))
        if response.send_debug:
            sent_responses.append(self._send_debug(response.send_debug))
        if response.send_to_each_players:
            for player_id, messages in response.send_to_each_players.items():
                sent_responses.append(self._send_to(messages, player_id))
        await asyncio.gather(*sent_responses)

    async def send_messages(self, messages):
        sent_messages = []
        for message in messages:
            sent_messages.append(self._send_message(message))
        await asyncio.gather(*sent_messages)

    async def _send_message(self, message):
        if isinstance(message, dict):
            message = json.dumps(message, default=to_json)
        self.logger.debug(f"Sending to {self.id}: {message}")
        message = message.encode("utf-8")
        # Must not use await here: sendMessage in the base class is not a coroutine.
        try:
            self.sendMessage(message)
        except Disconnected:
            self.logger.debug("Connection was closed, cannot send message.")

    async def onClose(self, was_clean, code, reason):  # pragma: no cover  # noqa: N802
        self.logger.info(
            f"WS n°{self.id} was closed cleanly? {was_clean} with code {code} and reason {reason}",
        )

        if config.is_testing:
            self._disconnect_timeouts[self.id] = None
            await self._disconnect_player()
        else:
            self._disconnect_timeouts[self.id] = self._loop.call_later(
                self.DISCONNECTED_TIMEOUT_WAIT,
                lambda: asyncio.ensure_future(self._disconnect_player()),
            )

        self._clients.pop(self.id, None)

    async def _disconnect_player(self):
        self.logger.debug(f"Disconnecting player {self.id} from game {self._api.game_id}")
        if self.id not in self._disconnect_timeouts:
            return

        # Remove expired timeout so it will never interfere with new disconnections.
        self._disconnect_timeouts.pop(self.id)

        try:
            response = await self._api.disconnect_player()
        except AotError as e:
            await self._send_error(e, {"rt": "disconnect"})
        else:
            if response:
                await self._send_response(response)

    def _cancel_disconnect_player(self):
        if self.id not in self._disconnect_timeouts:
            return

        # Remove canceled timeout so it will never interfere with new disconnections.
        self.logger.debug(f"Game n°{self._api.game_id}: cancel disconnect timeout for {self.id}")
        timeout = self._disconnect_timeouts.pop(self.id)
        timeout.cancel()

    async def _send_to_all(self, messages, excluded_players=None):
        if excluded_players is None:
            excluded_players = set()

        sent_messages = []

        for player_id in await self._api.player_ids:
            player = self._clients.get(player_id, None)
            if player is not None and player_id not in excluded_players:
                sent_messages.append(player.send_messages(messages))

        await asyncio.gather(*sent_messages)

    async def _send_to(self, messages, client_id):
        if client_id in self._clients:
            await self._clients[client_id].send_messages(messages)

    async def _send_error(self, error, received_message):
        message = self._format_error(error)
        # Errors to display are sent to the user and are foreseen in the application.
        # No need to log them.
        if not isinstance(error, AotErrorToDisplay):
            payload = json.dumps(received_message, default=to_json)
            self.logger.error(message["error"], extra_data={"payload": payload})

        await self.send_messages([message])

    async def _send_debug(self, message):
        if config["api"]["allow_debug"]:
            await self._send_to_all([{"debug": message}])

    def _format_error(self, error):
        message_key = "error_to_display" if isinstance(error, AotErrorToDisplay) else "error"
        # Some error messages to display can be formatted with infos from the exception
        # to give extra information to the user.
        raw_message = str(error)
        formatted_message = self._error_messages.get(raw_message, raw_message).format(**error.infos)

        formatted_error = {
            "is_fatal": False,
            message_key: formatted_message,
        }
        if error.infos:
            formatted_error["extra_data"] = error.infos
        if isinstance(error, AotFatalError):
            formatted_error["is_fatal"] = True

        return formatted_error

    @property
    def id(self):
        return self._id
