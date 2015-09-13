import logging
import pytest

from aot.test.integration import (
    flush_cache,
    create_game,
    player1,
    player2,
    players,
)


logging.basicConfig(level=logging.DEBUG)


@pytest.mark.asyncio
def test_no_enough_players(player1):
    yield from player1.send('init_game')
    yield from player1.send('create_game')
    response = yield from player1.recv()
    assert response == {
        'error': 'Number of registered players differs with number of players '
                            'descriptions.'
    }


@pytest.mark.asyncio
def test_too_many_players(player1, players):
    yield from player1.connect()
    yield from player1.send('init_game')
    msg = {
        'index': -1,
        'state': 'OPEN',
        'player_name': ''
    }
    for i in range(1, 8):
        msg['index'] = i
        yield from player1.send('add_slot', message_override={'slot': msg})
    # Max number of slots reach, try to add one
    msg['index'] = i + 1
    yield from player1.send('add_slot', message_override={'slot': msg})
    response = yield from player1.recv()
    assert response == {
        'error_to_display': 'Max number of slots reached. You cannot add more slots.'
    }

    game_id = yield from player1.get_game_id()

    # Number of registered players differs number of players descriptions
    msg = [{
        'name': 'P{}'.format(i),
        'index': i
    } for i in range(9)]
    yield from player1.send('create_game', message_override={'create_game_request': msg})
    response = yield from player1.recv()
    assert response == {
        'error': 'Number of registered players differs with number of players descriptions.'
    }


@pytest.mark.asyncio
def test_wrong_request(player1):
    yield from player1.send('init_game')
    yield from player1.send('create_game', message_override={'rt': 'TOTO'})
    response = yield from player1.recv()
    assert response == {'error': 'Unknown request.'}


@pytest.mark.asyncio
def test_cannot_join(player1, player2):
    yield from player1.send('init_game')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    response = yield from player2.recv()

    assert response == {'error_to_display': 'You cannot join this game. No slots opened.'}


@pytest.mark.asyncio
def test_only_game_master_can_create_game(player1, player2):
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    yield from player2.send('create_game')
    response = yield from player2.recv()

    assert response == {'error_to_display': 'Only the game master can use CREATE_GAME request.'}


@pytest.mark.asyncio
def test_only_game_master_add_slot(player1, player2):
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    slot = {
        "index": 2,
        "state": "CLOSED",
        "player_name": ""
    }
    yield from player2.send('add_slot', message_override={'slot': slot})
    response = yield from player2.recv()

    assert response == {'error_to_display': 'Only the game master can use ADD_SLOT request.'}


@pytest.mark.asyncio
def test_update_wrong_slot(player1):
    yield from player1.send('init_game')
    yield from player1.send('update_slot2')
    response = yield from player1.recv()

    assert response == {'error_to_display': 'Trying to update non existant slot.'}


@pytest.mark.asyncio
def test_add_existing_slot(player1):
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('add_slot')
    response = yield from player1.recv()

    assert response == {'error_to_display': 'Trying to add a slot that already exists.'}


@pytest.mark.asyncio
def test_not_your_turn(player1, player2):
    yield from create_game(player1, player2)
    yield from player2.send('pass_turn')

    response = yield from player2.recv()
    assert response == {'error_to_display': 'Not your turn.'}


