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

import pickle

from aot.test import api_cache
from unittest.mock import MagicMock


def test_create_new_game(api_cache):
    slots = []

    def add_slot_cache_side_effect(key, slot):
        slot = pickle.loads(slot)
        assert key == 'slots:game_id'
        assert slot['index'] == len(slots)
        if len(slots) == 0:
            assert slot['player_id'] == 'player_id'
        else:
            assert not slot['player_id']

        slots.append(slot)

    api_cache._cache.rpush = MagicMock(side_effect=add_slot_cache_side_effect)
    api_cache.get_slots = MagicMock(return_value=slots)

    api_cache.create_new_game()

    assert api_cache._cache.hset.call_count == 3
    assert api_cache._cache.rpush.call_count == 8


def test_number_taken_slots(api_cache):
    slots = [{'state': 'TAKEN'}, {'state': 'IA'}, {'state': 'AI'}]
    api_cache.get_slots = MagicMock(return_value=slots)
    assert api_cache.number_taken_slots() == 2
