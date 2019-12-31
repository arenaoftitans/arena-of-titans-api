import json
from os import path


def load_board(name):
    directory = path.dirname(path.realpath(__file__))
    board_file_name = path.join(directory, f"{name}.json")
    with open(board_file_name, "r") as board_file:
        board_data = json.load(board_file)

    return board_data
