import pytest

from aot import get_cards_list
from aot.cards import Card
from aot.cards import Deck
# board is a fixture, ignore the unsued import warnig
from aot.test import board


NUMBER_COLORS = 4
NUMBER_CARD_TYPES = 7
NUMBER_CARDS_HAND = 5
NUMBER_TOTAL_CARDS = NUMBER_CARD_TYPES * NUMBER_COLORS


@pytest.fixture
def deck(board):
    cards = get_cards_list(board)
    return Deck(cards)


def test_get_card(deck):
    card = deck.first_card_in_hand
    assert card == deck.get_card(card.name, card.color)
    assert deck.get_card('Azerty', 'Black') is None
    assert deck.get_card(None, 'Black') is None
    assert deck.get_card('King', 'king') is None
    assert deck.get_card('King', None) is None


def test_init_deck(deck):
    assert NUMBER_TOTAL_CARDS == deck.number_cards_in_hand + \
        deck.number_cards_in_stock +\
        deck.number_cards_in_graveyard
    assert deck.number_cards_in_graveyard == 0
    assert NUMBER_CARDS_HAND == deck.number_cards_in_hand
    assert NUMBER_TOTAL_CARDS - NUMBER_CARDS_HAND == deck.number_cards_in_stock


def test_play_existing_card(deck):
    nb_remaining_cards_before_play = deck.number_cards_in_stock
    played_card = deck.first_card_in_hand

    deck.play(played_card)
    nb_remaining_cards_after_play = deck.number_cards_in_stock
    assert nb_remaining_cards_before_play == nb_remaining_cards_after_play
    assert NUMBER_CARDS_HAND - 1 == deck.number_cards_in_hand

    deck.init_turn()
    assert nb_remaining_cards_before_play -1 == deck.number_cards_in_stock
    assert NUMBER_CARDS_HAND == deck.number_cards_in_hand
    assert 1 == deck.number_cards_in_graveyard
    assert not deck.card_in_hand(played_card)
    assert not deck.card_in_stock(played_card)
    assert deck.card_in_graveyard(played_card)


def test_play_no_card(deck):
    nb_remaining_cards_before_play = deck.number_cards_in_stock
    deck.play(None)

    assert nb_remaining_cards_before_play == deck.number_cards_in_stock
    assert NUMBER_CARDS_HAND == deck.number_cards_in_hand
    assert 0 == deck.number_cards_in_graveyard


def test_play_unexisting_card(board, deck):
    nb_remaining_cards_before_play = deck.number_cards_in_stock
    card = Card(board)
    deck.play(card)

    assert nb_remaining_cards_before_play == deck.number_cards_in_stock
    assert NUMBER_CARDS_HAND == deck.number_cards_in_hand
    assert 0 == deck.number_cards_in_graveyard


def test_play_more_cards_than_total_in_deck(deck):
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
