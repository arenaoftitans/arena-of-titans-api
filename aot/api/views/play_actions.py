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

from ..serializers import get_global_game_message, get_private_player_messages_by_ids
from ..utils import AotError, AotErrorToDisplay, RequestTypes, WsResponse
from .play_utils import get_square


def view_possible_actions(request, game):
    action = _get_action(request, game)
    target = _get_target(request, game)

    return WsResponse(
        send_to_current_player=[
            {
                "rt": RequestTypes.SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS,
                "request": {
                    "special_action_name": action.name,
                    "possible_squares": action.view_possible_squares(target, game.board)
                    if action.require_target_square
                    else [],
                },
            },
        ]
    )


def play_action(request, game):
    action = _get_action(request, game)
    target = None
    if request.get("cancel", False):
        game.cancel_special_action(action)
    else:
        target = _get_target(request, game)
        _play_special_action_on_target(request, game, action, target)

    if not game.active_player.has_special_actions:
        game.complete_special_actions()

    messages_for_current_player = []
    message_for_each_players = {}
    if game.active_player.has_special_actions:
        messages_for_current_player = [
            {
                "rt": RequestTypes.SPECIAL_ACTION_NOTIFY,
                "special_action_name": game.active_player.name_next_special_action,
            }
        ]
    else:
        message_for_each_players = get_private_player_messages_by_ids(game)

    WsResponse(
        send_to_all=[get_global_game_message(game)],
        send_to_current_player=messages_for_current_player,
        send_to_each_players=message_for_each_players,
    )


def _get_action(request, game):
    action_name = request.get("special_action_name", None)
    action_color = request.get("special_action_color", None)
    target_index = request.get("target_index", None)
    allow_no_target = request.get("cancel", False)

    if not action_name:
        raise AotError("missing_action_name")
    elif target_index is None and not allow_no_target:
        raise AotError("missing_action_target")

    try:
        return game.active_player.special_actions[action_name, action_color]
    except IndexError:
        raise AotError("wrong_action")
    except TypeError as e:
        if str(e) == "'NoneType' object is not subscriptable":
            raise AotError("no_action")
        raise e


def _get_target(request, game):
    target_index = request.get("target_index", None)
    return game.players[target_index]


def _play_special_action_on_target(request, game, action, target):
    context = {}
    if action.require_target_square:
        context["square"] = get_square(request, game)
        context["board"] = game.board
        if context["square"] is None:
            raise AotErrorToDisplay("wrong_square")

    game.play_special_action(action, target=target, context=context)
    last_action = game.active_player.last_action
    game.add_action(last_action)
