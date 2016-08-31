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

from aot.board import (
    Board,
    Color,
)
from aot.cards import (
    Card,
    Deck,
)
from aot.cards.trumps import (
    SimpleTrump,
    TrumpList
)
from aot.game import (
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
            card = Card(
                board,
                number_movements=number_movements,
                color=color,
                complementary_colors=additional_colors,
                name=name,
                description=description,
                movements_types=movements_types,
                cost=cost
            )
            cards.append(card)
    return cards


def _get_additionnal_colors(color,
                            additional_movements_color,
                            complementary_colors):
    additional_colors = set()
    additional_colors.update([Color[col]
                              for col in additional_movements_color])
    additional_colors.update([Color[col]
                              for col in complementary_colors.get(color, [])])
    return additional_colors


def get_trumps_list(board_name='standard', test=False):
    trumps_descriptions = get_trumps_descriptions(name=board_name)
    trumps = TrumpList()
    for raw_trump_description in trumps_descriptions:
        trump_description = copy.deepcopy(raw_trump_description)
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

    # Return 4 trumps at random among all the possible ones
    if not test:
        random.shuffle(trumps)
    return trumps[1:]


def get_trumps_descriptions(name='standard'):
    return get_game_description(name)['trumps']


def get_game(players_description, name='standard', test=False):
    board = get_board(name=name)
    players = []
    for player in players_description:
        if player:
            deck = get_deck(board)
            player = Player(
                player['name'],
                player['id'],
                player['index'],
                board,
                deck,
                trumps=get_trumps_list(board_name=name, test=test),
                hero=player.get('hero', ''),
                is_ai=player.get('is_ai', False))
        players.append(player)
    return Game(board, players)


def get_board(name='standard'):
    return Board(get_board_description(name=name))
