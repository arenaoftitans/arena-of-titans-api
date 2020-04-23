################################################################################
# Copyright (C) 2015-2017 by Arena of Titans Contributors.
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

from dataclasses import dataclass, field

from .constants import EffectTypes
from .trumps import (
    AddSpecialActionsToCard,
    CannotBeAffectedByTrumps,
    ChangeSquare,
    ModifyCardColors,
    ModifyCardNumberMoves,
    PreventTrumpAction,
    StealPower,
    VoidTrump,
)
from .utils import TrumpsList


@dataclass(frozen=True)
class Power:
    passive: bool = False
    trump_cost_delta: int = 0
    trump_args: dict = field(default_factory=dict)
    trump_cls: type = None
    require_square_target: bool = False

    def allow_trump_to_affect(self, trump):
        return self.trump.allow_trump_to_affect(trump)

    def create_effect(self, *, initiator, target, context):
        return self.trump.create_effect(
            initiator=initiator, target=target, context=context, effect_type=EffectTypes.power
        )

    def setup(self, trumps):
        if not self.passive:
            return trumps

        return TrumpsList(trump.update_cost(trump.cost + self.trump_cost_delta) for trump in trumps)

    def teardown(self, trumps):
        if not self.passive:
            return trumps

        return TrumpsList(trump.update_cost(trump.cost - self.trump_cost_delta) for trump in trumps)

    @property
    def apply_on_initiator(self):
        return self.trump.apply_on_initiator

    @property
    def duration(self):
        if self.passive:
            return float("inf")
        return self.trump.duration

    @property
    def color(self):
        return self.trump.color

    @property
    def cost(self):
        return self.trump.cost

    @property
    def must_target_player(self):
        return self.trump.must_target_player

    @property
    def name(self):
        return self.trump.name

    @property
    def trump(self):
        trump_args = self.trump_args.copy()
        if self.passive:
            trump_args["duration"] = float("inf")

        return self.trump_cls(**trump_args)

    def __str__(self):
        return f"{self.__class__}<trump={self.trump}, passive={self.passive}>"

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class CannotBeAffectedByTrumpsPower(Power):
    trump_cls: type = CannotBeAffectedByTrumps


@dataclass(frozen=True)
class ChangeSquarePower(Power):
    trump_cls: type = ChangeSquare
    require_square_target: bool = True


@dataclass(frozen=True)
class ModifyCardColorsPower(Power):
    trump_cls: type = ModifyCardColors


@dataclass(frozen=True)
class ModifyCardNumberMovesPower(Power):
    trump_cls: type = ModifyCardNumberMoves


@dataclass(frozen=True)
class PreventTrumpActionPower(Power):
    trump_cls: type = PreventTrumpAction

    def setup(self, trumps):
        trumps = super().setup(trumps)

        return TrumpsList(
            trump.update_prevent_trumps_to_modify(self.trump.prevent_trumps_to_modify)
            if trump.name in self.trump.enable_for_trumps
            else trump
            for trump in trumps
        )


@dataclass(frozen=True)
class AddSpecialActionsToCardPower(Power):
    trump_cls: type = AddSpecialActionsToCard


@dataclass(frozen=True)
class StealPowerPower(Power):
    trump_cls: type = StealPower

    def __post_init__(self):
        if not self.passive:
            # If the power is not passive, increase its duration by 1 to allow the user to play
            # it during the next turn.
            self.trump_args["duration"] = self.trump_args.get("duration", 0) + 1


@dataclass(frozen=True)
class VoidPower(Power):
    trump_cls: type = VoidTrump
