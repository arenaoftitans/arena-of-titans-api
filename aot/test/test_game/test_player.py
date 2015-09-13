from aot.game import Player
from aot.cards.trumps import Trump
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

    player.move(None)
    assert square is player.current_square


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


def test_play_card(player):
    start_square = player.current_square
    card = player.hand[0]
    player.play_card(card, (0, 0), check_move=False)
    end_square = player.current_square

    assert not start_square.occupied
    assert end_square.occupied
    assert start_square != end_square
    assert 0 == start_square.x
    assert 0 == end_square.y
    assert card not in player.deck.hand


def test_play_wrong_card(player):
    # None of these tests must throw.
    player.play_card(None, None)
    player.play_card(player.hand[0], None)
    player.play_card(None, (0, 0))


def test_pass(player):
    player.init_turn()
    assert player.can_play
    player.pass_turn()
    assert not player.can_play


def test_discard(player):
    player.init_turn()
    card = player.hand[0]
    player.discard(card)
    assert player.can_play
    assert card not in player.deck.hand

    card = player.hand[0]
    player.discard(card)
    assert not player.can_play
    assert card not in player.deck.hand


def test_get_card(player):
    assert player.get_card(None, None) is None
    card = player.hand[0]
    assert player.get_card(None, card.color) is None
    assert player.get_card(card.name, None) is None
    assert player.get_card(card.name, card.color) is card


def test_get_trump(player):
    assert player.get_trump(None) is None
    assert player.get_trump('wrong_trump') is None
    assert isinstance(player.get_trump('Reinforcements'), Trump)


def test_trumps_property(player):
    assert len(player.trumps) == 5
    trump = player.trumps[0]
    assert 'name' in trump
    assert 'description' in trump
    assert 'cost' in trump
    assert 'duration' in trump
    assert 'must_target_player' in trump


def test_affecting_trumps(player):
    trump = player.get_trump('Reinforcements')
    player.affect_by(trump)
    player.init_turn()
    assert len(player.affecting_trumps) == 1
    assert player.affecting_trumps[0] is trump

    player.complete_turn()
    assert len(player.affecting_trumps) == 0
