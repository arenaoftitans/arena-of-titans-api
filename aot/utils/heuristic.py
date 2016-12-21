################################################################################
# Copyright (C) 2016 by Arena of Titans Contributors.
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

from aot.utils import SimpleEnumMeta
from collections import namedtuple


BranchDistance = namedtuple('BranchDistance', 'distance side')


class Side(metaclass=SimpleEnumMeta):
    RIGHT = ()
    LEFT = ()


DISTANCE_BRANCH_TO_BRANCH = {
    0: {
        5: BranchDistance(distance=3, side=Side.LEFT),
        6: BranchDistance(distance=2, side=Side.LEFT),
        7: BranchDistance(distance=1, side=Side.LEFT),
        0: BranchDistance(distance=0, side=None),
        1: BranchDistance(distance=1, side=Side.RIGHT),
        2: BranchDistance(distance=2, side=Side.RIGHT),
        3: BranchDistance(distance=3, side=Side.RIGHT),
        4: BranchDistance(distance=4, side=Side.RIGHT),
    },
    1: {
        6: BranchDistance(distance=3, side=Side.LEFT),
        7: BranchDistance(distance=2, side=Side.LEFT),
        0: BranchDistance(distance=1, side=Side.LEFT),
        1: BranchDistance(distance=0, side=None),
        2: BranchDistance(distance=1, side=Side.RIGHT),
        3: BranchDistance(distance=2, side=Side.RIGHT),
        4: BranchDistance(distance=3, side=Side.RIGHT),
        5: BranchDistance(distance=4, side=Side.RIGHT),
    },
    2: {
        7: BranchDistance(distance=3, side=Side.LEFT),
        0: BranchDistance(distance=2, side=Side.LEFT),
        1: BranchDistance(distance=1, side=Side.LEFT),
        2: BranchDistance(distance=0, side=None),
        3: BranchDistance(distance=1, side=Side.RIGHT),
        4: BranchDistance(distance=2, side=Side.RIGHT),
        5: BranchDistance(distance=3, side=Side.RIGHT),
        6: BranchDistance(distance=4, side=Side.RIGHT),
    },
    3: {
        0: BranchDistance(distance=3, side=Side.LEFT),
        1: BranchDistance(distance=2, side=Side.LEFT),
        2: BranchDistance(distance=1, side=Side.LEFT),
        3: BranchDistance(distance=0, side=None),
        4: BranchDistance(distance=1, side=Side.RIGHT),
        5: BranchDistance(distance=2, side=Side.RIGHT),
        6: BranchDistance(distance=3, side=Side.RIGHT),
        7: BranchDistance(distance=4, side=Side.RIGHT),
    },
    4: {
        1: BranchDistance(distance=3, side=Side.LEFT),
        2: BranchDistance(distance=2, side=Side.LEFT),
        3: BranchDistance(distance=1, side=Side.LEFT),
        4: BranchDistance(distance=0, side=None),
        5: BranchDistance(distance=1, side=Side.RIGHT),
        6: BranchDistance(distance=2, side=Side.RIGHT),
        7: BranchDistance(distance=3, side=Side.RIGHT),
        0: BranchDistance(distance=4, side=Side.RIGHT),
    },
    5: {
        2: BranchDistance(distance=3, side=Side.LEFT),
        3: BranchDistance(distance=2, side=Side.LEFT),
        4: BranchDistance(distance=1, side=Side.LEFT),
        5: BranchDistance(distance=0, side=None),
        6: BranchDistance(distance=1, side=Side.RIGHT),
        7: BranchDistance(distance=2, side=Side.RIGHT),
        0: BranchDistance(distance=3, side=Side.RIGHT),
        1: BranchDistance(distance=4, side=Side.RIGHT),
    },
    6: {
        3: BranchDistance(distance=3, side=Side.LEFT),
        4: BranchDistance(distance=2, side=Side.LEFT),
        5: BranchDistance(distance=1, side=Side.LEFT),
        6: BranchDistance(distance=0, side=None),
        7: BranchDistance(distance=1, side=Side.RIGHT),
        0: BranchDistance(distance=2, side=Side.RIGHT),
        1: BranchDistance(distance=3, side=Side.RIGHT),
        2: BranchDistance(distance=4, side=Side.RIGHT),
    },
    7: {
        4: BranchDistance(distance=3, side=Side.LEFT),
        5: BranchDistance(distance=2, side=Side.LEFT),
        6: BranchDistance(distance=1, side=Side.LEFT),
        7: BranchDistance(distance=0, side=None),
        0: BranchDistance(distance=1, side=Side.RIGHT),
        1: BranchDistance(distance=2, side=Side.RIGHT),
        2: BranchDistance(distance=3, side=Side.RIGHT),
        3: BranchDistance(distance=4, side=Side.RIGHT),
    },
}


CORRECT_X_LEFT = {
    0: 4,
    1: 3,
    2: 2,
    3: 1,
}
