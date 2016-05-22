from aot.game import Player
from aot.cards.trumps import Trump
# fixtures, ignore the unsued import warnig
from aot.test import (
    board,
    deck,
    player,
)
from unittest.mock import MagicMock


def test_view_possible_squares(player):
    player.deck.view_possible_squares = MagicMock()
    card = player.deck.first_card_in_hand
    player.view_possible_squares(card)
    player.deck.view_possible_squares.assert_called_once_with(card, player.current_square)


def test_can_move(player):
    square = player.current_square
    card = player.deck.first_card_in_hand
    player.deck.view_possible_squares = MagicMock(return_value={square})
    assert player.can_move(card, square)
    player.deck.view_possible_squares.assert_called_with(card, square)

    player.deck.view_possible_squares = MagicMock(return_value=set())
    assert not player.can_move(card, square)
    player.deck.view_possible_squares.assert_called_with(card, square)


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
    player = Player(None, None, 1, board, deck)
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


def test_complete_turn(player):
    player.deck.revert_to_default = MagicMock()
    trump1 = MagicMock()
    trump1.duration = 0
    trump2 = MagicMock()
    trump2.duration = 2
    player._affecting_trumps = [trump1, trump2]
    player._number_moves_to_play = 0

    player.complete_turn()

    player.deck.revert_to_default.assert_called_once_with()
    trump1.consume.assert_called_once_with()
    trump2.consume.assert_called_once_with()
    assert len(player.affecting_trumps) == 1
    assert player.affecting_trumps[0] is trump2
    assert player._number_moves_to_play == player.MAX_NUMBER_MOVE_TO_PLAY


def test_play_card(player):
    player.deck.play = MagicMock()
    player.deck.init_turn = MagicMock()
    start_square = player.current_square
    card = player.deck.first_card_in_hand
    player.play_card(card, (3, 1), check_move=False)

    player.deck.play.assert_called_once_with(card)
    end_square = player.current_square
    assert not start_square.occupied
    assert end_square.occupied
    assert start_square.x != end_square.x and start_square.y != end_square.y
    assert 3 == end_square.x
    assert 1 == end_square.y

    player.play_card(card, (0, 0), check_move=False)

    assert player.deck.play.call_count == 2
    player.deck.play.assert_called_with(card)
    player.deck.init_turn.assert_called_once_with()


def test_reach_aim(player):
    player._aim = {player.current_square}
    player._last_square_previous_turn = player.current_square
    assert player.has_reached_aim


def test_play_wrong_card(player):
    player.deck.play = MagicMock()
    # None of these tests must throw.
    player.play_card(None, None)
    player.play_card(player.hand[0], None)
    player.play_card(None, (0, 0))


def test_pass(player):
    player.deck.init_turn = MagicMock()
    player.init_turn()
    assert player.can_play
    assert player._number_turn_passed_not_connected == 0
    player.pass_turn()

    player.deck.init_turn.assert_called_once_with()
    assert not player.can_play
    assert player._number_turn_passed_not_connected == 0


def test_pass_not_connected(player):
    player.is_connected = False
    player.deck.init_turn = MagicMock()
    player.init_turn()
    assert player.can_play
    assert player._number_turn_passed_not_connected == 0
    player.pass_turn()

    player.deck.init_turn.assert_called_once_with()
    assert player._number_turn_passed_not_connected == 1


def test_expect_reconnect(player):
    assert player.expect_reconnect
    player._number_turn_passed_not_connected = Player.MAX_NUMBER_TURN_EXPECTING_RECONNECT + 1
    assert not player.expect_reconnect


def test_reconnect(player):
    player._number_turn_passed_not_connected = 2
    player.is_connected = False
    assert player._number_turn_passed_not_connected == 2
    player.is_connected = True
    assert player._number_turn_passed_not_connected == 0


def test_discard(player):
    player.deck.play = MagicMock()
    player.deck.init_turn = MagicMock()

    player.init_turn()
    card = player.deck.first_card_in_hand
    player.discard(card)
    assert player.can_play
    player.deck.play.assert_called_once_with(card)

    player.discard(card)
    assert not player.can_play
    assert player.deck.play.call_count == 2
    player.deck.play.assert_called_with(card)
    player.deck.init_turn.assert_called_once_with()


def test_get_card(player):
    player.deck.get_card = MagicMock()
    card = player.deck.first_card_in_hand
    player.get_card(card.name, card.color)
    player.deck.get_card.assert_called_once_with(card.name, card.color)


def test_modify_number_moves(player):
    player.modify_number_moves(5)
    assert player._number_moves_to_play == player.MAX_NUMBER_MOVE_TO_PLAY + 5
    player.complete_turn()
    assert player._number_moves_to_play == player.MAX_NUMBER_MOVE_TO_PLAY

    player.modify_number_moves(-1)
    assert player._number_moves_to_play == player.MAX_NUMBER_MOVE_TO_PLAY - 1
    player.complete_turn()
    assert player._number_moves_to_play == player.MAX_NUMBER_MOVE_TO_PLAY


def test_get_trump(player):
    assert player.get_trump(None) is None
    assert player.get_trump('wrong_trump') is None
    assert isinstance(player.get_trump('Reinforcements'), Trump)


def test_trumps_property(player):
    assert len(player.trumps) == 4
    trump = player.trumps[0]
    assert 'name' in trump
    assert 'description' in trump
    assert 'cost' in trump
    assert 'duration' in trump
    assert 'must_target_player' in trump


def test_affecting_trumps(player):
    trump = player.get_trump('Reinforcements')
    trump.affect = MagicMock()
    trump.consume = MagicMock()
    player._affect_by(trump)
    player.init_turn()

    assert len(player.affecting_trumps) == 1
    assert player.affecting_trumps[0] is trump
    trump.affect.assert_called_once_with(player)


def test_play_trump(player):
    player.init_turn()
    trump = player.get_trump('Reinforcements')
    trump.affect = MagicMock()

    assert player.play_trump(trump, target=player)
    trump.affect.assert_called_once_with(player)
    assert not player.play_trump(trump, target=player)
    assert trump.affect.call_count == 1

    player.complete_turn()
    player.init_turn()
    assert player.play_trump(trump, target=player)
    assert trump.affect.call_count == 2
    trump.affect.assert_called_with(player)


def test_number_affecting_trumps(player):
    # Check that the number of played trumps is only increased if the targeted
    # player can be affected.
    trump = player.get_trump('Reinforcements')
    assert player._affect_by(trump)
    assert player._affect_by(trump)
    assert player._affect_by(trump)
    assert player._affect_by(trump)
    assert not player._affect_by(trump)
    player.init_turn()
    assert not player.play_trump(trump, target=player)
    assert player._number_trumps_played == 0
