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
from aot.game.trumps.exceptions import (
    GaugeTooLowToPlayTrumpError,
    MaxNumberAffectingTrumpsError,
    MaxNumberTrumpPlayedError,
)

from ..serializers import get_global_game_message, get_private_player_state
from ..utils import AotError, AotErrorToDisplay, WsResponse


def play_trump(request, game):
    try:
        trump = _get_trump(request, game)
    except IndexError:
        raise AotError("wrong_trump")

    target = _get_trump_target(request, game, trump)
    context = _get_trump_context(request, game)

    _play_trump_with_target(game, trump, target, context)

    return WsResponse(
        send_to_all=[get_global_game_message(game)],
        send_to_current_player=[get_private_player_state(game.active_player)],
    )


def _get_trump(request, game):
    return game.active_player.get_trump(request.get("name", None), request.get("color", None))


def _get_trump_target(request, game, trump):
    target_index = request.get("target_index", None)
    if trump.must_target_player and target_index is None:
        raise AotError("missing_trump_target")
    elif not trump.must_target_player:
        target_index = game.active_player.index

    try:
        return game.get_player_by_index(target_index)
    except IndexError:
        raise AotError("The target of this trump does not exist")


def _get_trump_context(request, game):
    context = {
        "board": game.board,
    }
    if "square" in request:
        context["square"] = {
            "x": request["square"]["x"],
            "y": request["square"]["y"],
            "color": request["square"]["color"],
        }

    return context


def _play_trump_with_target(game, trump, target, context):
    try:
        game.play_trump(trump, target, context)
    except GaugeTooLowToPlayTrumpError:
        raise AotError("gauge_too_low")
    except MaxNumberTrumpPlayedError:
        raise AotError(
            "max_number_played_trumps", infos={"num": game.active_player.MAX_NUMBER_TRUMPS_PLAYED},
        )
    except MaxNumberAffectingTrumpsError:
        raise AotErrorToDisplay(
            "max_number_trumps", {"num": target.MAX_NUMBER_AFFECTING_TRUMPS},
        )