@pytest.mark.asyncio
def test_view_squares_wrong_card(player1, player2):
    yield from create_game(player1, player2)

    response = yield from player1.recv()
    for card in response['hand']:
        play_request = {
            'card_name': card['name'],
            'card_color': card['color']
        }
        yield from player1.send(
            'view_possible_squares',
            message_override={'play_request': play_request})
        response = yield from player1.recv()
        if len(response['possible_squares']) > 0:
            break

    # Wrong card to play.
    # Wrong color
    new_square = response['possible_squares'][0]
    msg = {'play_request': {
        'card_name': card['name'],
        'card_color': 'wrong_color',
    }}
    yield from player1.send('view_possible_squares', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing color
    msg = {
        'card_name': card['name'],
        'x': new_square['x'],
        'y': new_square['y']
    }
    yield from player1.send('view_possible_squares', message_override={'play_request': msg})

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Wrong name
    msg = {'play_request': {
        'card_name': 'wrong_name',
        'card_color': card['color'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('view_possible_squares', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing name
    msg = {'play_request': {
        'card_color': card['color'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('view_possible_squares', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}


@pytest.mark.asyncio
def test_play_wrong_card(player1, player2):
    yield from create_game(player1, player2)

    response = yield from player1.recv()
    for card in response['hand']:
        play_request = {
            'card_name': card['name'],
            'card_color': card['color']
        }
        yield from player1.send(
            'view_possible_squares',
            message_override={'play_request': play_request})
        response = yield from player1.recv()
        if len(response['possible_squares']) > 0:
            break

    # Wrong color
    new_square = response['possible_squares'][0]
    msg = {'play_request': {
        'card_name': card['name'],
        'card_color': 'wrong_color',
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing color
    msg = {'play_request': {
        'card_name': card['name'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Wrong name
    msg = {'play_request': {
        'card_name': 'wrong_name',
        'card_color': card['color'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing name
    msg = {'play_request': {
        'card_color': card['color'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}


@pytest.mark.asyncio
def test_play_wrong_square(player1, player2):
    yield from create_game(player1, player2)

    response = yield from player1.recv()
    for card in response['hand']:
        play_request = {
            'card_name': card['name'],
            'card_color': card['color']
        }
        yield from player1.send(
            'view_possible_squares',
            message_override={'play_request': play_request})
        response = yield from player1.recv()
        if len(response['possible_squares']) > 0:
            break

    # Wrong x
    new_square = response['possible_squares'][0]
    msg = {'play_request': {
        'card_name': card['name'],
        'card_color': card['color'],
        'x': 5,
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {
        'error_to_display': 'This square doesn\'t exist or you cannot move there yet.'
    }

    # Wrong y
    msg = {'play_request': {
        'card_name': card['name'],
        'card_color': card['color'],
        'x': new_square['x'],
        'y': -1
    }}
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {
        'error_to_display': 'This square doesn\'t exist or you cannot move there yet.'
    }

    # Missing x
    msg = {'play_request': {
        'card_name': card['name'],
        'card_color': card['color'],
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {
        'error_to_display': 'This square doesn\'t exist or you cannot move there yet.'
    }

    # Missing y
    msg = {'play_request': {
        'card_color': card['color'],
        'card_name': card['name'],
        'x': new_square['x'],
    }}
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {
        'error_to_display': 'This square doesn\'t exist or you cannot move there yet.'
    }

    # Wrong card and wrong coords
    # Missing y
    msg = {'play_request': {
        'card_color': card['color'],
        'card_name': 'wrong_name',
        'x': new_square['x'],
    }}
    yield from player1.send('play_card', message_override=msg)

    response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}


@pytest.mark.asyncio
def test_play_wrong_trump_without_target(player1, player2):
    yield from create_game(player1, player2)

    # Unknown
    play_request = {
        'name': 'TOTO'
    }
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request})
    response = yield from player1.recv()
    assert response == {'error_to_display': 'Unknown trump.'}

    # Missing
    play_request = {
    }
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request})
    response = yield from player1.recv()
    assert response == {'error_to_display': 'Unknown trump.'}


@pytest.mark.asyncio
def test_play_wrong_trump_with_target(player1, player2):
    yield from create_game(player1, player2)

    # Unknown
    play_request = {
        'name': 'TOTO'
    }
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request})
    response = yield from player1.recv()
    assert response == {'error_to_display': 'Unknown trump.'}

    # Wrong index
    play_request = {
        'name': 'Tower Black',
        'target_index': 78
    }
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request})
    response = yield from player1.recv()
    assert response == {'error_to_display': 'Wrong target player index.'}

    # Missing index
    play_request = {
        'name': 'Tower Black'
    }
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request})
    response = yield from player1.recv()
    assert response == {'error': 'You must specify a target player.'}

    # Missing
    play_request = {
    }
    yield from player1.send(
        'play_trump_with_target',
        message_override={'play_request': play_request})
    response = yield from player1.recv()
    assert response == {'error_to_display': 'Unknown trump.'}
