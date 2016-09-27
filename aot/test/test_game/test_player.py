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

import pytest

from aot.game import Player
from aot.cards.trumps import (
    SimpleTrump,
    Trump,
    TrumpList,
)
# fixtures, ignore the unsued import warnig
from aot.test import (
    board,
    deck,
    player,
)
from unittest.mock import (
    MagicMock,
    patch,
)


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


def test_complet_turn_collect_all_consumed_trumps(player):
    trump1 = MagicMock()
    trump1.duration = 0
    trump2 = MagicMock()
    trump2.duration = 0
    player._affecting_trumps = [trump1, trump2]
    player._number_moves_to_play = 0

    player.complete_turn()

    assert len(player.affecting_trumps) == 0


def test_play_card(player):
    player.deck.play = MagicMock()
    player.deck.init_turn = MagicMock()
    start_square = player.current_square
    card = player.deck.first_card_in_hand

    assert not player.play_card(card, (3, 1), check_move=False)

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


def test_play_card_with_special_actions(player):
    player.deck.play = MagicMock()
    player.deck.init_turn = MagicMock()
    start_square = player.current_square
    card = player.deck.first_card_in_hand
    card._special_actions = TrumpList()
    card._special_actions.append(SimpleTrump(name='action', type=None, args=None))

    assert player.play_card(card, (3, 1), check_move=False)

    player.deck.play.assert_called_once_with(card)
    end_square = player.current_square
    assert not start_square.occupied
    assert end_square.occupied
    assert start_square.x != end_square.x and start_square.y != end_square.y
    assert 3 == end_square.x
    assert 1 == end_square.y
    assert player._special_actions_names == ['action']
    assert player._special_actions is card._special_actions


def test_has_special_actions(player):
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type=None, args=None))
    player.special_actions = actions

    assert player.has_special_actions
    assert player.name_next_special_action == 'action'
    assert player.has_special_actions

    player._special_actions_names.remove('action')
    assert not player.has_special_actions


def test_play_special_action(player):
    action = MagicMock()
    action.name = 'Action'
    target = MagicMock()
    player._special_actions_names = {'action'}
    kwargs = {'square': 'square-0-0'}

    player.play_special_action(action, target=target, action_args=kwargs)

    action.affect.assert_called_once_with(target, **kwargs)
    assert not player.has_special_actions


def test_play_special_action_no_args(player):
    action = MagicMock()
    action.name = 'action'
    target = MagicMock()
    player._special_actions_names = {'action'}

    player.play_special_action(action, target=target)

    action.affect.assert_called_once_with(target)
    assert not player.has_special_actions


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
    assert player._number_turns_passed_not_connected == 0
    player.pass_turn()

    player.deck.init_turn.assert_called_once_with()
    assert not player.can_play
    assert player._number_turns_passed_not_connected == 0


def test_pass_not_connected(player):
    player.is_connected = False
    player.deck.init_turn = MagicMock()
    player.init_turn()
    assert player.can_play
    assert player._number_turns_passed_not_connected == 0
    player.pass_turn()

    player.deck.init_turn.assert_called_once_with()
    assert player._number_turns_passed_not_connected == 1


def test_expect_reconnect(player):
    assert player.expect_reconnect
    player._number_turns_passed_not_connected = Player.MAX_NUMBER_TURN_EXPECTING_RECONNECT + 1
    assert not player.expect_reconnect


def test_reconnect(player):
    player._number_turns_passed_not_connected = 2
    player.is_connected = False
    assert player._number_turns_passed_not_connected == 2
    player.is_connected = True
    assert player._number_turns_passed_not_connected == 0


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
    with pytest.raises(IndexError):
        assert player.get_trump(None)
    with pytest.raises(IndexError):
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


def test_still_in_game_ai(player):
    player._is_ai = True
    player.is_connected = False
    assert player.still_in_game
    player._has_won = True
    assert not player.still_in_game


def test_still_in_game_has_won(player):
    player.is_connected = True
    player._has_won = True
    assert not player.still_in_game


def test_still_in_game_player_connected(player):
    player.is_connected = True
    assert player.still_in_game


def test_still_in_game_player_not_connected_may_come_back(player):
    player.is_connected = False
    assert player.still_in_game


def test_still_in_game_player_not_connected_wont_come_back(player):
    player.is_connected = False
    player._number_turns_passed_not_connected = float('inf')
    assert not player.still_in_game


def test_ai_aim(player, board):
    # Just direction
    assert len(player.ai_aim) == 1
    # On arm: full aim
    player._current_square = board[19, 3]
    assert len(player.ai_aim) == 4
    # On wrong arm
    player._current_square = board[8, 3]
    assert len(player.ai_aim) == 1
