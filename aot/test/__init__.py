import pytest

from aot import get_board_description
from aot import get_cards_list
from aot.board import Board
from aot.cards import Deck
from aot.game import Player


@pytest.fixture
def board():
    board_description = get_board_description()
    return Board(board_description)


@pytest.fixture
def deck(board):
    cards = get_cards_list(board)
    return Deck(cards)


@pytest.fixture
def player(board, deck):
    player = Player(None, None, 0)
    player.set(board, deck)
    return player
