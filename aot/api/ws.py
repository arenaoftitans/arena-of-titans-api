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

from abc import abstractmethod

import daiquiri

from asyncio_extras.contextmanager import async_contextmanager
from autobahn.asyncio.websocket import WebSocketServerProtocol

from .api_cache import ApiCache
from .utils import (
    RequestTypes,
    to_json,
)
from ..utils import get_time


class AotWs(WebSocketServerProtocol):
    # Class variables.
    DISCONNECTED_TIMEOUT_WAIT = 10
    LOGGER = daiquiri.getLogger(__name__)
    _clients = {}
    _clients_pending_disconnection = {}
    _clients_pending_reconnection = {}
    _disconnect_timeouts = {}

    # Instance variable
    _cache = None
    _loop = None
    _message = None
    _rt = ''

    @property
    @abstractmethod
    def _creating_new_game(self):  # pragma: no cover
        pass

    @abstractmethod
    def _create_new_game(self):  # pragma: no cover
        pass

    @property
    @abstractmethod
    async def _creating_game(self):  # pragma: no cover
        pass

    @abstractmethod
    def _process_create_game_request(self):  # pragma: no cover
        pass

    @abstractmethod
    def _process_play_request(self):  # pragma: no cover
        pass

    @abstractmethod
    def _get_action_message(self, action):  # pragma: no cover
        pass

    @abstractmethod
    @async_contextmanager
    async def _load_game(self):  # pragma: no cover
        pass

    @abstractmethod
    def _modify_slots(self):  # pragma: no cover
        pass

    @abstractmethod
    def _play_ai_after_timeout(self, game):  # pragma: no cover
        pass

    async def sendMessage(self, message):  # pragma: no cover  # noqa: N802
        if isinstance(message, dict):
            message = json.dumps(message, default=to_json)
        self.LOGGER.debug(message)
        message = message.encode('utf-8')
        if isinstance(message, bytes):
            # Must not use await here: sendMessage in the base class is not a coroutine.
            super().sendMessage(message)

    async def onOpen(self):  # pragma: no cover  # noqa: N802
        self.id = self._wskey
        self._clients[self.id] = self
        self._loop = asyncio.get_event_loop()
        self._set_up_connection_keep_alive()
        self._cache = ApiCache()

    async def onClose(self, was_clean, code, reason):  # pragma: no cover  # noqa: N802
        self.LOGGER.info(
            f'WS n°{self.id} was closed cleanly? {was_clean} with code {code} and reason {reason}',
        )

        if self._cache is not None:
            self._disconnect_timeouts[self.id] = self._loop.call_later(
                self.DISCONNECTED_TIMEOUT_WAIT,
                lambda: asyncio.ensure_future(self._disconnect_player()),
            )

        if self.id in self._clients:
            del self._clients[self.id]

    async def onPong(self, payload):  # pragma: no cover  # noqa: N802
        self._set_up_connection_keep_alive()

    async def _disconnect_player(self):
        if await self._creating_game:
            await self._free_slot()
        else:
            await self._disconnect_player_from_game()

    async def _free_slot(self):
        slots = await self._cache.get_slots()
        slots = [slot for slot in slots if slot.get('player_id', None) == self.id]
        if slots:
            slot = slots[0]
            name = slot.get('player_name', None)
            self.LOGGER.debug(
                f'Game n°{self._game_id}: slot for player n°{self.id} ({name}) was freed',
            )
            self._message = {
                'rt': RequestTypes.SLOT_UPDATED,
                'slot': {
                    'index': slot['index'],
                    'state': 'OPEN',
                },
            }
            await self._modify_slots()

    async def _disconnect_player_from_game(self):
        async with self._load_game() as game:
            if game:
                player = game.get_player_by_id(self.id)
                self.LOGGER.debug(
                    f'Game n°{self._game_id}: player n°{self.id} ({player.name}) was '
                    'disconnected from the game',
                )
                if not game.is_over and player == game.active_player:
                    player.is_connected = False
                    game.pass_turn()
                    await self._send_play_message(game, player)
                    if game.active_player.is_ai:
                        self._play_ai_after_timeout(game)
                else:
                    self._append_to_clients_pending_disconnection()
                    self._must_save_game = False

    def _append_to_clients_pending_disconnection(self):
        self._clients_pending_disconnection_for_game.add(self.id)
        self._clients_pending_reconnection_for_game.discard(self.id)

    def _set_up_connection_keep_alive(self):  # pragma: no cover
        self._loop.call_later(5, self.sendPing)

    @property
    def _is_reconnecting(self):
        return self._rt == RequestTypes.INIT_GAME and \
            'player_id' in self._message and \
            'game_id' in self._message

    @property
    async def _can_reconnect(self):
        return await self._cache.is_member_game(
            self._message['game_id'],
            self._message['player_id'],
        )

    async def _reconnect(self):
        self.id = self._message['player_id']
        self._game_id = self._message['game_id']
        self._cache.init(game_id=self._game_id, player_id=self.id)
        self._clients[self.id] = self

        if self.id in self._disconnect_timeouts:
            self.LOGGER.debug(
                f'Game n°{self._game_id}: cancel disconnect timeout for {self.id}',
            )
            self._disconnect_timeouts[self.id].cancel()

        message = None

        if await self._creating_game:
            try:
                index = await self._cache.get_player_index()
            except IndexError:
                # We were disconnected and we must register again
                self._game_id = None
                index = -1
            finally:
                message = await self._get_initialiazed_game_message(index)
        else:
            async with self._load_game() as game:
                self._must_save_game = False
                self._append_to_clients_pending_reconnection()
                message = self._reconnect_to_game(game)
                if game.active_player.is_ai and self._game_id not in self._pending_ai:
                    self._play_ai_after_timeout(game)

        if message:
            await self.sendMessage(message)

    def _append_to_clients_pending_reconnection(self):
        self._clients_pending_reconnection_for_game.add(self.id)
        self._clients_pending_disconnection_for_game.discard(self.id)

    def _reconnect_to_game(self, game):
        player = [player for player in game.players if player and player.id == self.id][0]
        self.LOGGER.debug(
            f'Game n°{self._game_id}: player n°{self.id} ({player.name}) was reconnected '
            f'to the game',
        )
        message = self._get_play_message(player, game)

        last_action = self._get_action_message(game.last_action)
        if game.active_player.has_special_actions:
            special_action = game.active_player.name_next_special_action
        else:
            special_action = None

        message['reconnect'] = {
            'players': [{
                'index': player.index,
                'name': player.name,
                'square': player.current_square,
                'hero': player.hero,
            } if player else None for player in game.players],
            'trumps': player.trumps,
            'index': player.index,
            'last_action': last_action,
            'special_action_name': special_action,
            'special_action_elapsed_time': get_time() - player.special_action_start_time,
            'history': self._get_history(game),
            'game_over': game.is_over,
            'winners': game.winners,
        }

        return message

    def _get_history(self, game):
        return [
            [self._get_action_message(action) for action in player.history]
            if player else None for player in game.players]

    async def _send_all(self, message, excluded_players=None):  # pragma: no cover
        if excluded_players is None:
            excluded_players = set()

        messages = []

        for player_id in await self._cache.get_players_ids():
            player = self._clients.get(player_id, None)
            if player is not None and player_id not in excluded_players:
                messages.append(player.sendMessage(message))

        await asyncio.gather(*messages)

    async def _send_all_others(self, message):  # pragma: no cover
        await self._send_all(message, excluded_players=set([self.id]))

    async def _send_to(self, message, id):  # pragma: no cover
        if id in self._clients:
            await self._clients[id].sendMessage(message)

    def _format_error_to_display(self, message, format_opt=None):  # pragma: no cover
        if format_opt is None:
            format_opt = {}

        return {'error_to_display': self._get_error(message, format_opt)}

    def _get_error(self, message, format_opt):  # pragma: no cover
        return self._error_messages.get(message, message).format(**format_opt)

    async def _send_error(self, message, format_opt=None):  # pragma: no cover
        if format_opt is None:
            format_opt = {}

        await self.sendMessage(self._format_error(message, format_opt))

    async def _send_error_to_display(self, message, format_opt=None):  # pragma: no cover
        if format_opt is None:
            format_opt = {}

        await self.sendMessage(self._format_error_to_display(message, format_opt))

    async def _send_debug(self, message):  # pragma: no cover
        await self._send_all({'debug': message})

    async def _send_all_error(self, message, format_opt=None):  # pragma: no cover
        if format_opt is None:
            format_opt = {}

        await self._send_all(self._format_error(message, format_opt))

    def _format_error(self, message, format_opt=None):  # pragma: no cover
        if format_opt is None:
            format_opt = {}

        return {'error': self._get_error(message, format_opt)}

    @property
    def _clients_pending_reconnection_for_game(self):
        return self._clients_pending_reconnection.setdefault(self._game_id, set())

    @property
    def _clients_pending_disconnection_for_game(self):
        return self._clients_pending_disconnection.setdefault(self._game_id, set())
