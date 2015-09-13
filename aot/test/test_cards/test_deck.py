from aot.cards import Card
# fixtures, ignore the unsued import warnig
from aot.test import (
    board,
    deck
)


NUMBER_COLORS = 4
NUMBER_CARD_TYPES = 7
NUMBER_CARDS_HAND = 5
NUMBER_TOTAL_CARDS = NUMBER_CARD_TYPES * NUMBER_COLORS


def test_get_card(deck):
    card = deck.first_card_in_hand
    assert card == deck.get_card(card.name, card.color)
    assert deck.get_card('Azerty', 'Black') is None
    assert deck.get_card(None, 'Black') is None
    assert deck.get_card('King', 'king') is None
    assert deck.get_card('King', None) is None


def test_init_deck(deck):
    assert NUMBER_TOTAL_CARDS == deck.number_cards_in_hand + \
        deck.number_cards_in_stock + \
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
    assert played_card not in deck.hand
    assert played_card not in deck.stock
    assert played_card in deck.graveyard


def test_play_card_from_name_color(deck):
    nb_remaining_cards_before_play = deck.number_cards_in_stock
    played_card = deck.first_card_in_hand

    deck.play((played_card.name, played_card.color))
    nb_remaining_cards_after_play = deck.number_cards_in_stock
    assert nb_remaining_cards_before_play == nb_remaining_cards_after_play
    assert NUMBER_CARDS_HAND - 1 == deck.number_cards_in_hand


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


def test_view_possible_square(deck):
    assert isinstance(deck.view_possible_squares(None, None), set)
    assert isinstance(deck.view_possible_squares(deck.first_card_in_hand, None), set)
