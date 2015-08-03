from aot.game import Player
# fixtures, ignore the unsued import warnig
from aot.test import board
from aot.test import deck
from aot.test import player


def test_move(player, board):
    start_square = player.current_square
    assert start_square.occupied
    assert 0 == start_square.x
    assert 8 == start_square.y

    square = board[8, 0]
    player.move(square)
    square = player.current_square
    assert not start_square.occupied
    assert square.occupied
    assert square != start_square
    assert 8 == square.x
    assert 0 == square.y


def test_wins(player):
    player.wins(rank=1)

    assert player.has_won
    assert 1 == player.rank


def test_init_game_player_0(player, board):
    start_square = player.current_square
    assert start_square.occupied
    assert 0 == start_square.x
    assert 8 == start_square.y

    # Check the deck
    deck = player.deck
    assert deck is not None
    assert 5 == deck.number_cards_in_hand

    # Check that the player has not won
    assert not player.has_won
    assert not player.has_reached_aim
    assert -1 == player.rank

    # Check the aim
    expected_aim = set([board[16, 8], board[17, 8], board[18, 8], board[19, 8]])
    assert expected_aim == player.aim


def test_init_game_player_1(board, deck):
    player = Player(None, None, 1)
    player.set(board, deck)
    start_square = player.current_square
    assert start_square.occupied
    assert 4 == start_square.x
    assert 8 == start_square.y

    # Check the deck
    deck = player.deck
    assert deck is not None
    assert 5 == deck.number_cards_in_hand

    # Check that the player has not won
    assert not player.has_won
    assert not player.has_reached_aim
    assert -1 == player.rank

    # Check the aim
    expected_aim = set([board[20, 8], board[21, 8], board[22, 8], board[23, 8]])
    assert expected_aim == player.aim


def test_init_turn(player):
    player.can_play = False
    player.init_turn()
    assert player.can_play
    assert player.current_square == player.last_square_previous_turn

def test_reach_aim(player):
    player.play_card(None, (16, 8), check_move=False)
    player.init_turn()
    player.pass_turn()
    assert player.has_reached_aim


def test_play(player):
    start_square = player.current_square
    card = player.deck.first_card_in_hand
    player.play_card(card, (0, 0), check_move=False)
    end_square = player.current_square

    assert not start_square.occupied
    assert end_square.occupied
    assert start_square != end_square
    assert 0 == start_square.x
    assert 0 == end_square.y
    assert not player.deck.card_in_hand(card)


def test_pass(player):
    player.init_turn()
    assert player.can_play
    player.pass_turn()
    assert not player.can_play


def test_discard(player):
    player.init_turn()
    card = player.deck.first_card_in_hand
    player.discard(card)
    assert player.can_play
    assert not player.deck.card_in_hand(card)

    card = player.deck.first_card_in_hand
    player.discard(card)
    assert not player.can_play
    assert not player.deck.card_in_hand(card)
