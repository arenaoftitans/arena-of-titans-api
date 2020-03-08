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

import pytest

from aot.game import Player
from aot.game.board import Color
from aot.game.cards import Card
from aot.game.trumps import ChangeSquare, SimpleTrump, Trump, TrumpList
from aot.game.trumps.exceptions import (
    GaugeTooLowToPlayTrumpError,
    MaxNumberAffectingTrumpsError,
    MaxNumberTrumpPlayedError,
    TrumpHasNoEffectError,
)


def test_view_possible_squares(player):  # noqa: F811
    player.deck.view_possible_squares = MagicMock()
    card = player.deck.first_card_in_hand
    player.view_possible_squares(card)
    player.deck.view_possible_squares.assert_called_once_with(card, player.current_square)


def test_can_move(player):  # noqa: F811
    square = player.current_square
    card = player.deck.first_card_in_hand
    player.deck.view_possible_squares = MagicMock(return_value={square})
    assert player.can_move(card, square)
    player.deck.view_possible_squares.assert_called_with(card, square)

    player.deck.view_possible_squares = MagicMock(return_value=set())
    assert not player.can_move(card, square)
    player.deck.view_possible_squares.assert_called_with(card, square)


def test_has_remaining_moves_to_play(player):  # noqa: F811
    assert player.has_remaining_moves_to_play
    player._number_moves_played = player.MAX_NUMBER_MOVE_TO_PLAY
    assert not player.has_remaining_moves_to_play


def test_move(player, board):  # noqa: F811
    start_square = player.current_square
    assert start_square.occupied
    assert 6 == start_square.x
    assert 7 == start_square.y

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


def test_wins(player):  # noqa: F811
    player.wins(rank=1)

    assert player.has_won
    assert 1 == player.rank


def test_init_game_player_0(player, board):  # noqa: F811
    start_square = player.current_square
    assert start_square.occupied
    assert 6 == start_square.x
    assert 7 == start_square.y

    # Check the deck
    deck = player.deck  # noqa: 811
    assert deck is not None
    assert 5 == deck.number_cards_in_hand

    # Check that the player has not won
    assert not player.has_won
    assert not player.has_reached_aim
    assert -1 == player.rank

    # Check the aim
    expected_aim = [board[15, 1], board[15, 2], board[15, 3], board[15, 4]]
    assert expected_aim == player.aim


def test_init_game_player_1(board, deck):  # noqa: F811
    player = Player(None, None, 1, board, deck, MagicMock())  # noqa: 811
    start_square = player.current_square
    assert start_square.occupied
    assert 6 == start_square.x
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
    expected_aim = [board[15, 1], board[15, 2], board[15, 3], board[15, 4]]
    assert expected_aim == player.aim


def test_init_turn(player):  # noqa: F811
    player.can_play = False
    player._power = MagicMock()
    player._power.passive = True

    player.init_turn()

    assert player.can_play
    assert player.current_square == player.last_square_previous_turn
    player._power.affect.assert_called_once_with(player=player)


def test_complete_turn(player):  # noqa: F811
    player.deck.revert_to_default = MagicMock()
    trump1 = MagicMock()
    trump1.duration = 0
    trump2 = MagicMock()
    trump2.duration = 2
    power = MagicMock()
    player._affecting_trumps = [trump1, trump2]
    player._number_moves_to_play = 0
    player._power = power

    player.complete_turn()

    player.deck.revert_to_default.assert_called_once_with()
    trump1.consume.assert_called_once_with()
    trump2.consume.assert_called_once_with()
    power.turn_teardown.assert_called_once_with()
    assert len(player.affecting_trumps) == 1
    assert player.affecting_trumps[0] is trump2
    assert player._number_moves_to_play == player.MAX_NUMBER_MOVE_TO_PLAY


def test_complet_turn_collect_all_consumed_trumps(player):  # noqa: F811
    trump1 = MagicMock()
    trump1.duration = 0
    trump2 = MagicMock()
    trump2.duration = 0
    player._affecting_trumps = [trump1, trump2]
    player._number_moves_to_play = 0

    player.complete_turn()

    assert len(player.affecting_trumps) == 0


def test_play_card_cannot_play(board, player):  # noqa: F811
    player.deck.play = MagicMock()
    player.deck.init_turn = MagicMock()
    start_square = player.current_square
    card = Card(board)

    assert not player.play_card(card, (3, 1), check_move=False)

    player.deck.play.assert_called_once_with(card)
    end_square = player.current_square
    player._gauge.move.assert_called_once_with(start_square, end_square, card)
    assert not start_square.occupied
    assert end_square.occupied
    assert start_square.x != end_square.x and start_square.y != end_square.y
    assert 3 == end_square.x
    assert 1 == end_square.y


