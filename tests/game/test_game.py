################################################################################
# Copyright (C) 2015-2020 by Last Run Contributors.
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

from aot.game import Game, Player
from aot.game.actions import nothing_has_happened_action
from aot.game.board import Square


def test_eq(board, player):  # noqa: F811
    other_obj = {}

    assert not Game(board, [player]) == other_obj
    assert Game(board, [player]) != Game(board, [player])

    assert Game(board, [player], game_id="game_id") == Game(board, [player], game_id="game_id")

    assert Game(board, [player], game_id="game_id") != Game(board, [player], game_id="game_id2")


def test_game_creation(player):  # noqa: F811
    player.init_turn = MagicMock()
    Game(None, [player])
    player.init_turn.assert_called_once_with()


def test_play_card_with_special_actions(game):  # noqa: F811
    game._active_player.play_card = MagicMock(return_value=True)
    game._continue_game_if_enough_players = MagicMock()

    has_actions = game.play_card(None, None)

    assert not game._continue_game_if_enough_players.called
    assert has_actions


def test_play_card_no_special_action(game):  # noqa: F811
    game._active_player.play_card = MagicMock(return_value=False)
    game._continue_game_if_enough_players = MagicMock()

    has_actions = game.play_card(None, None)

    assert game._continue_game_if_enough_players.called
    assert not has_actions


def test_game_one_player_left(game):  # noqa: F811
    game.active_player.play_card = MagicMock(return_value=None)
    for i in range(3):
        game._players[i] = None
    game.play_card(None, (0, 0), check_move=False)
    game.active_player.play_card.assert_called_once_with(None, (0, 0), check_move=False)
    assert game.is_over


def test_play_turn_winning_player(game):  # noqa: F811
    player1 = game._players[0]
    player2 = game._players[1]
    player1_aim_square = player1.aim[0]

    assert player1 is game.active_player
    game.play_card(game.active_player.deck.first_card_in_hand, player1_aim_square, check_move=False)
    assert player1 is game.active_player
    assert not game._players[0].has_won
    assert not game.is_over

    # Same turn
    player1.can_play = False
    game.play_card(game.active_player.deck.first_card_in_hand, player1_aim_square, check_move=False)
    assert player2 is game.active_player
    assert not game._players[0].has_won
    assert not game.is_over

    # Play other players
    for i in range(4):
        game.play_card(game.active_player.deck.first_card_in_hand, (0, i), check_move=False)
        game.play_card(game.active_player.deck.first_card_in_hand, (i, 0), check_move=False)

    winner = game._players[0]
    assert game.active_player is not winner
    assert not game.is_over
    assert winner.has_won
    assert 1 == winner.rank


def test_move_last_line_before_winning(game):  # noqa: F811
    game.play_card(
        game.active_player.deck.first_card_in_hand, game._players[0].aim[0], check_move=False
    )
    assert not game._players[0].has_won
    assert not game.is_over

    # Same turn
    game.play_card(
        game.active_player.deck.first_card_in_hand, game._players[0].aim[1], check_move=False
    )
    assert not game._players[0].has_won
    assert not game.is_over

    # Play other players
    for i in range(8):
        game.play_card(game.active_player.deck.first_card_in_hand, (0, i), check_move=False)
        game.play_card(game.active_player.deck.first_card_in_hand, (i, 0), check_move=False)

    winner = game._players[0]
    assert game.active_player is not winner
    assert not game.is_over
    assert winner.has_won
    assert 1 == winner.rank


def test_move_back_before_winning(game):  # noqa: F811
    game.play_card(game.active_player.deck.first_card_in_hand, (16, 8), check_move=False)
    assert not game._players[0].has_won
    assert not game.is_over

    # Same turn
    game.play_card(game.active_player.deck.first_card_in_hand, (16, 7), check_move=False)
    assert not game._players[0].has_won
    assert not game.is_over

    # Play other players
    for _ in range(8):
        game.pass_turn()

    player = game._players[0]  # noqa: 811
    assert game.active_player is not player
    assert not game.is_over
    assert not player.has_won


def test_game_over(game):  # noqa: F811
    for i in range(2, 4):
        game._players[i] = None

    # Player 1
    game.play_card(
        game.active_player.deck.first_card_in_hand, game._players[0].aim[0], check_move=False
    )
    game.play_card(
        game.active_player.deck.first_card_in_hand, game._players[0].aim[0], check_move=False
    )

    # Player 2, game over
    game.pass_turn()

    assert game._players[0].has_won
    assert game.is_over
    assert len(game.winners) == 2


