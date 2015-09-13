import asyncio
import logging
import pytest

from aot.test.integration.test_api import player1, player2


logging.basicConfig(level=logging.DEBUG)


@pytest.mark.asyncio
def test_no_enough_players(player1):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('create_game')
    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'Not enough player to create game. 2 Players are at least required to start a game.'}

    yield from player1.close()


@pytest.mark.asyncio
def test_wrong_request(player1):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('create_game', message_override={'rt': 'TOTO'})
    response, expected_response = yield from player1.recv()
    assert response == {'error': 'Unknown request.'}

    yield from player1.close()


@pytest.mark.asyncio
def test_cannot_join(player1, player2):
    yield from player1.connect()
    yield from player1.send('init_game')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    response, expected_response = yield from player2.recv()

    assert response == {'error_to_display': 'You cannot join this game. No slots opened.'}

    yield from asyncio.wait([player1.close(), player2.close()])


@pytest.mark.asyncio
def test_only_game_master_can_create_game(player1, player2):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    yield from player2.send('create_game')
    response, expected_response = yield from player2.recv()

    assert response == {'error_to_display': 'Only the game master can create the game.'}

    yield from asyncio.wait([player1.close(), player2.close()])


@pytest.mark.asyncio
def test_not_your_turn(player1, player2):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    yield from player1.send('create_game')
    player2.recieve_index += 1
    yield from player2.send('pass_turn')
    response, expected_response = yield from player2.recv()

    assert response == {'error_to_display': 'Not your turn.'}

    yield from asyncio.wait([player1.close(), player2.close()])


@pytest.mark.asyncio
def test_view_squares_wrong_card(player1, player2):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    yield from player1.send('create_game')
    player1.recieve_index += 1

    response, expected_response = yield from player1.recv()
    for card in response['hand']:
        yield from player1.send('view_possible_squares', message_override={'play_request': {'card_name': card['name'], 'card_color': card['color']}})
        response, expected_response = yield from player1.recv()
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

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing color
    msg = {'play_request': {
        'card_name': card['name'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('view_possible_squares', message_override=msg)

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Wrong name
    msg = {'play_request': {
        'card_name': 'wrong_name',
        'card_color': card['color'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('view_possible_squares', message_override=msg)

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing name
    msg = {'play_request': {
        'card_color': card['color'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('view_possible_squares', message_override=msg)

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    yield from asyncio.wait([player1.close(), player2.close()])


@pytest.mark.asyncio
def test_play_wrong_card(player1, player2):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    yield from player1.send('create_game')
    player1.recieve_index += 1

    response, expected_response = yield from player1.recv()
    for card in response['hand']:
        yield from player1.send('view_possible_squares', message_override={'play_request': {'card_name': card['name'], 'card_color': card['color']}})
        response, expected_response = yield from player1.recv()
        if len(response['possible_squares']) > 0:
            break

    # Wrong card to play.
    # Wrong color
    new_square = response['possible_squares'][0]
    msg = {'play_request': {
        'card_name': card['name'],
        'card_color': 'wrong_color',
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing color
    msg = {'play_request': {
        'card_name': card['name'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Wrong name
    msg = {'play_request': {
        'card_name': 'wrong_name',
        'card_color': card['color'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    # Missing name
    msg = {'play_request': {
        'card_color': card['color'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    yield from asyncio.wait([player1.close(), player2.close()])


@pytest.mark.asyncio
def test_play_wrong_square(player1, player2):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    yield from player1.send('create_game')
    player1.recieve_index += 1

    response, expected_response = yield from player1.recv()
    for card in response['hand']:
        yield from player1.send('view_possible_squares', message_override={'play_request': {'card_name': card['name'], 'card_color': card['color']}})
        response, expected_response = yield from player1.recv()
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

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This square doesn\'t exist or you cannot move there yet.'}

    # Wrong y
    msg = {'play_request': {
        'card_name': card['name'],
        'card_color': card['color'],
        'x': new_square['x'],
        'y': -1
    }}
    yield from player1.send('play_card', message_override=msg)

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This square doesn\'t exist or you cannot move there yet.'}

    # Missing x
    msg = {'play_request': {
        'card_name': card['name'],
        'card_color': card['color'],
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This square doesn\'t exist or you cannot move there yet.'}

    # Missing y
    msg = {'play_request': {
        'card_color': card['color'],
        'card_name': card['name'],
        'x': new_square['x'],
    }}
    yield from player1.send('play_card', message_override=msg)

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This square doesn\'t exist or you cannot move there yet.'}

    # Wrong card and wrong coords
    # Missing y
    msg = {'play_request': {
        'card_color': card['color'],
        'card_name': 'wrong_name',
        'x': new_square['x'],
    }}
    yield from player1.send('play_card', message_override=msg)

    response, expected_response = yield from player1.recv()
    assert response == {'error_to_display': 'This card doesn\'t exist or is not in your hand.'}

    yield from asyncio.wait([player1.close(), player2.close()])
