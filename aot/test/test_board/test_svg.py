import json
import pytest

from aot.board import SvgBoardCreator


@pytest.fixture()
def svg_board():
    with open('aot/resources/games/standard.json') as games:
        game = json.load(games)
        board_description = game['board']
        return SvgBoardCreator(board_description)


@pytest.fixture()
def height():
    with open('aot/resources/games/standard.json') as games:
        game_description = json.load(games)['board']
        return len(game_description['inner_circle_colors']) + \
            len(game_description['arms_colors'])


@pytest.fixture()
def width():
    with open('aot/resources/games/standard.json') as games:
        game_description = json.load(games)['board']
        return game_description['number_arms'] * game_description['arms_width']


def test_number_square(svg_board, height, width):
    board_layer = svg_board.svg.xpath(
        './/ns:g[@id="boardLayer"]',
        namespaces=SvgBoardCreator.NS)[0]
    assert len(board_layer) == height * width


def test_paws(svg_board):
    pawn_layer = svg_board.svg.xpath(
        './/ns:g[@id="pawnLayer"]',
        namespaces=SvgBoardCreator.NS)[0]
    assert len(pawn_layer) == 8


def test_str(svg_board):
    assert str(svg_board)
    assert '&gt;' not in str(svg_board)