def test_game_over_simultanous_winners(game):  # noqa: F811
    for i in range(2, 4):
        game._players[i] = None

    # Player 1
    game.play_card(
        game.active_player.deck.first_card_in_hand, game._players[0].aim[0], check_move=False
    )
    game.play_card(
        game.active_player.deck.first_card_in_hand, game._players[0].aim[0], check_move=False
    )

    # Player 2, game over
    game.play_card(
        game.active_player.deck.first_card_in_hand, game._players[1].aim[1], check_move=False
    )
    game.play_card(
        game.active_player.deck.first_card_in_hand, game._players[1].aim[1], check_move=False
    )

    assert game._players[0].has_won
    assert game.is_over
    assert len(game.winners) == 2


def test_play_missing_players(game):  # noqa: F811
    game._players[1] = None
    player3 = game._players[2]

    game.play_card(game.active_player.deck.first_card_in_hand, (16, 8), check_move=False)
    game.play_card(game.active_player.deck.first_card_in_hand, (16, 8), check_move=False)
    assert player3 is game.active_player


def test_pass_turn(game):  # noqa: F811
    first_player = game.active_player
    game.pass_turn()
    assert game.active_player is not first_player


def test_discard(game):  # noqa: F811
    first_player = game.active_player
    deck = first_player.deck  # noqa: 811
    card = deck.first_card_in_hand
    game.discard(card)
    assert first_player.can_play
    assert card not in deck.hand


def test_view_possible_squares(game):  # noqa: F811
    # Must not throw. Correctness of the list is tested in card module
    card = game.active_player.deck.first_card_in_hand
    game.active_player.view_possible_squares = MagicMock()
    game.view_possible_squares(card)
    game.active_player.view_possible_squares.assert_called_once_with(card)


def test_get_square(game):  # noqa: F811
    assert isinstance(game.get_square(6, 10), Square)
    assert game.get_square(None, 0) is None
    assert game.get_square(0, None) is None
    assert game.get_square(None, None) is None


def test_can_move(game):  # noqa: F811
    game.active_player.can_move = MagicMock(return_value=True)
    card = game.active_player.deck.first_card_in_hand
    square = game.get_square(4, 0)
    assert game.can_move(card, square)
    game.active_player.can_move.assert_called_once_with(card, square)

    game.active_player.can_move = MagicMock(return_value=False)
    assert not game.can_move(card, square)
    game.active_player.can_move.assert_called_once_with(card, square)


def test_actions(game):  # noqa: F811
    assert len(game.actions) == 1
    assert game.actions[0] is nothing_has_happened_action
    game.add_action("An action")
    assert len(game._actions) == 1
    assert game.actions[0] == "An action"


def test_disconnect(game):  # noqa: F811
    player0 = game._players[0]
    assert player0 is game.active_player
    assert player0.is_connected

    ret = game.get_player_by_id(player0.id)
    assert ret is player0


def test_has_enough_players_to_continue(game):  # noqa: F811
    player1 = game._players[0]
    assert player1 is game.active_player

    # AI player should be counted as not connected.
    player1._is_ai = True
    # Players that won shouldn't be counted as connected
    game._players[1]._has_won = True
    for player in game._players[2:]:  # noqa
        player.is_connected = False
        player._number_turns_passed_not_connected = float("inf")

    assert not game._has_enough_players_to_continue()


def test_only_one_player_connected(game):  # noqa: F811
    last_player = game._players[-1]

    for player in game._players[:-1]:  # noqa
        player.is_connected = False

    for _ in range(Player.MAX_NUMBER_TURN_EXPECTING_RECONNECT):
        game.pass_turn()
    game.pass_turn()

    assert game.is_over
    assert len(game.winners) == 4
    assert game.winners[0] == last_player.name


def test_continue_game_with_ai(game):  # noqa: F811
    game._has_enough_players_to_continue = MagicMock(return_value=True)
    game._find_next_player = MagicMock(return_value=game._players[1])
    game._players[1]._is_ai = True

    game._continue_game_if_enough_players()

    assert game.active_player is game._players[1]
    assert game._players[1].is_ai


def test_dont_increase_nb_turns_if_same_player(game):  # noqa: F811
    assert game.nb_turns == 0

    game._active_player.can_play = True

    game._find_next_player()

    assert game.nb_turns == 0


def test_increase_nb_turns(game):  # noqa: F811
    assert game.nb_turns == 0

    game._active_player.can_play = False
    # Make sure the next player is the active player.
    game._players = [game._active_player]

    game._find_next_player()

    assert game.nb_turns == 1


