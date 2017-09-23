################################################################################
# Copyright (C) 2015-2016 by Arena of Titans Contributors.
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

import copy
import json
import random

from .board import (
    Board,
    Color,
)
from .cards import (
    Card,
    Deck,
)
from .cards.trumps import (
    Gauge,
    SimpleTrump,
    TrumpList,
)
from .game import (
    Game,
    Player,
)


def get_game_description(name='standard'):
    with open('aot/resources/games/{}.json'.format(name)) as games:
        return json.load(games)


def get_board_description(name='standard'):
    return get_game_description(name)['board']


def get_number_players(name='standard'):
    return get_game_description(name)['number_players']


def get_deck(board, name='standard'):
    return Deck(get_cards_list(board, name=name))


def get_cards_list(board, name='standard'):
    cards_description = get_movements_cards_description(name)
    colors = _get_colors(name)
    cards = []
    number_cards_per_color = _get_number_cards_per_color(name)
    for card_description in cards_description['cards']:
        cards.extend(
            _get_cards(
                board, card_description, colors, number_cards_per_color))
    return cards


def get_movements_cards_description(name='standard'):
    return get_game_description(name)['movements_cards']


def _get_colors(name='standard'):
    colors = set()
    for color_name in get_game_description(name)['colors']:
        colors.add(Color[color_name])
    return colors


def _get_number_cards_per_color(name='standard'):
    return get_movements_cards_description(name)['number_cards_per_color']


def _get_cards(board, card_description, colors, number_cards_per_color):
    cards = []
    movements_types = card_description['movements_type']
    number_movements = card_description['number_of_movements']
    name = card_description['name']
    description = card_description['description']
    cost = card_description['cost']
    additional_movements_color = card_description\
        .get('additional_movements_colors', [])
    complementary_colors = card_description\
        .get('complementary_colors', {})

    for color in colors:
        additional_colors = _get_additionnal_colors(
            color,
            additional_movements_color,
            complementary_colors)
        for _ in range(number_cards_per_color):
            special_actions = _get_special_actions(card_description.get('special_actions', []))
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


def _get_special_actions(description):
    actions = TrumpList()
    for action_description in description:
        actions.extend(_get_trumps(action_description))

    return actions


def _get_additionnal_colors(color,
                            additional_movements_color,
                            complementary_colors):
    additional_colors = set()
    additional_colors.update([Color[col]
                              for col in additional_movements_color])
    additional_colors.update([Color[col]
                              for col in complementary_colors.get(color, [])])
    return additional_colors


def get_trumps_list(name='standard'):
    trumps_descriptions = get_trumps_descriptions(name=name)
    trumps = TrumpList()
    for raw_trump_description in trumps_descriptions:
        trumps.extend(_get_trumps(raw_trump_description))

    # Return 4 trumps at random among all the possible ones
    random.shuffle(trumps)
    return trumps[:get_number_trumps_per_player()]


def _get_trumps(description):
    trumps = []
    trump_description = copy.deepcopy(description)
    repeat_for_each_color = trump_description['repeat_for_each_color']
    del trump_description['repeat_for_each_color']
    trump_type = trump_description['parameters']['type']
    del trump_description['parameters']['type']
    trump_description.update(trump_description['parameters'])
    del trump_description['parameters']
    if repeat_for_each_color:
        for color in Color:
            color_trump_description = copy.deepcopy(trump_description)
            if color == Color.ALL:
                continue
            trump_name = color_trump_description['name']
            trump_name = '{name} {color}'.format(name=trump_name, color=color.title())
            color_trump_description['name'] = trump_name
            color_trump_description['color'] = color
            color_trump_description = copy.deepcopy(color_trump_description)
            trumps.append(
                SimpleTrump(type=trump_type, name=trump_name, args=color_trump_description))
    else:
        trump_name = trump_description['name']
        trumps.append(SimpleTrump(type=trump_type, name=trump_name, args=trump_description))

    return trumps


def get_trumps_descriptions(name='standard'):
    return get_game_description(name)['trumps']


def get_number_trumps_per_player(name='standard'):
    return get_game_description(name)['number_trumps_per_player']


def get_game(players_description, name='standard'):
    board = get_board(name=name)
    players = []
    for player in players_description:
        if player:
            deck = get_deck(board)
            gauge = get_gauge(board)
            trumps = get_trumps_list(name=name)
            hero = player['hero']
            power = get_power(name=name, trumps=trumps, hero=hero)
            player = Player(
                player['name'],
                player['id'],
                player['index'],
                board,
                deck,
                gauge,
                trumps=trumps,
                hero=player.get('hero', ''),
                is_ai=player.get('is_ai', False),
                power=power,
            )
        players.append(player)
    return Game(board, players)


def get_power(name='standard', trumps=None, hero=None):
    if trumps is None:  # pragma: no cover
        trumps = []

    power_description = get_power_description(name).get(hero.lower(), None)
    if power_description is not None:
        power_description = copy.deepcopy(power_description)
        power_type = power_description['parameters']['type']
        del power_description['parameters']['type']
        power_description.update(power_description['parameters'])
        del power_description['parameters']
        power_name = power_description['name']
        return SimpleTrump(type=power_type, name=power_name, args=power_description)


def get_power_description(name='standard'):
    return get_game_description(name)['powers']


def get_board(name='standard'):
    return Board(get_board_description(name=name))


def get_gauge(board):
    return Gauge(board)
