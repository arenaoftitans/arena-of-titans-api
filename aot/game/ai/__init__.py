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

from collections import namedtuple

from aot.game.ai.pathfinding import a_star


IACardResult = namedtuple('IAResult', 'card square')


def distance_covered(start_square, proposed_destination_square, goal_square, board):
    distance_from_start = len(a_star(start_square, goal_square, board))
    distance_from_destination = len(a_star(proposed_destination_square, goal_square, board))
    return distance_from_start - distance_from_destination


def find_move_to_play(hand, current_square, goal_squares, board):
    best_distance = 0
    best_card = None
    best_square = None
    for goal_square in goal_squares:
        for card in hand:
            for square in card.move(current_square):
                if square in goal_squares:
                    # We can't find a better move. Stopping here.
                    return IACardResult(card=card, square=square)

                distance = distance_covered(current_square, square, goal_square, board)
                if distance > best_distance or \
                        should_make_null_move(distance, best_distance, card, best_card) or \
                        is_card_cheaper(distance, best_distance, card, best_card):
                    best_card = card
                    best_square = square
                    best_distance = distance

    return IACardResult(card=best_card, square=best_square)


def should_make_null_move(distance, best_distance, card, best_card):
    return best_distance == 0 and \
        distance == 0 and \
        (best_card is None or is_card_cheaper(distance, best_distance, card, best_card))


def is_card_cheaper(distance, best_distance, card, best_card):
    return distance >= 0 and distance == best_distance and card.cost < best_card.cost


def find_cheapest_card(hand):
    cheapest_card = hand[0]
    for card in hand[1:]:
        if card.cost < cheapest_card.cost:
            cheapest_card = card

    return cheapest_card
