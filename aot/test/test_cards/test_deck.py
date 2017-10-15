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

from unittest.mock import MagicMock

from .. import (  # noqa: F401
    board,
    deck,
)
from ...cards import (
    Card,
    SimpleCard,
)


NUMBER_COLORS = 4
NUMBER_CARD_TYPES = 7
NUMBER_CARDS_HAND = 5
NUMBER_TOTAL_CARDS = NUMBER_CARD_TYPES * NUMBER_COLORS


def test_get_card(deck):  # noqa: F811
    card = deck.first_card_in_hand
    assert card is deck.get_card(card.name, card.color)
    assert deck.get_card('Azerty', 'Black') is None
    assert deck.get_card(None, 'Black') is None
    assert deck.get_card('King', 'king') is None
    assert deck.get_card('King', None) is None
    assert deck.get_card(None, None) is None


def test_init_deck(deck):  # noqa: F811
    assert NUMBER_TOTAL_CARDS == deck.number_cards_in_hand + \
        deck.number_cards_in_stock + \
        deck.number_cards_in_graveyard
    assert deck.number_cards_in_graveyard == 0
    assert NUMBER_CARDS_HAND == deck.number_cards_in_hand
    assert NUMBER_TOTAL_CARDS - NUMBER_CARDS_HAND == deck.number_cards_in_stock


def test_play_existing_card(deck):  # noqa: F811
    nb_remaining_cards_before_play = deck.number_cards_in_stock
    played_card = deck.first_card_in_hand
    played_card.revert_to_default = MagicMock()

    deck.play(played_card)
    nb_remaining_cards_after_play = deck.number_cards_in_stock
    assert nb_remaining_cards_before_play == nb_remaining_cards_after_play
    assert NUMBER_CARDS_HAND - 1 == deck.number_cards_in_hand
    played_card.revert_to_default.assert_called_once_with()

    deck.init_turn()
    assert nb_remaining_cards_before_play - 1 == deck.number_cards_in_stock
    assert NUMBER_CARDS_HAND == deck.number_cards_in_hand
    assert 1 == deck.number_cards_in_graveyard
    assert played_card not in deck.hand
    assert played_card not in deck.stock
    assert played_card in deck.graveyard


def test_play_card_from_name_color(deck):  # noqa: F811
    nb_remaining_cards_before_play = deck.number_cards_in_stock
    played_card = deck.first_card_in_hand
    played_card.revert_to_default = MagicMock()
    simple_card = SimpleCard(name=played_card.name, color=played_card.color)

    deck.play(simple_card)
    nb_remaining_cards_after_play = deck.number_cards_in_stock
    assert nb_remaining_cards_before_play == nb_remaining_cards_after_play
    assert NUMBER_CARDS_HAND - 1 == deck.number_cards_in_hand
    played_card.revert_to_default.assert_called_once_with()


def test_play_no_card(deck):  # noqa: F811
    nb_remaining_cards_before_play = deck.number_cards_in_stock
    deck.play(None)

    assert nb_remaining_cards_before_play == deck.number_cards_in_stock
    assert NUMBER_CARDS_HAND == deck.number_cards_in_hand
    assert 0 == deck.number_cards_in_graveyard


def test_play_unexisting_card(board, deck):  # noqa: F811
    nb_remaining_cards_before_play = deck.number_cards_in_stock
    card = Card(board)
    deck.play(card)

    assert nb_remaining_cards_before_play == deck.number_cards_in_stock
    assert NUMBER_CARDS_HAND == deck.number_cards_in_hand
    assert 0 == deck.number_cards_in_graveyard


def test_play_more_cards_than_total_in_deck(deck):  # noqa: F811
    # Empty stock
    for _ in range(NUMBER_TOTAL_CARDS - NUMBER_CARDS_HAND):
        card = deck.first_card_in_hand
        deck.play(card)
        deck.init_turn()

    assert 0 == deck.number_cards_in_stock
    assert NUMBER_CARDS_HAND == deck.number_cards_in_hand

    # Play another card
    card = deck.first_card_in_hand
    deck.play(card)
    deck.init_turn()

    assert NUMBER_TOTAL_CARDS - NUMBER_CARDS_HAND == deck.number_cards_in_stock
    assert NUMBER_CARDS_HAND == deck.number_cards_in_hand
    # 4 cards have not been played yet.
    assert NUMBER_TOTAL_CARDS - 4 == deck.number_cards_in_graveyard


def test_view_possible_square(deck):  # noqa: F811
    assert isinstance(deck.view_possible_squares(None, None), set)
    assert isinstance(deck.view_possible_squares(deck.first_card_in_hand, None), set)
    card = deck.first_card_in_hand
    card = SimpleCard(name=card.name, color=card.color)
    assert isinstance(deck.view_possible_squares(card, None), set)


def test_remove_color_from_possible_colors(deck):  # noqa: F811
    for card in deck.hand:
        card.remove_color_from_possible_colors = MagicMock()

    color = card.color
    deck.remove_color_from_possible_colors(color)
    for card in deck.hand:
        card.remove_color_from_possible_colors.assert_called_once_with(color)


def test_revert_to_default(deck):  # noqa: F811
    for card in deck.hand:
        card.revert_to_default = MagicMock()

    deck.revert_to_default()
    for card in deck.hand:
        card.revert_to_default.assert_called_once_with()


def test_modify_colors(deck):  # noqa: F811
    for card in deck.hand:
        card.modify_colors = MagicMock()

    deck.modify_colors({'BLACK'})

    for card in deck.hand:
        card.modify_colors.assert_called_once_with({'BLACK'})


def test_modify_colors_with_filter(deck):  # noqa: F811
    for card in deck.hand:
        card.modify_colors = MagicMock()
    deck.first_card_in_hand._name = 'Card to keep'
    card_filter = lambda card: card.name == 'Card to keep'  # noqa: E731

    deck.modify_colors(5, card_filter=card_filter)

    for card in deck.hand[1:]:
        assert not card.modify_colors.called
    deck.first_card_in_hand.modify_colors.assert_called_once_with(5)


def test_modify_number_moves(deck):  # noqa: F811
    for card in deck.hand:
        card.modify_number_moves = MagicMock()

    deck.modify_number_moves(5)

    for card in deck.hand:
        card.modify_number_moves.assert_called_once_with(5)


def test_modify_number_moves_with_filter(deck):  # noqa: F811
    for card in deck.hand:
        card.modify_number_moves = MagicMock()
    deck.first_card_in_hand._name = 'Card to keep'
    card_filter = lambda card: card.name == 'Card to keep'  # noqa: E731

    deck.modify_number_moves(5, card_filter=card_filter)

    for card in deck.hand[1:]:
        assert not card.modify_number_moves.called
    deck.first_card_in_hand.modify_number_moves.assert_called_once_with(5)
