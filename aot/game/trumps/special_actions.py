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

from dataclasses import dataclass, field

from . import trumps
from .constants import EffectTypes


@dataclass(frozen=True)
class SpecialAction:
    trump_args: dict = field(default_factory=dict)
    trump_cls: type = None

    def create_effect(self, *, initiator, target, context):
        return self.trump.create_effect(
            initiator=initiator,
            target=target,
            context=context,
            effect_type=EffectTypes.special_action,
        )

    @property
    def name(self):
        return self.trump.name

    @property
    def trump(self):
        return self.trump_cls(**self.trump_args)

    @property
    def require_target_square(self):
        return False


@dataclass(frozen=True)
class TeleportSpecialAction(SpecialAction):
    trump_cls: type = trumps.Teleport

    def view_possible_squares(self, player, board):
        effect = self.create_effect(initiator=player, target=player, context={"board": board})
        return effect.view_possible_squares()

    @property
    def require_target_square(self):
        return True
