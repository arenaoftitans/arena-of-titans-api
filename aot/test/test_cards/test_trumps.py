from aot.board import Color
from aot.cards.trumps import ModifyNumberMoves
from aot.cards.trumps import RemoveColor
# fixtures, ignore the unsued import warnig
from aot.test import board
from aot.test import game


def test_affect_modify_number_moves(game):
    player1 = game.players[0]
    player2 = game.players[1]
    trump = ModifyNumberMoves(delta_moves=1, duration=1)
    player1.affect_by(trump)

    assert player1 is game.active_player
    game.play_card(None, (0, 0), check_move=False)
    assert player1 is game.active_player
    game.play_card(None, (0, 0), check_move=False)
    assert player1 is game.active_player
    game.play_card(None, (0, 0), check_move=False)
    assert player2 is game.active_player

    for _ in game.players[1:]:
        game.pass_turn()

    assert player1 is game.active_player
    game.play_card(None, (0, 0), check_move=False)
    assert player1 is game.active_player
    game.play_card(None, (0, 0), check_move=False)
    assert player2 is game.active_player


def test_affect_modify_number_moves_middle_turn(game):
    player1 = game.players[0]
    player2 = game.players[1]
    trump = ModifyNumberMoves(delta_moves=1, duration=1)

    assert player1 is game.active_player
    game.play_card(None, (0, 0), check_move=False)
    assert player1 is game.active_player
    player1.affect_by(trump)
    game.play_card(None, (0, 0), check_move=False)
    assert player1 is game.active_player
    game.play_card(None, (0, 0), check_move=False)
    assert player2 is game.active_player

    for _ in game.players[1:]:
        game.pass_turn()

    assert player1 is game.active_player
    game.play_card(None, (0, 0), check_move=False)
    assert player1 is game.active_player
    game.play_card(None, (0, 0), check_move=False)
    assert player2 is game.active_player


def test_remove_color(game):
    player1 = game.players[0]
    card = player1.deck.first_card_in_hand
    color = card.color
    trump = RemoveColor(color=color, duration=1)
    player1.affect_by(trump)
    assert color not in card.colors


def test_remove_all_colors(game):
    player1 = game.players[0]
    card = player1.deck.first_card_in_hand
    trump = RemoveColor(color=Color['ALL'], duration=1)
    player1.affect_by(trump)
    assert 0 == len(card.colors)


def test_remove_multiple_colors(game):
    player1 = game.players[0]
    card = player1.deck.first_card_in_hand
    trump = RemoveColor(colors=[card.color, Color['BLACK']], duration=1)
    player1.affect_by(trump)
    assert card.color not in card.colors
    assert Color['BLACK'] not in card.colors
