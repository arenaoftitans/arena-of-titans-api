import logging
import random

from aot.game.board import Board, Color
from aot.game.cards import Card, Deck
from aot.game.config import GAME_CONFIGS
from aot.game.game import Game
from aot.game.player import Player
from aot.game.trumps import Gauge, SimpleTrump, TrumpList

logger = logging.getLogger(__name__)


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
                trumps=trumps,
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
            special_actions = _get_special_actions(card_description.get("special_actions", []))
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


def _get_additional_colors(color, additional_movements_color, complementary_colors):  # noqa: E503
    additional_colors = set()
    additional_colors.update([Color[col] for col in additional_movements_color])
    additional_colors.update([Color[col] for col in complementary_colors.get(color, [])])
    return additional_colors


def _get_trumps(description):
    trumps = []
    trump_description = description.copy()
    trump_description["parameters"] = trump_description["parameters"].copy()
    repeat_for_each_color = trump_description["repeat_for_each_color"]
    del trump_description["repeat_for_each_color"]
    trump_type = trump_description["parameters"]["type"]
    del trump_description["parameters"]["type"]
    trump_description.update(trump_description["parameters"])
    del trump_description["parameters"]
    if repeat_for_each_color:
        for color in Color:
            color_trump_description = trump_description.copy()
            if color == Color.ALL:
                continue
            trump_name = color_trump_description["name"]
            color_trump_description["name"] = trump_name
            color_trump_description["color"] = color
            color_trump_description = color_trump_description.copy()
            trumps.append(
                SimpleTrump(
                    type=trump_type, name=trump_name, color=color, args=color_trump_description,
                )
            )
    else:
        trump_name = trump_description["name"]
        trump_description["color"] = None
        trumps.append(
            SimpleTrump(type=trump_type, name=trump_name, color=None, args=trump_description,)
        )

    return trumps


def build_trumps_list(config):
    trumps_descriptions = config["trumps"]
    trumps = []
    weights = []
    for raw_trump_description in trumps_descriptions:
        raw_trump_description = raw_trump_description.copy()
        weight = raw_trump_description["weight"]
        del raw_trump_description["weight"]
        generated_trumps = _get_trumps(raw_trump_description)
        trumps.extend(generated_trumps)
        weights.extend([weight] * len(generated_trumps))

    # Return 4 trumps at random among all the possible ones
    randomized_trumps = _get_random_trump_list(config, trumps, weights)
    return TrumpList(randomized_trumps)


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
        power_description = power_description.copy()
        power_description["parameters"] = power_description["parameters"].copy()
        power_type = power_description["parameters"]["type"]
        del power_description["parameters"]["type"]
        power_description.update(power_description["parameters"])
        del power_description["parameters"]
        power_name = power_description["name"]
        return SimpleTrump(type=power_type, name=power_name, args=power_description)
