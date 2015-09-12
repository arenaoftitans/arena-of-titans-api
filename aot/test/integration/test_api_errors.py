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