import json

from aot.board import Color
from aot.cards import Card
from aot.cards import Deck


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
        colors.add(Color[color_name.upper()])
    return colors


def _get_number_cards_per_color(name='standard'):
    return get_movements_cards_description(name)['number_cards_per_color']


def _get_cards(board, card_description, colors, number_cards_per_color):
    cards = []
    movements_types = card_description['movements_type']
    number_movements = card_description['number_of_movements']
    name = card_description['name']
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
            cards.append(Card(
                board,
                number_movements=number_movements,
                color=color,
                complementary_colors=additional_colors,
                name=name,
                movements_types=movements_types))
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
