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

from ..utils import AotError, AotErrorToDisplay
from .play_utils import get_square


def view_possible_actions(game, request):
    action = _get_action(game, request)
    target = _get_target(game, request)
    message = {
        "special_action_name": action.name,
    }
    if action.require_target_square:
        message["possible_squares"] = action.view_possible_squares(target, game.board)

    return message


def play_action(game, request):
    action = _get_action(game, request)
    if request.get("cancel", False):
        game.cancel_special_action(action)
        return False, None

    target = _get_target(game, request)
    _play_special_action_on_target(game, request, action, target)
    return True, target


def _get_action(game, request):
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


def _get_target(game, request):
    target_index = request.get("target_index", None)
    return game.players[target_index]


def _play_special_action_on_target(game, request, action, target):
    context = {}
    if action.require_target_square:
        context["square"] = get_square(game, request)
        context["board"] = game.board
        if context["square"] is None:
            raise AotErrorToDisplay("wrong_square")

    game.play_special_action(action, target=target, context=context)
    last_action = game.active_player.last_action
    game.add_action(last_action)
