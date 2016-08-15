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

# fixtures, ignore the unsued import warnig
from aot.test import (
    board,
    deck,
    game,
    player,
)
from aot.board import Square
from aot.cards import SimpleCard
from aot.game import (
    Game,
    Player,
)
from unittest.mock import MagicMock


def test_game_creation(player):
    player.init_turn = MagicMock()
    Game(None, [player])
    player.init_turn.assert_called_once_with()


def test_game_one_player_left(game):
    game.active_player.play_card = MagicMock()
    for i in range(7):
        game.players[i] = None
    game.play_card(None, (0, 0), check_move=False)
    game.active_player.play_card.assert_called_once_with(None, (0, 0), check_move=False)
    assert game.is_over


def test_play_turn_winning_player(game):
    player1 = game.players[0]
    player2 = game.players[1]

    assert player1 is game.active_player
    game.play_card(None, (16, 8), check_move=False)
    assert player1 is game.active_player
    assert not game.players[0].has_won
    assert not game.is_over

    # Same turn
    player1.can_play = False
    game.play_card(None, (16, 8), check_move=False)
    assert player2 is game.active_player
    assert not game.players[0].has_won
    assert not game.is_over

    # Play other players
    for i in range(8):
        game.play_card(None, (0, i), check_move=False)
        game.play_card(None, (i, 0), check_move=False)

    winner = game.players[0]
    assert game.active_player is not winner
    assert not game.is_over
    assert winner.has_won
    assert 1 == winner.rank


def test_move_last_line_before_winning(game):
    game.play_card(None, (16, 8), check_move=False)
    assert not game.players[0].has_won
    assert not game.is_over

    # Same turn
    game.play_card(None, (17, 8), check_move=False)
    assert not game.players[0].has_won
    assert not game.is_over

    # Play other players
    for i in range(8):
        game.play_card(None, (0, i), check_move=False)
        game.play_card(None, (i, 0), check_move=False)

    winner = game.players[0]
    assert game.active_player is not winner
    assert not game.is_over
    assert winner.has_won
    assert 1 == winner.rank


def test_move_back_before_winning(game):
    game.play_card(None, (16, 8), check_move=False)
    assert not game.players[0].has_won
    assert not game.is_over

    # Same turn
    game.play_card(None, (16, 7), check_move=False)
    assert not game.players[0].has_won
    assert not game.is_over

    # Play other players
    for i in range(8):
        game.play_card(None, (0, i), check_move=False)
        game.play_card(None, (i, 0), check_move=False)

    player = game.players[0]
    assert game.active_player is not player
    assert not game.is_over
    assert not player.has_won


def test_game_over(game):
    for i in range(2, 8):
        game.players[i] = None

    # Player 1
    game.play_card(None, (16, 8), check_move=False)
    game.play_card(None, (16, 8), check_move=False)

    # Player 2, game over
    game.play_card(None, (0, 0), check_move=False)
    game.play_card(None, (0, 0), check_move=False)

    assert game.players[0].has_won
    assert game.is_over
    assert len(game.winners) == 2


def test_game_over_simultanous_winners(game):
    for i in range(2, 8):
        game.players[i] = None

    # Player 1
    game.play_card(None, (16, 8), check_move=False)
    game.play_card(None, (16, 8), check_move=False)

    # Player 2, game over
    game.play_card(None, (20, 8), check_move=False)
    game.play_card(None, (20, 8), check_move=False)

    assert game.players[0].has_won
    assert game.is_over
    assert len(game.winners) == 2


def test_play_missing_players(game):
    game.players[1] = None
    player3 = game.players[2]

    game.play_card(None, (16, 8), check_move=False)
    game.play_card(None, (16, 8), check_move=False)
    assert player3 is game.active_player


def test_pass_turn(game):
    first_player = game.active_player
    game.pass_turn()
    assert game.active_player is not first_player


def test_discard(game):
    first_player = game.active_player
    deck = first_player.deck
    card = deck.first_card_in_hand
    game.discard(card)
    assert first_player.can_play
    assert card not in deck.hand


def test_view_possible_squares(game):
    # Must not throw. Correctness of the list is tested in card module
    card = game.active_player.deck.first_card_in_hand
    game.active_player.view_possible_squares = MagicMock()
    card_properties = SimpleCard(name=card.name, color=card.color)
    game.view_possible_squares(card_properties)
    game.active_player.view_possible_squares.assert_called_once_with(card_properties)


def test_get_square(game):
    assert isinstance(game.get_square(0, 0), Square)
    assert game.get_square(None, 0) is None
    assert game.get_square(0, None) is None
    assert game.get_square(None, None) is None


