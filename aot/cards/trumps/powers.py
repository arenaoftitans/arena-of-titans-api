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

from copy import deepcopy

from .constants import TargetTypes
from .trumps import (
    AddSpecialActionsToCard,
    CannotBeAffectedByTrumps,
    ChangeSquare,
    ModifyCardColors,
    ModifyCardNumberMoves,
    PreventTrumpAction,
    Trump,
)
from .utils import TrumpPlayedInfos


class Power(Trump):
    def __init__(
        self,
        duration=0,
        cost=5,
        description='',
        must_target_player=False,
        name='',
        passive=False,
        trump_cost_delta=0,
        **kwargs,
    ):
        super().__init__(
            duration=duration,
            cost=cost,
            description=description,
            must_target_player=must_target_player,
            name=name,
            **kwargs,
        )
        self._passive = passive
        self._trump_cost_delta = trump_cost_delta
        if self._passive:
            self._duration = float('inf')

    def setup(self, trumps):
        if not self.passive:
            return

        # We expect a list of SimpleTrump
        for trump in trumps:
            trump.args['cost'] += self._trump_cost_delta

    def turn_teardown(self):
        '''Call this tearndown at the end of every turn.'''
        # By default, there is nothing to do.
        pass

    def clone(self):
        return deepcopy(self)

    @property
    def passive(self):
        return self._passive

    @property
    def trump_cost_delta(self):
        return self._trump_cost_delta


class CannotBeAffectedByTrumpsPower(CannotBeAffectedByTrumps, Power):
    pass


class ChangeSquarePower(ChangeSquare, Power):
    pass


class ModifyCardColorsPower(ModifyCardColors, Power):
    pass


class ModifyCardNumberMovesPower(ModifyCardNumberMoves, Power):
    pass


class PreventTrumpActionPower(PreventTrumpAction, Power):
    pass


class AddSpecialActionsToCardPower(AddSpecialActionsToCard, Power):
    pass


class StealPowerPower(Power):
    STOLEN_POWER_COST = 0
    STEALTH_DURATION = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stolen_power = None
        self._trumps_associated_with_passive_stolen_power = []
        self._theft_duration_left = self.STEALTH_DURATION

    def affect(self, *, power=None, **kwargs):
        if self._stolen_power:
            return self._affect_from_stolen_power(**kwargs)
        else:
            return self._steal_power(power, kwargs['player'])

    def _affect_from_stolen_power(self, **kwargs):
        self._theft_duration_left -= 1
        stolen_power_infos = self._stolen_power.affect(**kwargs)
        infos = TrumpPlayedInfos(
            name=stolen_power_infos.name,
            description=stolen_power_infos.description,
            cost=self.cost,
            duration=self.duration,
            must_target_player=stolen_power_infos.must_target_player,
            color=stolen_power_infos.color,
            initiator=stolen_power_infos.initiator,
        )
        return infos

    def _steal_power(self, power, player):
        infos = TrumpPlayedInfos(
            name=self.name,
            description=self.description,
            cost=self.cost,
            duration=self.duration,
            must_target_player=self.must_target_player,
            color=self.color,
            initiator=self.initiator,
            is_power=True,
        )
        self._stolen_power = power
        self._trumps_associated_with_passive_stolen_power = player.rw_available_trumps
        self._stolen_power.setup(self._trumps_associated_with_passive_stolen_power)
        self._theft_duration_left = self.STEALTH_DURATION
        if self._stolen_power.passive:
            # This is meant to allow passive powers to be stolen until the next turn,
            # since it is immediately activated.
            self._theft_duration_left += 1
            self.affect(player=player)
        return infos

    def turn_teardown(self):
        if self._stolen_power is None:
            return
        elif self._theft_duration_left > 0:
            return

        # We expect a list of SimpleTrump
        for trump in self._trumps_associated_with_passive_stolen_power:
            trump.args['cost'] -= self.trump_cost_delta

        self._stolen_power = None
        self._trumps_associated_with_passive_stolen_power = []

    def clone(self):
        # When this power it played, we need to mutate it to take into account the stealth of the
        # power. Thus we don't want to clone it.
        return self

    @property
    def color(self):
        if self._stolen_power is not None:
            return self._stolen_power.color
        return super().color

    @property
    def cost(self):
        if self._stolen_power is not None:
            return self.STOLEN_POWER_COST
        return super().cost

    @cost.setter
    def cost(self, value):
        if self._stolen_power is not None:
            self._stolen_power.cost = value
        super(self.__class__, self.__class__).cost.fset(self, value)

    @property
    def description(self):
        if self._stolen_power is not None:
            return self._stolen_power.description
        return super().description

    @property
    def duration(self):
        if self._stolen_power is not None:
            return self._stolen_power.duration
        return super().duration

    @duration.setter
    def duration(self, value):
        if self._stolen_power is not None:
            self._stolen_power.duration = value
        super(self.__class__, self.__class__).duration.fset(self, value)

    @property
    def must_target_player(self):
        if self._stolen_power is not None:
            return self._stolen_power.must_target_player
        return super().must_target_player

    @property
    def name(self):
        if self._stolen_power is not None:
            return self._stolen_power.name
        return super().name

    @property
    def initiator(self):
        if self._stolen_power is not None:
            return self._stolen_power.initiator
        return super().initiator

    @initiator.setter
    def initiator(self, initiator):
        if self._stolen_power is not None:
            self._stolen_power.initiator = initiator
        super(self.__class__, self.__class__).initiator.fset(self, initiator)

    @property
    def passive(self):
        if self._stolen_power is not None:
            return self._stolen_power.passive
        return super().passive

    @property
    def target_type(self):
        if self._stolen_power is not None:
            return self._stolen_power.target_type
        return TargetTypes.trump

    @property
    def trump_cost_delta(self):
        if self._stolen_power is not None:
            return self._stolen_power.trump_cost_delta
        return super().trump_cost_delta
