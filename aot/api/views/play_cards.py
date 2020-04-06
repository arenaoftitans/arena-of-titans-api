#
#  Copyright (C) 2015-2020 by Arena of Titans Contributors.
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
from ..utils import AotErrorToDisplay
from .play_utils import get_square


def view_possible_squares(game, request):
    card = _get_card(game, request)
    if card is None:
        raise AotErrorToDisplay("wrong_card")

    possible_squares = game.view_possible_squares(card)
    return possible_squares


def play_card(game, request):
    # If this action completes the turn, it may not be the active player
    # once the card has been played.
    player_that_played_the_card = game.active_player
    has_special_actions = False
    if request.get("pass", False):
        game.pass_turn()
    elif request.get("discard", False):
        card = _get_card(game, request)
        if card is None:
            raise AotErrorToDisplay("wrong_card")
        game.discard(card)
    else:
        card = _get_card(game, request)
        square = get_square(game, request)
        if card is None:
            raise AotErrorToDisplay("wrong_card")
        elif square is None or not game.can_move(card, square):
            raise AotErrorToDisplay("wrong_square")
        has_special_actions = game.play_card(card, square)

    return player_that_played_the_card, has_special_actions


def _get_card(game, request):
    name = request.get("card_name", None)
    color = request.get("card_color", None)
    return game.active_player.get_card(name, color)
