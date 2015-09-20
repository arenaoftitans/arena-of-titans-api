import json
import toml

from aot.board import (
    Board,
    Color,
)
from aot.cards import (
    Card,
    Deck,
)
from aot.cards.trumps import trump_type_to_class
from aot.game import (
    Game,
    Player,
)


with open('config.toml', 'r') as config_file:
    config = toml.load(config_file)


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
            card = Card(
                board,
                number_movements=number_movements,
                color=color,
                complementary_colors=additional_colors,
                name=name,
                movements_types=movements_types)
            cards.append(card)
    return cards


def _get_additionnal_colors(color,
                            additional_movements_color,
                            complementary_colors):
    additional_colors = set()
    additional_colors.update([Color[col]
                              for col in additional_movements_color])
    additional_colors.update([Color[col]
                              for col in complementary_colors.get(color.value, [])])
    return additional_colors


def get_trumps_list(name='standard'):
    trumps_descriptions = get_trumps_descriptions(name=name)
    trumps = []
    for trump_description in trumps_descriptions:
        repeat_for_each_color = trump_description['repeat_for_each_color']
        del trump_description['repeat_for_each_color']
        trump_type = trump_description['parameters']['type']
        del trump_description['parameters']['type']
        trump_description.update(trump_description['parameters'])
        del trump_description['parameters']
        if repeat_for_each_color:
            name = trump_description['name']
            for color in Color:
                if color == Color.ALL:
                    continue
                trump_description['name'] = \
                    '{name} {color}'.format(name=name, color=color.value.title())
                trump_description['color'] = color
                trumps.append(trump_type_to_class[trump_type](**trump_description))
        else:
            trumps.append(trump_type_to_class[trump_type](**trump_description))

    return trumps


def get_trumps_descriptions(name='standard'):
    return get_game_description(name)['trumps']


def get_game(players_description, name='standard'):
    board = get_board(name=name)
    players = []
    for player in players_description:
        players.append(Player(player['name'], player['id'], player['index']))
    return Game(board, players)


def get_board(name='standard'):
    return Board(get_board_description(name=name))
