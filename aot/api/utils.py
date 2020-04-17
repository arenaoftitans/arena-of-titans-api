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
import dataclasses
from enum import Enum
from typing import Dict, List, Optional

import bleach


class AotError(Exception):
    def __init__(self, msg, infos=None):
        super().__init__(msg)
        if infos is None:
            self.infos = {}
        else:
            self.infos = infos


class AotErrorToDisplay(AotError):
    pass


class AotFatalError(AotError):
    def __init__(self, msg, infos=None):
        super().__init__(msg, infos)


class AotFatalErrorToDisplay(AotFatalError, AotErrorToDisplay):
    pass


class MustNotSaveGameError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class WsResponse:
    future_message: Optional[asyncio.Future] = None
    include_number_connected_clients: bool = False
    send_to_all: List[dict] = dataclasses.field(default_factory=list)
    send_to_all_others: List[dict] = dataclasses.field(default_factory=list)
    # This is a mapping of player_id and the messages to send to the player.
    send_to_each_players: Dict[str, List[dict]] = dataclasses.field(default_factory=dict)
    send_to_current_player: List[dict] = dataclasses.field(default_factory=list)
    send_debug: List[dict] = dataclasses.field(default_factory=list)

    def add_debug_message(self, message):
        return dataclasses.replace(self, send_debug=message)

    def add_future_message(self, future):
        return dataclasses.replace(self, future_message=future)


class RequestTypes(Enum):
    CREATE_LOBBY = "CREATE_LOBBY"
    JOIN_GAME = "JOIN_GAME"
    UPDATE_SLOT = "UPDATE_SLOT"
    CREATE_GAME = "CREATE_GAME"
    SLOT_UPDATED = "SLOT_UPDATED"
    SPECIAL_ACTION_NOTIFY = "SPECIAL_ACTION_NOTIFY"
    SPECIAL_ACTION_PLAY = "SPECIAL_ACTION_PLAY"
    SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS = "SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS"
    PLAY_CARD = "PLAY_CARD"
    VIEW_POSSIBLE_SQUARES = "VIEW_POSSIBLE_SQUARES"
    PLAY_TRUMP = "PLAY_TRUMP"
    GAME_UPDATED = "GAME_UPDATED"
    PLAYER_UPDATED = "PLAYER_UPDATED"
    RECONNECT = "RECONNECT"


class SlotState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    RESERVED = "RESERVED"
    TAKEN = "TAKEN"
    AI = "AI"


def sanitize(string):
    return bleach.clean(string, tags=[], strip=True)
