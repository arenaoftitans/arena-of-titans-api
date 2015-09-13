import asyncio
import logging
import pytest
import redis

import aot
from aot.api.api_cache import ApiCache
from aot.test.integration import PlayerWs


logging.basicConfig(level=logging.DEBUG)


@pytest.yield_fixture(autouse=True)
def flush_cache():
    cache = redis.Redis(host=aot.config['cache']['server_host'], port=aot.config['cache']['server_port'])
    flush(cache)
    yield
    flush(cache)


def flush(cache):
    cache.execute_command('FLUSHALL')


@pytest.fixture
def player1():
    player = PlayerWs(1)
    return player


@pytest.fixture
def player2():
    player = PlayerWs(2)
    return player


@pytest.fixture
def cache():
    return ApiCache()


@pytest.mark.asyncio
def test_game_init(player1):
    yield from asyncio.wait([player1.connect()])
    yield from player1.send('init_game')
    response, expected_response = yield from player1.recv('init_game')
    expected_response['game_id'] = yield from player1.get_game_id()
    assert response == expected_response
    yield from asyncio.wait([player1.close()])


@pytest.mark.asyncio
def test_add_slot(player1):
    yield from asyncio.wait([player1.connect()])
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    response, expected_response = yield from player1.recv('add_slot')
    assert response == expected_response
    yield from asyncio.wait([player1.close()])


@pytest.mark.asyncio
def test_update_slot(player1, cache):
    # Update his/her slot
    yield from asyncio.wait([player1.connect()])
    yield from player1.send('init_game')
    yield from player1.send('update_slot')
    response, expected_response = yield from player1.recv('update_slot')
    assert response == expected_response
    # Check object in db. Player 1 took the slot, so it must have its id
    game_id = yield from player1.get_game_id()
    saved_slot0 = cache.get_slot(game_id, 0)
    assert 'player_id' in saved_slot0
    assert len(saved_slot0['player_id']) > 0
    # Player id never appears during communications
    player1_id = saved_slot0['player_id']
    del saved_slot0['player_id']
    assert saved_slot0 == response['slot']

    # Update status second slot which has no player_id
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')
    response, expected_response = yield from player1.recv('update_slot2')
    assert response == expected_response
    # Check in db
    saved_slot0['player_id'] = player1_id
    assert saved_slot0 == cache.get_slot(game_id, 0)
    saved_slot1 = cache.get_slot(game_id, 1)
    assert 'player_id' not in saved_slot1
    assert saved_slot1 == response['slot']
    yield from asyncio.wait([player1.close()])


@pytest.mark.asyncio
def test_player2_join(player1, player2, cache):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    response, expected_response = yield from player2.recv('join_game')

    # Correct expected_response
    expected_response['game_id'] = game_id

    # Check in db
    slot1 = cache.get_slot(game_id, 1)
    del slot1['player_id']
    assert slot1 == expected_response['slots'][1]

    assert response == expected_response

    # Check player 1 received update slot
    player1.recieve_index += 1
    response, expected_response = yield from player1.recv('join_game_other_players')
    assert response == expected_response

    yield from asyncio.wait([player1.close(), player2.close()])


@pytest.mark.asyncio
def test_create_game(player1, player2):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})

    yield from player1.send('create_game')
    player1.recieve_index += 1
    player2.recieve_index += 1

    response, expected_response = yield from player1.recv('create_game')
    hand_response = response['hand']
    pseudo_hand = expected_response['hand']
    trumps_response = response['trumps']
    pseudo_trumps = expected_response['trumps']
    del response['hand']
    del expected_response['hand']
    del response['trumps']
    del expected_response['trumps']
    assert response == expected_response
    assert len(hand_response) == 5
    assert len(trumps_response) == 5
    hand_element_keys = pseudo_hand[0].keys()
    for card in hand_response:
        assert card.keys() == hand_element_keys
    trump_element_keys = pseudo_trumps[0].keys()
    for trump in trumps_response:
        assert trump.keys() == trump_element_keys

    response, expected_response = yield from player2.recv('create_game')
    expected_response['your_turn'] = False
    hand_response = response['hand']
    trumps_response = response['trumps']
    del response['hand']
    del expected_response['hand']
    del response['trumps']
    del expected_response['trumps']
    assert response == expected_response
    for card in hand_response:
        assert card.keys() == hand_element_keys
    for trump in trumps_response:
        assert trump.keys() == trump_element_keys

    yield from asyncio.wait([player1.close(), player2.close()])


@pytest.mark.asyncio
def test_pass_turn(player1, player2):
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
    player2.recieve_index += 2

    yield from player1.send('pass_turn')
    #yield from asyncio.sleep(3)
    response, expected_response = yield from player1.recv('play_card')
    expected_response['next_player'] = 1
    del expected_response['hand']
    assert len(response['hand']) == 5
    del response['hand']
    assert response == expected_response

    response, expected_response = yield from player2.recv('play_card')
    expected_response['next_player'] = 1
    expected_response['your_turn'] = True
    expected_response['new_square'] = {
        'x': 4,
        'y': 8
    }
    del expected_response['hand']
    assert len(response['hand']) == 5
    del response['hand']
    assert response == expected_response

    yield from asyncio.wait([player1.close(), player2.close()])


@pytest.mark.asyncio
def test_discard_card(player1, player2):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    player1.recieve_index += 1

    yield from player1.send('create_game')
    response, expected_response = yield from player1.recv()
    player2.recieve_index += 2

    first_card = response['hand'][0]
    yield from player1.send('discard_card', message_override={'play_request': {'card_name': first_card['name'], 'card_color': first_card['color'], 'discard': True}})
    response, expected_response = yield from player1.recv('play_card')
    expected_response['next_player'] = 0
    expected_response['your_turn'] = True
    del expected_response['hand']
    assert len(response['hand']) == 4
    del response['hand']
    assert response == expected_response

    yield from asyncio.wait([player1.close(), player2.close()])


@pytest.mark.asyncio
def test_view_squares(player1, player2):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    player1.recieve_index += 1

    yield from player1.send('create_game')
    response, expected_response = yield from player1.recv()
    first_card = response['hand'][0]
    yield from player1.send('view_possible_squares', message_override={'play_request': {'card_name': first_card['name'], 'card_color': first_card['color']}})
    response, expected_response = yield from player1.recv('view_possible_squares')
    assert response['rt'] == expected_response['rt']
    assert isinstance(response['possible_squares'], list)

    yield from asyncio.wait([player1.close(), player2.close()])


@pytest.mark.asyncio
def test_play_card(player1, player2):
    yield from player1.connect()
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    yield from player2.connect()
    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    player1.recieve_index += 1

    yield from player1.send('create_game')
    response, expected_response = yield from player1.recv()
    for card in response['hand']:
        yield from player1.send('view_possible_squares', message_override={'play_request': {'card_name': card['name'], 'card_color': card['color']}})
        response, expected_response = yield from player1.recv()
        if len(response['possible_squares']) > 0:
            break

    new_square = response['possible_squares'][0]
    msg = {'play_request': {
        'card_name': card['name'],
        'card_color': card['color'],
        'x': new_square['x'],
        'y': new_square['y']
    }}
    yield from player1.send('play_card', message_override=msg)
    response, expected_response = yield from player1.recv('play_card')
    expected_response['your_turn'] = True
    expected_response['new_square'] = {
        'x': new_square['x'],
        'y': new_square['y']
    }
    del expected_response['hand']
    assert len(response['hand']) == 4
    del response['hand']
    assert response == expected_response

    yield from asyncio.wait([player1.close(), player2.close()])