def test_play_card_no_move_left(board, player):  # noqa: F811
    player.deck.play = MagicMock()
    player.deck.init_turn = MagicMock()
    card = Card(board)
    player._number_moves_played = player.MAX_NUMBER_MOVE_TO_PLAY

    ret = player.play_card(card, (3, 1), check_move=False)

    assert ret is None
    assert not player.deck.play.called
    assert not player._gauge.move.called


def test_play_card(board, player):  # noqa: F811
    player.deck.play = MagicMock()
    player.deck.init_turn = MagicMock()
    card = Card(board)
    start_square = player.current_square

    player.play_card(card, (0, 0), check_move=False)

    end_square = player.current_square
    player._gauge.move.assert_called_once_with(start_square, end_square, card)
    player.play_card(card, (0, 0), check_move=False)

    assert player.deck.play.call_count == 2
    assert player._gauge.move.call_count == 2
    player.deck.play.assert_called_with(card)
    player.deck.init_turn.assert_called_once_with()


def test_play_card_with_special_actions(player):  # noqa: F811
    player.deck.play = MagicMock()
    player.deck.init_turn = MagicMock()
    player._complete_action = MagicMock()
    start_square = player.current_square
    card = player.deck.first_card_in_hand
    card._special_actions = TrumpList()
    card._special_actions.append(SimpleTrump(name="action", type=None, args=None))

    assert player.play_card(card, (3, 1), check_move=False)

    player.deck.play.assert_called_once_with(card)
    end_square = player.current_square
    player._gauge.move.assert_called_once_with(start_square, end_square, card)
    assert not start_square.occupied
    assert end_square.occupied
    assert start_square.x != end_square.x and start_square.y != end_square.y
    assert 3 == end_square.x
    assert 1 == end_square.y
    assert player._special_actions_names == ["action"]
    assert player._special_actions is card._special_actions
    assert not player._complete_action.called
    assert player.special_action_start_time > 0


def test_has_special_actions(player):  # noqa: F811
    actions = TrumpList()
    actions.append(SimpleTrump(name="action", type=None, args=None))
    player.special_actions = actions

    assert player.has_special_actions
    assert player.name_next_special_action == "action"
    assert player.has_special_actions

    player._special_actions_names.remove("action")
    assert not player.has_special_actions


def test_play_special_action(player):  # noqa: F811
    action = MagicMock()
    action.name = "Action"
    target = MagicMock()
    player._special_actions_names = {"action"}
    kwargs = {"square": "square-0-0"}

    player.play_special_action(action, target=target, action_args=kwargs)

    action.affect.assert_called_once_with(player=target, **kwargs)
    assert not player.has_special_actions


def test_play_special_action_no_args(player):  # noqa: F811
    action = MagicMock()
    action.name = "action"
    target = MagicMock()
    player._special_actions_names = {"action"}

    player.play_special_action(action, target=target)

    action.affect.assert_called_once_with(player=target)
    assert not player.has_special_actions


def test_cancel_special_action(player):  # noqa: F811
    player._special_actions_names = ["action", "action2"]

    player.cancel_special_action(SimpleTrump(name="action", type=None, args=None))

    assert player._special_actions_names == ["action2"]


def test_reach_aim(player):  # noqa: F811
    player._aim = {player.current_square}
    player._last_square_previous_turn = player.current_square
    assert player.has_reached_aim


def test_play_wrong_card(player):  # noqa: F811
    player.deck.play = MagicMock()
    # None of these tests must throw.
    player.play_card(None, None)
    player.play_card(None, (0, 0))
    assert not player._gauge.move.called
    player.play_card(player.hand[0], None)
    assert player._gauge.move.called


def test_pass(player):  # noqa: F811
    player.deck.init_turn = MagicMock()
    player.init_turn()
    assert player.can_play
    assert player._number_turns_passed_not_connected == 0
    player.pass_turn()

    player.deck.init_turn.assert_called_once_with()
    assert not player.can_play
    assert player._number_turns_passed_not_connected == 0


def test_pass_not_connected(player):  # noqa: F811
    player.is_connected = False
    player.deck.init_turn = MagicMock()
    player.init_turn()
    assert player.can_play
    assert player._number_turns_passed_not_connected == 0
    player.pass_turn()

    player.deck.init_turn.assert_called_once_with()
    assert player._number_turns_passed_not_connected == 1


