from aot.board import Color
from aot.cards.trumps import (
    ModifyNumberMoves,
    RemoveColor,
)
# fixtures, ignore the unsued import warnig
from aot.test import (
    board,
    deck,
    game,
    player,
)
from unittest.mock import MagicMock


def test_affect_modify_number_moves(player):
    player.modify_number_moves = MagicMock()
    trump = ModifyNumberMoves(delta_moves=1, duration=1)
    trump.affect(player)
    player.modify_number_moves.assert_called_once_with(1)


def test_remove_color(player):
    player.deck.remove_color_from_possible_colors = MagicMock()
    card = player.deck.first_card_in_hand
    color = card.color
    trump = RemoveColor(color=color, duration=1)
    trump.affect(player)
    player.deck.remove_color_from_possible_colors.assert_called_once_with(color)


def test_remove_all_colors(player):
    player.deck.remove_color_from_possible_colors = MagicMock()
    trump = RemoveColor(color=Color['ALL'], duration=1)
    trump.affect(player)
    player.deck.remove_color_from_possible_colors.assert_called_once_with(Color['ALL'])


def test_remove_multiple_colors(player):
    player.deck.remove_color_from_possible_colors = MagicMock()
    card = player.deck.first_card_in_hand
    colors = {card.color, Color['BLACK']}
    trump = RemoveColor(colors=colors, duration=1)
    trump.affect(player)
    assert player.deck.remove_color_from_possible_colors.called
    assert player.deck.remove_color_from_possible_colors.call_count == len(colors)


def test_player_can_only_be_affected_by_max_affecting_trumps_number_trump(game):
    player1 = game.players[0]

    for i in range(player1.MAX_NUMBER_AFFECTING_TRUMPS):
        trump = RemoveColor(colors=[Color['BLACK']], duration=1)
        assert player1._affect_by(trump)
        assert len(player1.affecting_trumps) == i + 1

    trump = RemoveColor(colors=[Color['BLACK']], duration=1)
    assert not player1._affect_by(trump)
    assert len(player1.affecting_trumps) == player1.MAX_NUMBER_AFFECTING_TRUMPS
