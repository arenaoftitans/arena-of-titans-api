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
from aot.api.api_cache import ApiCache
from aot.api.utils import (
    to_json,
    RequestTypes,
)
from autobahn.asyncio.websocket import WebSocketServerProtocol
from contextlib import contextmanager


class AotWs(WebSocketServerProtocol):
    # Class variables.
    DISCONNECTED_TIMEOUT_WAIT = 10
    _clients = {}
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
    def _creating_game(self):  # pragma: no cover
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
    @contextmanager
    def _load_game(self):  # pragma: no cover
        pass

    def sendMessage(self, message):  # pragma: no cover
        if isinstance(message, dict):
            message = json.dumps(message, default=to_json)
        message = message.encode('utf-8')
        if isinstance(message, bytes):
            super().sendMessage(message)

    def onOpen(self):  # pragma: no cover
        self.id = self._wskey
        self._clients[self.id] = self
        self._loop = asyncio.get_event_loop()
        self._set_up_connection_keep_alive()
        self._cache = ApiCache()

    def onClose(self, wasClean, code, reason):
        if self._cache is not None:
            self._disconnect_timeouts[self.id] = self._loop.call_later(
                self.DISCONNECTED_TIMEOUT_WAIT,
                self._disconnect_player
            )

        if self.id in self._clients:
            del self._clients[self.id]

    def onPong(self, payload):  # pragma: no cover
        self._set_up_connection_keep_alive()

    def _disconnect_player(self):
        if self._creating_game:
            self._free_slot()
        else:
            self._disconnect_player_from_game()

    def _free_slot(self):
        slots = self._cache.get_slots()
        slots = [slot for slot in slots if slot.get('player_id', None) == self.id]
        if slots:
            slot = slots[0]
            self._message = {
                'rt': RequestTypes.SLOT_UPDATED,
                'slot': {
                    'index': slot['index'],
                    'state': 'OPEN',
                },
            }
            self._modify_slots(RequestTypes.SLOT_UPDATED)

    def _disconnect_player_from_game(self):
        with self._load_game() as game:
            if game:
                player = game.disconnect(self.id)
                if not game.is_over and player == game.active_player:
                    game.pass_turn()
                    self._send_play_message(player, game)

    def _set_up_connection_keep_alive(self):  # pragma: no cover
        self._loop.call_later(5, self.sendPing)

    @property
    def _is_reconnecting(self):
        return self._rt == RequestTypes.INIT_GAME and \
            'player_id' in self._message and \
            'game_id' in self._message

    @property
    def _can_reconnect(self):
        return self._cache.is_member_game(self._message['game_id'], self._message['player_id'])

    def _reconnect(self):
        self.id = self._message['player_id']
        self._game_id = self._message['game_id']
        self._cache.init(game_id=self._game_id, player_id=self.id)
        self._clients[self.id] = self

        if self.id in self._disconnect_timeouts:
            self._disconnect_timeouts[self.id].cancel()

        message = None

        if self._creating_game:
            try:
                index = self._cache.get_player_index()
            except IndexError:
                # We were disconnected and we must register again
                self._game_id = None
                index = -1
            finally:
                message = self._get_initialiazed_game_message(index)
        else:
            with self._load_game() as game:
                message = self._reconnect_to_game(game)

        if message:
            self.sendMessage(message)

    def _reconnect_to_game(self, game):
        player = [player for player in game.players if player.id == self.id][0]
        player.is_connected = True
        message = self._get_play_message(player, game)

        last_action = self._get_action_message(game.last_action)

        message['reconnect'] = {
            'players': [{
                'index': player.index,
                'name': player.name,
                'square': player.current_square,
                'hero': player.hero,
            } for player in game.players],
            'trumps': player.trumps,
            'index': player.index,
            'last_action': last_action,
            'history': self._get_history(game),
            'game_over': game.is_over,
            'winners': game.winners,
        }

        return message

    def _get_history(self, game):
        return [
            [self._get_action_message(action) for action in player.history]
            for player in game.players]

    def _send_all(self, message, excluded_players=set()):  # pragma: no cover
        for player_id in self._cache.get_players_ids():
            player = self._clients.get(player_id, None)
            if player is not None and player_id not in excluded_players:
                player.sendMessage(message)

    def _send_all_others(self, message):  # pragma: no cover
        self._send_all(message, excluded_players=set([self.id]))

    def _send_to(self, message, id):  # pragma: no cover
        if id in self._clients:
            self._clients[id].sendMessage(message)

    def _format_error_to_display(self, message, format_opt={}):  # pragma: no cover
        return {'error_to_display': self._get_error(message, format_opt)}

    def _get_error(self, message, format_opt):  # pragma: no cover
        return self._error_messages.get(message, message).format(**format_opt)

    def _send_error(self, message, format_opt={}):  # pragma: no cover
        self.sendMessage(self._format_error(message, format_opt))

    def _send_error_to_display(self, message, format_opt={}):  # pragma: no cover
        self.sendMessage(self._format_error_to_display(message, format_opt))

    def _send_all_error(self, message, format_opt={}):  # pragma: no cover
        self._send_all(self._format_error(message, format_opt))

    def _format_error(self, message, format_opt={}):  # pragma: no cover
        return {'error': self._get_error(message, format_opt)}
