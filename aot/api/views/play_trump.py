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
    TrumpHasNoEffectError,
)

from ..utils import AotError, AotErrorToDisplay, RequestTypes


def play_trump(game, request):
    try:
        trump = _get_trump(game, request)
    except IndexError:
        raise AotError("wrong_trump")

    target = _get_trump_target(game, trump, request)
    context = _get_trump_context(game, trump, request)

    return _play_trump_with_target(game, trump, target, context)


def _get_trump(game, request):
    return game.active_player.get_trump(request.get("name", None), request.get("color", None))


def _get_trump_target(game, trump, request):
    target_index = request.get("target_index", None)
    if trump.must_target_player and target_index is None:
        raise AotError("missing_trump_target")
    elif not trump.must_target_player:
        target_index = game.active_player.index

    try:
        return game.players[target_index]
    except IndexError:
        raise AotError("The target of this trump does not exist")


def _get_trump_context(game, trump, request):
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
    except TrumpHasNoEffectError:
        game.add_action(game.active_player.last_action)
        rt = RequestTypes.TRUMP_HAS_NO_EFFECT
    else:
        game.add_action(game.active_player.last_action)
        rt = RequestTypes.PLAY_TRUMP

    return target, context, rt
