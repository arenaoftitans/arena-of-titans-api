#
#  Copyright (C) 2015-2020 by Last Run Contributors.
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

from .create_game import create_game, create_lobby, free_slot, join_game, update_slot
from .play_actions import play_action, view_possible_actions
from .play_cards import play_card, view_possible_squares
from .play_trump import play_trump
from .reconnect import reconnect_to_game, reconnect_to_lobby

__all__ = [
    # Create game views.
    free_slot.__name__,
    create_lobby.__name__,
    create_game.__name__,
    join_game.__name__,
    update_slot.__name__,
    # Play game views.
    play_action.__name__,
    view_possible_actions.__name__,
    play_card.__name__,
    view_possible_squares.__name__,
    play_trump.__name__,
    # Reconnect.
    reconnect_to_lobby.__name__,
    reconnect_to_game.__name__,
]