def test_play_auto(game, mocker):  # noqa: F811
    card = game.active_player.hand[0]
    card._special_actions = None
    find_move_to_play = MagicMock(return_value=(card, None))
    find_cheapeast_card = MagicMock()
    game.discard = MagicMock()
    game.play_card = MagicMock()
    game.complete_special_actions = MagicMock()
    mocker.patch("aot.game.game.find_move_to_play", side_effect=find_move_to_play)
    mocker.patch("aot.game.game.find_cheapest_card", side_effect=find_cheapeast_card)

    game.play_auto()

    assert find_move_to_play.call_count == 1
    find_move_to_play.assert_called_with(
        game.active_player.hand,
        game.active_player.current_square,
        game.active_player.ai_aim,
        game.active_player._board,
    )
    game.play_card.assert_called_once_with(card, None)
    assert not find_cheapeast_card.called
    assert not game.discard.called
    assert not game.complete_special_actions.called


def test_play_auto_card_with_special_action(game, mocker):  # noqa: F811
    card = game.active_player.hand[0]
    card._special_actions = ["action"]
    find_move_to_play = MagicMock(return_value=(card, None))
    find_cheapeast_card = MagicMock()
    game.discard = MagicMock()
    game.play_card = MagicMock()
    game.complete_special_actions = MagicMock()
    mocker.patch("aot.game.game.find_move_to_play", side_effect=find_move_to_play)
    mocker.patch("aot.game.game.find_cheapest_card", side_effect=find_cheapeast_card)

    game.play_auto()

    assert find_move_to_play.call_count == 1
    find_move_to_play.assert_called_with(
        game.active_player.hand,
        game.active_player.current_square,
        game.active_player.ai_aim,
        game.active_player._board,
    )
    game.play_card.assert_called_once_with(card, None)
    assert not find_cheapeast_card.called
    assert not game.discard.called
    game.complete_special_actions.assert_called_once_with()


def test_play_auto_on_last_line(game, mocker):  # noqa: F811
    card = game.active_player.hand[0]
    find_move_to_play = MagicMock(return_value=(card, None))
    find_cheapeast_card = MagicMock()
    square = next(iter(game.active_player.aim))
    game.active_player._current_square = square
    game.discard = MagicMock()
    game.play_card = MagicMock()
    game.pass_turn = MagicMock()
    mocker.patch("aot.game.game.find_move_to_play", side_effect=find_move_to_play)
    mocker.patch("aot.game.game.find_cheapest_card", side_effect=find_cheapeast_card)

    game.play_auto()

    game.pass_turn.assert_called_once_with()
    assert not find_move_to_play.called
    assert not game.play_card.called
    assert not find_cheapeast_card.called
    assert not game.discard.called


def test_play_auto_no_moves_when_starting_turn(game, mocker):  # noqa: F811
    card = game.active_player.hand[0]
    find_move_to_play = MagicMock(return_value=(card, None))
    find_cheapeast_card = MagicMock()
    game.active_player._number_moves_played = float("inf")
    game.discard = MagicMock()
    game.play_card = MagicMock()
    game.pass_turn = MagicMock()
    mocker.patch("aot.game.game.find_move_to_play", side_effect=find_move_to_play)
    mocker.patch("aot.game.game.find_cheapest_card", side_effect=find_cheapeast_card)

    game.play_auto()

    game.pass_turn.assert_called_once_with()
    assert not find_move_to_play.called
    assert not game.play_card.called
    assert not find_cheapeast_card.called
    assert not game.discard.called


def test_play_auto_no_card_found(game, mocker):  # noqa: F811
    find_move_to_play = MagicMock(return_value=(None, None))
    find_cheapeast_card = MagicMock(return_value=game.active_player.hand[0])
    game.discard = MagicMock()
    game.play_card = MagicMock()
    mocker.patch("aot.game.game.find_move_to_play", side_effect=find_move_to_play)
    mocker.patch("aot.game.game.find_cheapest_card", side_effect=find_cheapeast_card)

    game.play_auto()

    assert find_move_to_play.call_count == 1
    find_move_to_play.assert_called_with(
        game.active_player.hand,
        game.active_player.current_square,
        game.active_player.aim,
        game.active_player._board,
    )
    assert not game.play_card.called
    assert find_cheapeast_card.call_count == 1
    find_cheapeast_card.assert_called_with(game.active_player.hand)
    game.discard.assert_called_once_with(game.active_player.hand[0])


def test_complete_special_actions(game):  # noqa: F811
    game._continue_game_if_enough_players = MagicMock()
    game.active_player.complete_special_actions = MagicMock()

    game.complete_special_actions()

    game.active_player.complete_special_actions.assert_called_once_with()
    game._continue_game_if_enough_players.assert_called_once_with()


def test_play_special_action(game):  # noqa: F811
    game.active_player.play_special_action = MagicMock()

    game.play_special_action(None, target=None, context=None)

    assert game.active_player.play_special_action.called


def test_cancel_special_action(game):  # noqa: F811
    game.active_player.cancel_special_action = MagicMock()

    game.cancel_special_action(None)

    game.active_player.cancel_special_action.assert_called_once_with(None)
