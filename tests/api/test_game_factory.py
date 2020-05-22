################################################################################
# Copyright (C) 2015-2020 by Last Run Contributors.
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

from aot.api.game_factory import build_cards_list
from aot.game.config import TEST_CONFIG
from aot.game.trumps.special_actions import SpecialAction


def test_get_cards_list():
    cards = build_cards_list(TEST_CONFIG, None)
    for card in cards:
        if card.name == "Bishop":
            assert len(card.colors) == 2
        elif card.name == "Assassin":
            assert len(card._special_actions) == 1
            action = card._special_actions[0]
            assert isinstance(action, SpecialAction)
