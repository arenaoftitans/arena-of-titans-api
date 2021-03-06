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

import copy
import random

from .card import Card
from .exceptions import CardNotFoundError


class Deck:
    CARDS_IN_HAND = 5

    _cards = []
    _graveyard = []
    _hand = []
    _stock = []

    def __init__(self, cards):
        self._cards = cards
        self._graveyard = []
        self._hand = []

        self._init_stock()
        self.init_turn()

    def _init_stock(self):
        self._stock = random.sample(self._cards, len(self._cards))

    def init_turn(self):
        while len(self._hand) < self.CARDS_IN_HAND:
            self._hand.append(self._draw_next_card())

    def _draw_next_card(self):
        if self.number_cards_in_stock == 0:
            self._init_stock()
            for card in self._hand:
                self._stock.remove(card)

        drawn_card = self._stock[0]
        self._stock.remove(drawn_card)
        return drawn_card

    def modify_colors(self, colors, filter_=None):
        for card in filter(filter_, self._hand):
            card.modify_colors(colors)

    def modify_number_moves(self, delta, filter_=None):
        for card in filter(filter_, self._hand):
            card.modify_number_moves(delta)

    def set_special_actions_to_card(self, card_name, special_action_descriptions):
        for card in filter(lambda x: x.name == card_name, self._hand):
            actions_copy = copy.deepcopy(special_action_descriptions)
            card.set_special_actions(actions_copy)

    def view_possible_squares(self, card, position):
        if card is not None and not isinstance(card, Card):
            game_card = self.get_card(card.name, card.color)
        else:
            game_card = card

        if game_card is not None and position is not None:
            return game_card.move(position)
        else:
            return set()

    def play(self, card):
        if card is not None and not isinstance(card, Card):
            card = self.get_card(card.name, card.color)

        if card is not None and card in self._hand:
            card.revert_to_default()
            self._hand.remove(card)
            self._graveyard.append(card)

    def remove_color_from_possible_colors(self, color):
        for card in self._hand:
            card.remove_color_from_possible_colors(color)

    def revert_to_default(self):
        for card in self._hand:
            card.revert_to_default()

    @property
    def first_card_in_hand(self):
        return self._hand[0]

    def get_card(self, card_name, card_color):
        matching_cards = [
            card for card in self._hand if card.name == card_name and card.color == card_color
        ]

        if len(matching_cards) != 1:
            raise CardNotFoundError

        return matching_cards[0]

    @property
    def graveyard(self):
        return self._graveyard

    @property
    def hand(self):
        return self._hand

    @property
    def number_cards_in_stock(self):
        return len(self._stock)

    @property
    def number_cards_in_graveyard(self):
        return len(self._graveyard)

    @property
    def number_cards_in_hand(self):
        return len(self._hand)

    @property
    def stock(self):
        return self._stock

    def __iter__(self):
        return iter(self._hand + self._stock)