def test_expect_reconnect(player):  # noqa: F811
    assert player.expect_reconnect
    player._number_turns_passed_not_connected = Player.MAX_NUMBER_TURN_EXPECTING_RECONNECT + 1
    assert not player.expect_reconnect


def test_reconnect(player):  # noqa: F811
    player._number_turns_passed_not_connected = 2
    player.is_connected = False
    assert player._number_turns_passed_not_connected == 2
    player.is_connected = True
    assert player._number_turns_passed_not_connected == 0


def test_discard(player):  # noqa: F811
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


def test_get_card(player):  # noqa: F811
    player.deck.get_card = MagicMock()
    card = player.deck.first_card_in_hand
    player.get_card(card.name, card.color)
    player.deck.get_card.assert_called_once_with(card.name, card.color)


def test_modify_number_moves(player):  # noqa: F811
    player.modify_number_moves(5)
    assert player._number_moves_to_play == player.MAX_NUMBER_MOVE_TO_PLAY + 5
    player.complete_turn()
    assert player._number_moves_to_play == player.MAX_NUMBER_MOVE_TO_PLAY

    player.modify_number_moves(-1)
    assert player._number_moves_to_play == player.MAX_NUMBER_MOVE_TO_PLAY - 1
    player.complete_turn()
    assert player._number_moves_to_play == player.MAX_NUMBER_MOVE_TO_PLAY


def test_modify_card_colors(player):  # noqa: F811
    player._deck = MagicMock()
    filter_ = lambda x: True  # noqa: E731

    player.modify_card_colors({"BLUE"}, filter_=filter_)

    player._deck.modify_colors.assert_called_once_with({"BLUE"}, filter_=filter_)


def test_modify_card_number_moves(player):  # noqa: F811
    player._deck = MagicMock()
    filter_ = lambda x: True  # noqa: E731

    player.modify_card_number_moves(5, filter_=filter_)

    player._deck.modify_number_moves.assert_called_once_with(5, filter_=filter_)


def test_modify_trump_duration(player):  # noqa: F811
    player._revert_to_default = MagicMock()
    tower = MagicMock()
    tower.name = "Tower"
    tower.duration = 2
    tower.temporary = False
    blizzard = MagicMock()
    blizzard.name = "Blizzard"
    blizzard.duration = 4
    blizzard.temporary = False
    ram = MagicMock()
    ram.name = "Ram"
    ram.duration = 0
    ram.temporary = True
    # Note: the trump that modifies the durations in in the affecting trumps list
    player._affecting_trumps = [tower, blizzard, ram]

    player.modify_affecting_trump_durations(-2)

    assert tower.duration == 0
    assert blizzard.duration == 2
    assert player.affecting_trumps == (blizzard,)
    # Trumps must be disabled then re-enabled to take into account the changes.
    assert player._revert_to_default.called
    # The tower is not available any more
    assert not tower.affect.called
    assert blizzard.affect.called
    # The ram must not be enabled again or we will enter an infinite loop that will call
    # player.modify_affecting_trump_durations again.
    assert not ram.affect.called


def test_modify_trump_duration_with_filter(player):  # noqa: F811
    player._revert_to_default = MagicMock()
    tower = MagicMock()
    tower.name = "Tower"
    tower.duration = 2
    tower.temporary = False
    blizzard = MagicMock()
    blizzard.name = "Blizzard"
    blizzard.duration = 4
    blizzard.temporary = False
    ram = MagicMock()
    ram.name = "Ram"
    ram.duration = 0
    ram.temporary = True
    # Note: the trump that modifies the durations in in the affecting trumps list
    player._affecting_trumps = [tower, blizzard, ram]

    player.modify_affecting_trump_durations(-2, filter_=lambda trump: trump.name == "Tower")

    assert tower.duration == 0
    assert blizzard.duration == 4
    assert player._affecting_trumps == [blizzard]
    assert player._revert_to_default.called
    # The tower is not available any more
    assert not tower.affect.called
    assert blizzard.affect.called
    # The ram must not be enabled again or we will enter an infinite loop that will call
    # player.modify_affecting_trump_durations again.
    assert not ram.affect.called


def test_get_trump(player):  # noqa: F811
    with pytest.raises(IndexError):
        assert player.get_trump(None)
    with pytest.raises(IndexError):
        assert player.get_trump("wrong_trump") is None
    assert isinstance(player.get_trump("Reinforcements"), Trump)


def test_trumps_property(player):  # noqa: F811
    assert len(player.trumps) == 4
    trump = player.trumps[0]
    assert "name" in trump
    assert "description" in trump
    assert "cost" in trump
    assert "duration" in trump
    assert "must_target_player" in trump


