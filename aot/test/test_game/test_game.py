# fixtures, ignore the unsued import warnig
from aot.test import (
    board,
    deck,
    game,
    player,
)
from aot.board import Square
from aot.cards import SimpleCard
from aot.game import Game
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


def test_all_players_disconnected(game):
    player1 = game.players[0]
    assert player1 is game.active_player

    for player in game.players:
        player.is_connected = False

    game.pass_turn()

    assert game.is_over
    assert len(game.winners) == 0


def test_only_one_player_connected(game):
    player8 = game.players[-1]

    for player in game.players[:-1]:
        player.is_connected = False

    game.pass_turn()

    assert game.is_over
    assert len(game.winners) == 8
    assert game.winners[0] == player8.name
