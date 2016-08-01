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
import logging

from abc import abstractmethod
from aot.api.utils import (
    AotError,
    AotErrorToDisplay,
    to_json,
    RequestTypes,
)
from autobahn.asyncio.websocket import WebSocketServerProtocol


class AotWs(WebSocketServerProtocol):
    # Class variables.
    DISCONNECTED_TIMEOUT_WAIT = 10
    _clients = {}
    _disconnect_timeouts = {}

    # Instance variable
    _loop = None
    _message = None
    _rt = ''

    def onMessage(self, payload, isBinary):
        try:
            self._message = json.loads(payload.decode('utf-8'))
            self._rt = self._message.get('rt', '')
            if self._rt not in RequestTypes:
                raise AotError('unknown_request', {'rt': self._rt})
            elif self._creating_new_game:
                self._create_new_game()
            elif self._creating_game:
                self._process_create_game_request()
            else:
                self._process_play_request()
        except AotError as e:
            self._send_error(str(e), e.infos)
        except AotErrorToDisplay as e:
            self._send_error_to_display(str(e), e.infos)
        except Exception as e:
            logging.exception('onMessage')

    @property
    @abstractmethod
    def _creating_new_game(self):
        pass

    @abstractmethod
    def _create_new_game(self):
        pass

    @property
    @abstractmethod
    def _creating_game(self):
        pass

    @abstractmethod
    def _process_create_game_request(self):
        pass

    @abstractmethod
    def _process_play_request(self):
        pass

    def sendMessage(self, message):
        if isinstance(message, dict):
            message = json.dumps(message, default=to_json)
        message = message.encode('utf-8')
        if isinstance(message, bytes):
            super().sendMessage(message)

    def onOpen(self):
        self.id = self._wskey
        self._clients[self.id] = self
        self._loop = asyncio.get_event_loop()
        self._set_up_connection_keep_alive()

    def onClose(self, wasClean, code, reason):
        if self._cache is not None:
            self._disconnect_timeouts[self.id] = self._loop.call_later(
                self.DISCONNECTED_TIMEOUT_WAIT,
                self._disconnect_player
            )

        if self.id in self._clients:
            del self._clients[self.id]

    def onPong(self, payload):
        self._set_up_connection_keep_alive()

    def _set_up_connection_keep_alive(self):
        self._loop.call_later(5, self.sendPing)

    def _send_all(self, message, excluded_players=set()):
        for player_id in self._cache.get_players_ids():
            player = self._clients.get(player_id, None)
            if player is not None and player_id not in excluded_players:
                player.sendMessage(message)

    def _send_all_others(self, message):
        self._send_all(message, excluded_players=set([self.id]))

    def _send_to(self, message, id):
        if id in self._clients:
            self._clients[id].sendMessage(message)

    def _format_error_to_display(self, message, format_opt={}):
        return {'error_to_display': self._get_error(message, format_opt)}

    def _get_error(self, message, format_opt):
        return self._error_messages.get(message, message).format(**format_opt)

    def _send_error(self, message, format_opt={}):
        self.sendMessage(self._format_error(message, format_opt))

    def _send_error_to_display(self, message, format_opt={}):
        self.sendMessage(self._format_error_to_display(message, format_opt))

    def _send_all_error(self, message, format_opt={}):
        self._send_all(self._format_error(message, format_opt))

    def _format_error(self, message, format_opt={}):
        return {'error': self._get_error(message, format_opt)}
