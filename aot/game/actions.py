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

from __future__ import annotations

import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class Action:
    initiator: Optional[Player]  # noqa: F821 undefined name
    target: Player = None  # noqa: F821 undefined name
    description: str = ""
    special_action: Trump = None  # noqa: F821 undefined name
    card: Card = None  # noqa: F821 undefined name
    trump: Trump = None  # noqa: F821 undefined name


nothing_has_happened_action = Action(initiator=None, description="nothing_happened")
