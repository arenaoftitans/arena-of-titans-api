import pytest
from aot.game import Game
from aot.board import Square


@pytest.fixture()
def game():
    game = Game()
    game.create('moi')
    return game


def test_view_possible_squares(game):
    assert game.player_name == 'moi'
    assert game.view_possible_squares(('King', 'blue')) == set([
        Square(0, 1, 'blue'),
        Square(0, 2, 'blue'),
        Square(1, 1, 'blue'),
        Square(7, 1, 'blue'),
        Square(6, 1, 'blue')
    ])


def test_play(game):
    assert game.play(('King', 'blue'), (0, 1)) == game._board[0, 1]
