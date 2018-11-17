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

from .trumps import (
    AddSpecialActionsToCard,
    CannotBeAffectedByTrumps,
    ChangeSquare,
    ModifyCardColors,
    ModifyCardNumberMoves,
    PreventTrumpAction,
    Trump,
)


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
        if self.passive:
            self._duration = float('inf')

    def setup(self, trumps):
        if not self.passive:
            return

        # We expect a list of SimpleTrump
        for trump in trumps:
            trump.args['cost'] += self._trump_cost_delta

    @property
    def passive(self):
        return self._passive


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
