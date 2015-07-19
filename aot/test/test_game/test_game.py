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
    assert game.view_possible_squares(('King', 'BLUE')) == set([
        Square(0, 1, 'BLUE'),
        Square(0, 2, 'BLUE'),
        Square(1, 1, 'BLUE'),
        Square(7, 1, 'BLUE'),
        Square(6, 1, 'BLUE')
    ])


def test_play(game):
    assert game.play(('King', 'BLUE'), (0, 1)) == game._board[0, 1]
