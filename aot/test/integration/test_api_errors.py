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

import logging
import pytest

from aot import get_number_players
from aot.game import Player
from aot.test.integration import (
    flush_cache,
    create_game,
    player1,
    player2,
    players,
)


logging.basicConfig(level=logging.DEBUG)


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_not_enough_players(player1):
    yield from player1.send('init_game')
    create_game_request = [{
        "name": "Player 1",
        "index": 0,
    }]
    yield from player1.send(
        'create_game',
        message_override={'create_game_request': create_game_request})
    response = yield from player1.recv()
    assert response == {
        'error': 'Number of registered players differs with number of '
                 'players descriptions or too many/too few players are '
                 'registered.',
    }


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_wrong_request(player1):
    yield from player1.send('init_game')
    yield from player1.send('create_game', message_override={'rt': 'TOTO'})
    response = yield from player1.recv()
    assert response == {'error': 'Unknown request: TOTO.'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_wrong_play_request(player1, player2):
    yield from create_game(player1, player2)
    yield from player1.send('pass_turn', message_override={'rt': 'TOTO'})
    response = yield from player1.recv()
    assert response == {'error': 'Unknown request: TOTO.'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_cannot_join(player1, player2, players):
    yield from player1.send('init_game')
    for i in range(1, get_number_players()):
        take_slot_message = {
            "rt": "SLOT_UPDATED",
            "slot": {
                "index": i,
                "state": "TAKEN",
            },
        }
        yield from player1.send('update_slot', message_override=take_slot_message)

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    response = yield from player2.recv()

    assert response == {'error_to_display': 'You cannot join this game. No slots opened.'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_only_game_master_can_create_game(player1, player2):
    yield from player1.send('init_game')
    yield from player1.send('update_slot2')

    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    yield from player2.send('create_game')
    response = yield from player2.recv()

    assert response == {'error_to_display': 'Only the game master can use CREATE_GAME request.'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_update_slot_no_solt(player1):
    yield from player1.send('init_game')

    yield from player1.send(message={'rt': 'SLOT_UPDATED'})
    response = yield from player1.recv()
    assert response == {'error_to_display': 'No slot provided.'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_not_your_turn(player1, player2):
    yield from create_game(player1, player2)
    yield from player2.send('pass_turn')

    response = yield from player2.recv()
    assert response == {'error_to_display': 'Not your turn.'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_view_squares_wrong_card(player1, player2):
    yield from create_game(player1, player2)

    response = yield from player1.recv()
    for card in response['hand']:
        play_request = {
            'card_name': card['name'],
            'card_color': card['color'],
        }
        yield from player1.send(
            'view_possible_squares',
            message_override={'play_request': play_request},
        )
        response = yield from player1.recv()
        if len(response['possible_squares']) > 0:
            break

    # Wrong card to play.
    # Wrong color
    new_square = response['possible_squares'][0]
    msg = {
        'play_request': {
            'card_name': card['name'],
            'card_color': 'wrong_color',
        },
    }
    yield from player1.send('view_possible_squares', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing color
    msg = {
        'card_name': card['name'],
        'x': new_square['x'],
        'y': new_square['y'],
    }
    yield from player1.send('view_possible_squares', message_override={'play_request': msg})

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Wrong name
    msg = {
        'play_request': {
            'card_name': 'wrong_name',
            'card_color': card['color'],
            'x': new_square['x'],
            'y': new_square['y'],
        },
    }
    yield from player1.send('view_possible_squares', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing name
    msg = {
        'play_request': {
            'card_color': card['color'],
            'x': new_square['x'],
            'y': new_square['y'],
        },
    }
    yield from player1.send('view_possible_squares', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_play_wrong_card(player1, player2):
    yield from create_game(player1, player2)

    response = yield from player1.recv()
    for card in response['hand']:
        play_request = {
            'card_name': card['name'],
            'card_color': card['color'],
        }
        yield from player1.send(
            'view_possible_squares',
            message_override={'play_request': play_request},
        )
        response = yield from player1.recv()
        if len(response['possible_squares']) > 0:
            break

    # Wrong color
    new_square = response['possible_squares'][0]
    msg = {
        'play_request': {
            'card_name': card['name'],
            'card_color': 'wrong_color',
            'x': new_square['x'],
            'y': new_square['y'],
        },
    }
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing color
    msg = {
        'play_request': {
            'card_name': card['name'],
            'x': new_square['x'],
            'y': new_square['y'],
        },
    }
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Wrong name
    msg = {
        'play_request': {
            'card_name': 'wrong_name',
            'card_color': card['color'],
            'x': new_square['x'],
            'y': new_square['y'],
        },
    }
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing name
    msg = {
        'play_request': {
            'card_color': card['color'],
            'x': new_square['x'],
            'y': new_square['y'],
        },
    }
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_play_wrong_square(player1, player2):
    yield from create_game(player1, player2)

    response = yield from player1.recv()
    for card in response['hand']:
        play_request = {
            'card_name': card['name'],
            'card_color': card['color'],
        }
        yield from player1.send(
            'view_possible_squares',
            message_override={'play_request': play_request})
        response = yield from player1.recv()
        if len(response['possible_squares']) > 0:
            break

    # Wrong x
    new_square = response['possible_squares'][0]
    msg = {
        'play_request': {
            'card_name': card['name'],
            'card_color': card['color'],
            'x': 5,
            'y': new_square['y'],
        },
    }
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {
        'error_to_display': 'This square doesn\'t exist or you cannot move there yet.',
    }

    # Wrong y
    msg = {
        'play_request': {
            'card_name': card['name'],
            'card_color': card['color'],
            'x': new_square['x'],
            'y': -1,
        },
    }
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {
        'error_to_display': 'This square doesn\'t exist or you cannot move there yet.',
    }

    # Missing x
    msg = {
        'play_request': {
            'card_name': card['name'],
            'card_color': card['color'],
            'y': new_square['y'],
        },
    }
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {
        'error_to_display': 'This square doesn\'t exist or you cannot move there yet.',
    }

    # Missing y
    msg = {
        'play_request': {
            'card_color': card['color'],
            'card_name': card['name'],
            'x': new_square['x'],
        },
    }
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {
        'error_to_display': 'This square doesn\'t exist or you cannot move there yet.',
    }

    # Wrong card and wrong coords
    # Missing y
    msg = {
        'play_request': {
            'card_color': card['color'],
            'card_name': 'wrong_name',
            'x': new_square['x'],
        },
    }
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {
        'error_to_display': 'This card doesn\'t exist or is not in your hand.',
    }


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_play_wrong_trump_without_target(player1, player2):
    yield from create_game(player1, player2)

    # Unknown
    play_request = {
        'name': 'TOTO',
    }
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request},
    )
    response = yield from player1.recv()
    assert response == {'error': 'Unknown trump.'}

    # Missing
    play_request = {}
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request},
    )
    response = yield from player1.recv()
    assert response == {'error': 'Unknown trump.'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_play_wrong_trump_with_target(player1, player2):
    yield from create_game(player1, player2)

    # Unknown
    play_request = {
        'name': 'TOTO',
    }
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request},
    )
    response = yield from player1.recv()
    assert response == {'error': 'Unknown trump.'}

    # Wrong index
    play_request = {
        'name': 'Tower Blue',
        'target_index': 78,
    }
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request})
    response = yield from player1.recv()
    assert response == {'error': 'Wrong target player index.'}

    # Missing index
    play_request = {
        'name': 'Tower Blue',
    }
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request},
    )
    response = yield from player1.recv()
    assert response == {'error': 'You must specify a target player.'}

    # Missing
    play_request = {
    }
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request},
    )
    response = yield from player1.recv()
    assert response == {'error': 'Unknown trump.'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_play_two_trumps_on_same_player(players):
    for _ in range(Player.MAX_NUMBER_AFFECTING_TRUMPS + 2):
        player = players.add()

    yield from create_game(*players)
    msg = {
        'play_request': {
            'target_index': len(players) - 1,
            'name': 'Tower Blue',
        },
    }

    for i in range(Player.MAX_NUMBER_AFFECTING_TRUMPS + 1):
        player = players[i]
        yield from player.send('play_trump_with_target', message_override=msg)
        if i == Player.MAX_NUMBER_AFFECTING_TRUMPS:
            break
        for p in players:
            response = yield from p.recv()
        yield from player.send('pass_turn')
        for p in players:
            yield from p.recv()
            yield from p.recv()

    response = yield from player.recv()
    assert response == {
        'error_to_display': 'trumps.max_number_trumps',
    }


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_play_two_trumps_in_same_turn(player1, player2):
    yield from create_game(player1, player2)
    yield from player1.send('play_trump_with_target')
    yield from player1.send('play_trump_with_target')

    response = yield from player1.recv()
    assert response == {'error_to_display': 'trumps.max_number_played_trumps'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_reconnect_wrong_game_id(player1, player2, players):
    yield from create_game(player1, player2)
    yield from player1.get_game_id()
    player_id = yield from player1.get_player_id()

    player1.close()
    players.add()
    new_player = players[-1]
    yield from new_player.connect()

    msg = {
        'game_id': 'toto',
        'player_id': player_id,
    }
    yield from new_player.send('join_game', message_override=msg)
    response = yield from new_player.recv()

    assert response == {'error_to_display': 'You cannot join this game. No slots opened.'}


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.timeout(5)
def test_reconnect_wrong_player_id(player1, player2, players):
    yield from create_game(player1, player2)
    game_id = yield from player1.get_game_id()
    yield from player1.get_player_id()

    player1.close()
    players.add()
    new_player = players[-1]
    yield from new_player.connect()

    msg = {
        'game_id': game_id,
        'player_id': 'toto',
    }
    yield from new_player.send('join_game', message_override=msg)
    response = yield from new_player.recv()

    assert response == {'error_to_display': 'You cannot join this game. No slots opened.'}
