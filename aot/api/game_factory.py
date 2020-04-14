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

import logging
import random

import daiquiri

from aot.game.board import Board, Color
from aot.game.cards import Card, Deck
from aot.game.config import GAME_CONFIGS
from aot.game.game import Game
from aot.game.player import Player
from aot.game.trumps import (
    Gauge,
    SpecialActionsList,
    TrumpsList,
    create_action_from_description,
    power_type_to_class,
    trump_type_to_class,
)

from ..utils import remove_mappingproxies

logger = daiquiri.getLogger(__name__)


def create_game_for_players(players_description, name="standard"):
    config = GAME_CONFIGS[name]

    board = Board(config["board"])
    players = []
    for player in players_description:
        if player:
            deck = Deck(build_cards_list(config, board))
            gauge = Gauge(board)
            trumps = build_trumps_list(config)
            hero = player["hero"]
            power = _get_power(config, hero=hero)
            player = Player(
                player["name"],
                player["id"],
                player["index"],
                board,
                deck,
                gauge,
                available_trumps=trumps,
                hero=hero,
                is_ai=player.get("is_ai", False),
                power=power,
            )
        players.append(player)
    return Game(board, players)


def build_cards_list(config, board):
    colors = _get_colors(config)
    cards = []
    for card_description in config["movements_cards"]["cards"]:
        cards.extend(
            _get_cards_for_each_color(
                board, card_description, colors, config["movements_cards"]["number_cards_per_color"]
            ),
        )
    return cards


def _get_colors(config):
    colors = set()
    for color_name in config["colors"]:
        colors.add(Color[color_name])
    return colors


def _get_cards_for_each_color(board, card_description, colors, number_cards_per_color):
    cards = []
    movements_types = card_description["movements_type"]
    number_movements = card_description["number_of_movements"]
    name = card_description["name"]
    description = card_description["description"]
    cost = card_description["cost"]
    additional_movements_color = card_description.get("additional_movements_colors", [])
    complementary_colors = card_description.get("complementary_colors", {})

    for color in colors:
        additional_colors = _get_additional_colors(
            color, additional_movements_color, complementary_colors
        )
        for _ in range(number_cards_per_color):
            special_actions = _get_special_actions(
                card_description.get("special_actions", []), color
            )
            card = Card(
                board,
                number_movements=number_movements,
                color=color,
                complementary_colors=additional_colors,
                name=name,
                description=description,
                movements_types=movements_types,
                cost=cost,
                special_actions=special_actions,
            )
            cards.append(card)
    return cards


def _get_special_actions(description, color):
    actions = []
    for action_description in description:
        actions.append(create_action_from_description(action_description, color))

    return SpecialActionsList(actions)


def _get_additional_colors(color, additional_movements_color, complementary_colors):  # noqa: E503
    additional_colors = set()
    additional_colors.update([Color[col] for col in additional_movements_color])
    additional_colors.update([Color[col] for col in complementary_colors.get(color, [])])
    return additional_colors


def _get_trumps(description):
    trumps = []
    trump_cls = trump_type_to_class[description["type"]]
    if description.get("repeat_for_each_color", False):
        for color in Color:
            if color == Color.ALL:
                continue
            trumps.append(trump_cls(**description["args"], color=color))
    else:
        trumps.append(trump_cls(**description["args"], color=None))

    return trumps


def build_trumps_list(config):
    trumps_descriptions = config["trumps"]
    trumps = []
    weights = []
    for trump_description in trumps_descriptions:
        generated_trumps = _get_trumps(trump_description)
        trumps.extend(generated_trumps)
        weights.extend([trump_description["weight"]] * len(generated_trumps))

    # Return 4 trumps at random among all the possible ones
    randomized_trumps = _get_random_trump_list(config, trumps, weights)
    return TrumpsList(randomized_trumps)


def _get_random_trump_list(config, trumps, weights):
    number_trumps_per_player = config["number_trumps_per_player"]

    for _ in range(10):
        trumps_list = random.choices(trumps, weights=weights, k=number_trumps_per_player)
        if not any(trumps_list.count(x) > 1 for x in trumps_list):
            return trumps_list

    logging.debug("Failed to find a stable random.choices, reverting to shuffle.")

    random.shuffle(trumps)
    return trumps[:number_trumps_per_player]


def _get_power(config, hero=None):
    power_description = config["powers"].get(hero.lower(), None)
    if power_description is not None:
        power_cls = power_type_to_class[power_description["type"]]
        # We must create copies here, because mappingproxy objects cannot be pickled.
        power_args = remove_mappingproxies(power_description["args"])
        return power_cls(**power_args)
