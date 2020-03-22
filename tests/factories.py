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

import factory

from aot.api.game_factory import build_cards_list
from aot.game.board import Board, Color
from aot.game.cards import Deck
from aot.game.config import TEST_CONFIG
from aot.game.player import Player
from aot.game.trumps import Gauge, TeleportSpecialAction


class BoardFactory(factory.Factory):
    board_description = TEST_CONFIG["board"]

    class Meta:
        model = Board


class DeckFactory(factory.Factory):
    cards = factory.LazyFunction(
        lambda: build_cards_list(TEST_CONFIG, factory.SubFactory(BoardFactory))
    )

    class Meta:
        model = Deck


class GaugeFactory(factory.Factory):
    class Meta:
        model = Gauge


class PlayerFactory(factory.Factory):
    name = factory.Sequence(lambda n: f"Player {n}")
    id_ = 1
    index = 0
    board = factory.SubFactory(BoardFactory)
    deck = factory.SubFactory(DeckFactory)
    gauge = factory.SubFactory(GaugeFactory, board=factory.SelfAttribute("..board"))
    trumps = ()
    hero = ""

    class Meta:
        model = Player


class TeleportSpecialActionFactory(factory.Factory):
    trump_args = {"name": "TeleportFromFactory", "color": Color.RED}

    class Meta:
        model = TeleportSpecialAction
