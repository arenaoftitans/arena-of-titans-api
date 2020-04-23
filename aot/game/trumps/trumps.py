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

import random
from dataclasses import dataclass, replace
from typing import FrozenSet, Iterable, Tuple

from ..board import Color
from . import effects
from .constants import EffectTypes


@dataclass(frozen=True)
class Trump:
    trump_effect_cls: type = None

    name: str = ""
    description: str = ""
    duration: int = 0
    cost: int = 5
    must_target_player: bool = False
    color: Color = None
    colors: Iterable[Color] = ()
    #: List of trumps names that cannot modify this trump.
    #: This is also used to force a trump to act against a CannotBeAffectedByTrumps.
    prevent_trumps_to_modify: Tuple[str] = ()
    apply_on_initiator: bool = False
    is_player_visible: bool = True

    def create_effect(self, *, initiator, target, context, effect_type=EffectTypes.trump):
        return self.trump_effect_cls(
            trump=self,
            target=target,
            initiator=initiator,
            context=context,
            effect_type=effect_type,
        )

    def allow_trump_to_affect(self, trump):
        return True

    def update_cost(self, new_cost):
        return replace(self, cost=new_cost)

    def update_prevent_trumps_to_modify(self, prevent_trumps_to_modify):
        return replace(self, prevent_trumps_to_modify=prevent_trumps_to_modify)


@dataclass(frozen=True)
class ModifyNumberMoves(Trump):
    trump_effect_cls: type = effects.ModifyNumberMovesEffect
    delta_moves: int = 0


@dataclass(frozen=True)
class ModifyCardColors(Trump):
    trump_effect_cls: type = effects.ModifyCardColorEffect
    card_names: Tuple[str] = ()


@dataclass(frozen=True)
class CannotBeAffectedByTrumps(Trump):
    trump_effect_cls: type = effects.CannotBeAffectedByTrumpsEffect
    trump_names: Tuple[str] = ()

    def allow_trump_to_affect(self, trump: Trump):
        # If trump_names is not defined, we consider that not trump can affect the player.
        if not self.trump_names:
            return False

        # ``trump.name in self._trump_names`` says the trump has no effect.
        # but ``self.name in trump._prevent_trumps_to_modify`` says
        # the trump has an effect nonetheless.
        # So we randomly pick an outcome.
        if trump.name in self.trump_names and self.name in trump.prevent_trumps_to_modify:
            return random.choice((False, True))  # noqa: S311 (random generator)

        if trump.name in self.trump_names:
            return False
        return True

    @property
    def is_affecting_all_trumps(self):
        return not self.trump_names


@dataclass(frozen=True)
class ChangeSquare(Trump):
    trump_effect_cls: type = effects.ChangeSquareEffect


@dataclass(frozen=True)
class ModifyCardNumberMoves(Trump):
    trump_effect_cls: type = effects.ModifyCardNumberMovesEffect
    delta_moves: int = 0
    card_names: Tuple[str] = ()


@dataclass(frozen=True)
class AddSpecialActionsToCard(Trump):
    trump_effect_cls: type = effects.AddSpecialActionsToCardEffect
    card_names: Tuple[str] = ()
    spectial_action_despriptions: Tuple = ()


@dataclass(frozen=True)
class ModifyTrumpDurations(Trump):
    delta_duration: int = 0
    trump_effect_cls: type = effects.ModifyTrumpDurationsEffect
    trump_names: Tuple[str] = ()


@dataclass(frozen=True)
class PreventTrumpAction(Trump):
    """Prevent the normal behavior of a trump.

    For instance with the power *Impassable*, the towers and fortresses played are immune
    to the *Ram* trump. This trump is meant to make this possible.

    Args:
        prevent_trumps_to_modify:  List of trump names that cannot be applied to
            ``enable_for_trumps``
        enable_for_trumps: List of trump names to modify. Only the trumps with these names
            will be modified and cannot be affected by ``prevent_trumps``.
    """

    trump_effect_cls: type = effects.PreventTrumpActionEffect
    prevent_trumps_to_modify: Tuple[str] = ()
    enable_for_trumps: Tuple[str] = ()


@dataclass(frozen=True)
class RemoveColor(Trump):
    trump_effect_cls: type = effects.RemoveColorEffect
    colors: FrozenSet[Color] = frozenset()


@dataclass(frozen=True)
class StealPower(Trump):
    trump_effect_cls: type = effects.StealPowerEffect
    apply_on_initiator: bool = True


@dataclass(frozen=True)
class Teleport(Trump):
    trump_effect_cls: type = effects.TeleportEffect
    distance: int = 0


@dataclass(frozen=True)
class VoidTrump(Trump):
    trump_effect_cls: type = effects.VoidEffect
