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
from ..serializers import get_player_states_by_ids
from ..utils import AotErrorToDisplay, RequestTypes, WsResponse
from .play_utils import get_square


def view_possible_squares(request, game):
    card = _get_card(request, game)
    if card is None:
        raise AotErrorToDisplay("wrong_card")

    possible_squares = game.view_possible_squares(card)
    return WsResponse(
        send_to_current_player=[
            {"rt": RequestTypes.VIEW_POSSIBLE_SQUARES, "possible_squares": possible_squares}
        ]
    )


def play_card(request, game):
    # If this action completes the turn, it may not be the active player
    # once the card has been played.
    player_that_played_the_card = game.active_player
    has_special_actions = False
    if request.get("pass", False):
        game.pass_turn()
    elif request.get("discard", False):
        card = _get_card(request, game)
        if card is None:
            raise AotErrorToDisplay("wrong_card")
        game.discard(card)
    else:
        card = _get_card(request, game)
        square = get_square(request, game)
        if card is None:
            raise AotErrorToDisplay("wrong_card")
        elif square is None or not game.can_move(card, square):
            raise AotErrorToDisplay("wrong_square")
        has_special_actions = game.play_card(card, square)

    send_to_current_player = []
    if has_special_actions:
        send_to_current_player = [
            {
                "rt": RequestTypes.SPECIAL_ACTION_NOTIFY,
                "special_action_name": game.active_player.name_next_special_action,
            }
        ]

    return WsResponse(
        send_to_current_player=send_to_current_player,
        send_to_all=[
            {
                "rt": RequestTypes.PLAYER_PLAYED,
                "player_index": player_that_played_the_card.index,
                "new_square": {
                    "x": player_that_played_the_card.current_square.x,
                    "y": player_that_played_the_card.current_square.y,
                },
                "has_remaining_moves_to_play": player_that_played_the_card.has_remaining_moves_to_play,  # noqa: E501
                "trumps_statuses": player_that_played_the_card.trumps_statuses,
                "can_power_be_played": player_that_played_the_card.can_power_be_played,
                "last_action": {
                    "description": game.last_action.description,
                    "card": game.last_action.card,
                    "trump": game.last_action.trump,
                    "special_action": game.last_action.special_action,
                    "player_name": game.last_action.player_name,
                    "target_name": game.last_action.target_name,
                    "target_index": game.last_action.target_index,
                    "player_index": game.last_action.player_index,
                },
                "game_over": game.is_over,
                "winners": game.winners,
            }
        ],
        send_to_each_players=get_player_states_by_ids(game),
    )


def _get_card(request, game):
    name = request.get("card_name", None)
    color = request.get("card_color", None)
    return game.active_player.get_card(name, color)