def test_can_move(game):
    game.active_player.can_move = MagicMock(return_value=True)
    card = game.active_player.deck.first_card_in_hand
    square = game.get_square(4, 0)
    assert game.can_move(card, square)
    game.active_player.can_move.assert_called_once_with(card, square)

    game.active_player.can_move = MagicMock(return_value=False)
    assert not game.can_move(card, square)
    game.active_player.can_move.assert_called_once_with(card, square)


def test_actions(game):
    assert len(game._actions) == 0
    assert game.last_action is None
    game.add_action('An action')
    assert len(game._actions) == 1
    assert game.last_action == 'An action'


def test_disconnect(game):
    player0 = game.players[0]
    assert player0 is game.active_player
    assert player0.is_connected

    ret = game.disconnect(player0.id)
    assert ret is player0
    assert not player0.is_connected


def test_has_enough_players_to_continue(game):
    player1 = game.players[0]
    assert player1 is game.active_player

    # AI player should be counted as not connected.
    player1._is_ai = True
    # Players that won shouldn't be counted as connected
    game.players[1]._has_won = True
    for player in game.players[2:]:
        player.is_connected = False
        player._number_turn_passed_not_connected = float('inf')

    assert not game._has_enough_players_to_continue()


def test_only_one_player_connected(game):
    player8 = game.players[-1]

    for player in game.players[:-1]:
        player.is_connected = False

    for i in range(Player.MAX_NUMBER_TURN_EXPECTING_RECONNECT):
        game.pass_turn()
    game.pass_turn()

    assert game.is_over
    assert len(game.winners) == 8
    assert game.winners[0] == player8.name


def test_continue_game_with_ai(game):
    game._has_enough_players_to_continue = MagicMock(return_value=True)
    game._find_next_player = MagicMock(return_value=game.players[1])
    game.players[1]._is_ai = True

    game._continue_game_if_enough_players()

    assert game.active_player is game.players[1]
    assert game.players[1].is_ai


def test_play_auto(game, mocker):
    card = game.active_player.hand[0]
    find_move_to_play = MagicMock(return_value=(card, None))
    find_cheapeast_card = MagicMock()
    game.discard = MagicMock()
    game.play_card = MagicMock()
    mocker.patch('aot.game.game.find_move_to_play', side_effect=find_move_to_play)
    mocker.patch('aot.game.game.find_cheapest_card', side_effect=find_cheapeast_card)

    game.play_auto()

    assert find_move_to_play.call_count == 1
    find_move_to_play.assert_called_with(
        game.active_player.hand,
        game.active_player.current_square,
        game.active_player.ai_aim,
        game.active_player._board
    )
    game.play_card.assert_called_once_with(card, None)
    assert not find_cheapeast_card.called
    assert not game.discard.called


def test_play_auto_on_last_line(game, mocker):
    card = game.active_player.hand[0]
    find_move_to_play = MagicMock(return_value=(card, None))
    find_cheapeast_card = MagicMock()
    square = next(iter(game.active_player.aim))
    game.active_player._current_square = square
    game.discard = MagicMock()
    game.play_card = MagicMock()
    game.pass_turn = MagicMock()
    mocker.patch('aot.game.game.find_move_to_play', side_effect=find_move_to_play)
    mocker.patch('aot.game.game.find_cheapest_card', side_effect=find_cheapeast_card)

    game.play_auto()

    game.pass_turn.assert_called_once_with()
    assert not find_move_to_play.called
    assert not game.play_card.called
    assert not find_cheapeast_card.called
    assert not game.discard.called


def test_play_auto_no_card_found(game, mocker):
    find_move_to_play = MagicMock(return_value=(None, None))
    find_cheapeast_card = MagicMock(return_value=game.active_player.hand[0])
    game.discard = MagicMock()
    game.play_card = MagicMock()
    mocker.patch('aot.game.game.find_move_to_play', side_effect=find_move_to_play)
    mocker.patch('aot.game.game.find_cheapest_card', side_effect=find_cheapeast_card)

    game.play_auto()

    assert find_move_to_play.call_count == 1
    find_move_to_play.assert_called_with(
        game.active_player.hand,
        game.active_player.current_square,
        game.active_player._ai_direction_aim,
        game.active_player._board
    )
    assert not game.play_card.called
    assert find_cheapeast_card.call_count == 1
    find_cheapeast_card.assert_called_with(game.active_player.hand)
    game.discard.assert_called_once_with(game.active_player.hand[0])
