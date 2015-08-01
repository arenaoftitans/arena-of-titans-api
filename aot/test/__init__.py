import pytest

from aot import get_board_description
from aot.board import Board


@pytest.fixture()
def board():
    board_description = get_board_description()
    return Board(board_description)
