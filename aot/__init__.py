import json


def get_game_description(name='standard'):
    with open('aot/resources/games/{}.json'.format(name)) as games:
        return json.load(games)


def get_board_description(name='standard'):
    return get_game_description(name)['board']