def test_affecting_trumps(player):  # noqa: F811
    trump = player.get_trump("Reinforcements")
    trump.affect = MagicMock()
    trump.consume = MagicMock()
    player._affect_by(trump)
    player.init_turn()

    assert len(player.affecting_trumps) == 1
    assert player.affecting_trumps[0] is trump
    trump.affect.assert_called_once_with(player=player)


def test_play_trump(player):  # noqa: F811
    player.init_turn()
    trump = player.get_trump("Reinforcements")
    trump.affect = MagicMock()

    player.play_trump(trump, target=player)
    trump.affect.assert_called_once_with(player=player)
    player._gauge.can_play_trump.assert_called_once_with(trump)
    player._gauge.play_trump.assert_called_once()
    with pytest.raises(MaxNumberTrumpPlayedError):
        player.play_trump(trump, target=player)
    assert trump.affect.call_count == 1

    player.complete_turn()
    player.init_turn()
    player.play_trump(trump, target=player)
    assert trump.affect.call_count == 2
    assert player._gauge.can_play_trump.call_count == 2
    player._gauge.play_trump.call_count == 2
    trump.affect.assert_called_with(player=player)


def test_play_trump_target_type_board(player):  # noqa: F811
    player.init_turn()
    trump = ChangeSquare()
    target = {
        "x": 0,
        "y": 0,
        "color": "blue",
    }

    assert player._board[0, 0].color == Color.RED

    player.play_trump(trump, target=target)
    assert player._board[0, 0].color == Color.BLUE
    player._gauge.can_play_trump.assert_called_once_with(trump)
    player._gauge.play_trump.assert_called_once()


def test_number_affecting_trumps(player):  # noqa: F811
    # Check that the number of played trumps is only increased if the targeted
    # player can be affected.
    trump = player.get_trump("Reinforcements")
    player._affect_by(trump)
    player._affect_by(trump)
    player._affect_by(trump)
    player._affect_by(trump)

    with pytest.raises(MaxNumberAffectingTrumpsError):
        player._affect_by(trump)
    assert len(player.affecting_trumps) == 4

    player.init_turn()
    with pytest.raises(MaxNumberAffectingTrumpsError):
        player.play_trump(trump, target=player)
    assert len(player.affecting_trumps) == 4
    assert not player._gauge.play_trump.called
    assert player._number_trumps_played == 0


def test_trump_affect_raises(player, mocker):  # noqa: F811
    trump = player.get_trump("Reinforcements")
    player._can_play = True

    def affect(player):
        raise TrumpHasNoEffectError

    trump.affect = affect

    with pytest.raises(TrumpHasNoEffectError):
        player.play_trump(trump, target=player)

    assert len(player.affecting_trumps) == 0


def test_number_gauge_empty(player):  # noqa: F811
    trump = player.get_trump("Reinforcements")
    player._gauge.can_play_trump = MagicMock(return_value=False)
    player.init_turn()

    with pytest.raises(GaugeTooLowToPlayTrumpError):
        player.play_trump(trump, target=player)
    assert not player._gauge.play_trump.called
    assert player._number_trumps_played == 0


def test_still_in_game_ai(player):  # noqa: F811
    player._is_ai = True
    player.is_connected = False
    assert player.still_in_game
    player._has_won = True
    assert not player.still_in_game


def test_still_in_game_has_won(player):  # noqa: F811
    player.is_connected = True
    player._has_won = True
    assert not player.still_in_game


def test_still_in_game_player_connected(player):  # noqa: F811
    player.is_connected = True
    assert player.still_in_game


def test_still_in_game_player_not_connected_may_come_back(player):  # noqa: F811
    player.is_connected = False
    assert player.still_in_game


def test_still_in_game_player_not_connected_wont_come_back(player):  # noqa: F811
    player.is_connected = False
    player._number_turns_passed_not_connected = float("inf")
    assert not player.still_in_game


def test_ai_aim(player, board):  # noqa: F811
    player._current_square = board[19, 3]
    assert len(player.ai_aim) == 4


def test_complete_special_actions(player):  # noqa: F811
    player._complete_action = MagicMock()

    player.complete_special_actions()

    player._complete_action.assert_called_once_with()


def test_trumps_statuses(player):  # noqa: F811
    trump1 = MagicMock()
    trump2 = MagicMock()

    def can_play_trump(trump):
        return trump is trump1

    player.can_play_trump = MagicMock(side_effect=can_play_trump)

    player._available_trumps = [trump1, trump2]

    assert player.trumps_statuses == [True, False]
