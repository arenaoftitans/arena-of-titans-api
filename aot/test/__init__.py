import pytest

from aot import (
    get_board,
    get_game,
    get_cards_list,
    get_number_players,
    get_trumps_list,
)
from aot.board import Board
from aot.cards import Deck
from aot.game import Player


@pytest.fixture
def board():
    return get_board()


@pytest.fixture
def deck(board):
    cards = get_cards_list(board)
    return Deck(cards)


@pytest.fixture
def player(board, deck):
    player = Player(None, None, 0, board, deck, trumps=get_trumps_list(test=True))
    return player


@pytest.fixture
def game():
    players_description = [{
        'name': 'Player {}'.format(i),
        'index': i,
        'id': i
    } for i in range(get_number_players())]
    return get_game(players_description)
