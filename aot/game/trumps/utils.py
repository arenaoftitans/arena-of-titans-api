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

from dataclasses import dataclass


@dataclass(frozen=True)
class TrumpPlayedInfos:
    """Mimics the attribute of a trump.

    This way we can use this instead when updating the gauge and creating the action.
    This is required to pass the proper information of ProxyTrumps.
    """

    name: str
    description: str
    cost: int
    duration: int
    must_target_player: bool
    color: Color  # noqa: F821 postponed annotation not supported.
    initiator: Player  # noqa: F821 postponed annotation not supported.
    is_power: bool = False


def return_trump_infos(func):
    def wrapper(trump, *args, **kwargs):
        func(trump, *args, **kwargs)
        return TrumpPlayedInfos(
            name=trump.name,
            description=trump.description,
            cost=trump.cost,
            duration=trump.duration,
            must_target_player=trump.must_target_player,
            color=trump.color,
            initiator=trump.initiator,
        )

    return wrapper
