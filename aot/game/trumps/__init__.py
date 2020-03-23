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

from .gauge import Gauge
from .powers import (
    AddSpecialActionsToCardPower,
    CannotBeAffectedByTrumpsPower,
    ChangeSquarePower,
    ModifyCardColorsPower,
    ModifyCardNumberMovesPower,
    Power,
    PreventTrumpActionPower,
    StealPowerPower,
    VoidPower,
)
from .special_actions import TeleportSpecialAction
from .trumps import (
    CannotBeAffectedByTrumps,
    ChangeSquare,
    ModifyCardColors,
    ModifyCardNumberMoves,
    ModifyNumberMoves,
    ModifyTrumpDurations,
    PreventTrumpAction,
    RemoveColor,
    Teleport,
    Trump,
)
from .utils import SpecialActionsList, TrumpsList

special_action_type_to_class = {
    "Teleport": TeleportSpecialAction,
}

power_type_to_class = {
    "AddSpecialActionsToCard": AddSpecialActionsToCardPower,
    "CannotBeAffectedByTrumps": CannotBeAffectedByTrumpsPower,
    "ChangeSquare": ChangeSquarePower,
    "ModifyCardColors": ModifyCardColorsPower,
    "ModifyCardNumberMoves": ModifyCardNumberMovesPower,
    "PreventTrumpAction": PreventTrumpActionPower,
    "StealPower": StealPowerPower,
}

trump_type_to_class = {
    "CannotBeAffectedByTrumps": CannotBeAffectedByTrumps,
    "ChangeSquare": ChangeSquare,
    "ModifyNumberMoves": ModifyNumberMoves,
    "ModifyTrumpDurations": ModifyTrumpDurations,
    "PreventTrumpAction": PreventTrumpAction,
    "RemoveColor": RemoveColor,
    "Teleport": Teleport,
}


def create_action_from_description(action_description, color=None):
    action_cls = special_action_type_to_class[action_description["type"]]
    direct_args = action_description["args"].copy()
    trump_args = direct_args.pop("trump_args").copy()
    trump_args["color"] = color
    return action_cls(**direct_args, trump_args=trump_args)


__all__ = [
    power_type_to_class,
    special_action_type_to_class,
    # Powers
    "ModifyCardColorsPower",
    "ModifyCardNumberMovesPower",
    "VoidPower",
    # Power utils
    "Power",
    # Trumps
    "CannotBeAffectedByTrumps",
    "ChangeSquare",
    "ModifyCardColors",
    "ModifyCardNumberMoves",
    "ModifyNumberMoves",
    "ModifyTrumpDurations",
    "RemoveColor",
    "Teleport",
    # Trump utils
    "Gauge",
    "Trump",
    "TrumpsList",
    "SpecialActionsList",
]
