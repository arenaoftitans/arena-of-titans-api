import logging
import pytest

from aot.test.integration import (
    create_game,
    flush_cache,
    player1,
    player2,
    players,
)
from aot.api.api_cache import ApiCache


logging.basicConfig(level=logging.DEBUG)


@pytest.mark.asyncio
def test_game_init(player1):
    yield from player1.send('init_game')

    response, expected_response = yield from player1.recv('init_game')
    expected_response['game_id'] = yield from player1.get_game_id()
    expected_response['player_id'] = yield from player1.get_player_id()

    assert response == expected_response


@pytest.mark.asyncio
def test_add_slot(player1):
    yield from player1.send('init_game')
    yield from player1.send('add_slot')

    response, expected_response = yield from player1.recv('add_slot')

    assert response == expected_response


@pytest.mark.asyncio
def test_update_slot(player1):
    # Update his/her slot
    yield from player1.send('init_game')
    yield from player1.send('update_slot')

    response, expected_response = yield from player1.recv('update_slot')
    assert response == expected_response

    # Check object in db. Player 1 took the slot, so it must have its id
    game_id = yield from player1.get_game_id()
    saved_slot0 = ApiCache.get_slot_from_game_id(0, game_id)
    assert 'player_id' in saved_slot0
    assert len(saved_slot0['player_id']) > 0

    # Player id never appears during communications, so we must delete it
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
    assert saved_slot0 == ApiCache.get_slot_from_game_id(0, game_id)
    saved_slot1 = ApiCache.get_slot_from_game_id(1, game_id)
    assert 'player_id' not in saved_slot1
    assert saved_slot1 == response['slot']


@pytest.mark.asyncio
def test_player2_join(player1, player2):
    yield from player1.send('init_game')
    yield from player1.send('add_slot')
    yield from player1.send('update_slot2')

    game_id = yield from player1.get_game_id()
    yield from player2.send('join_game', message_override={'game_id': game_id})
    response, expected_response = yield from player2.recv('join_game')

    # Correct expected_response
    expected_response['game_id'] = game_id
    expected_response['player_id'] = yield from player2.get_player_id()

    # Check in db
    slot1 = ApiCache.get_slot_from_game_id(1, game_id)
    del slot1['player_id']
    assert slot1 == expected_response['slots'][1]

    assert response == expected_response

    response, expected_response = yield from player1.recv('join_game_other_players')
    assert response == expected_response


@pytest.mark.asyncio
def test_create_game(player1, player2):
    yield from create_game(player1, player2)

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


@pytest.mark.asyncio
def test_pass_turn(player1, player2):
    yield from create_game(player1, player2)

    yield from player1.send('pass_turn')
    # Player moved answer
    yield from player1.recv()
    response, expected_response = yield from player1.recv('play_card')
    expected_response['next_player'] = 1
    del expected_response['hand']
    assert len(response['hand']) == 5
    del response['hand']
    assert response == expected_response

    # Player moved answer
    yield from player2.recv()
    response, expected_response = yield from player2.recv('play_card')
    expected_response['next_player'] = 1
    expected_response['your_turn'] = True
    del expected_response['hand']
    assert len(response['hand']) == 5
    del response['hand']
    assert response == expected_response


@pytest.mark.asyncio
def test_discard_card(player1, player2):
    yield from create_game(player1, player2)
    response = yield from player1.recv()

    first_card = response['hand'][0]
    play_request = {
        'card_name': first_card['name'],
        'card_color': first_card['color'],
        'discard': True
    }
    yield from player1.send('discard_card', message_override={'play_request': play_request})
    # Player moved answer
    yield from player1.recv()
    response, expected_response = yield from player1.recv('play_card')
    expected_response['next_player'] = 0
    expected_response['your_turn'] = True
    del expected_response['hand']
    assert len(response['hand']) == 4
    del response['hand']
    assert response == expected_response


@pytest.mark.asyncio
def test_view_squares(player1, player2):
    yield from create_game(player1, player2)
    response = yield from player1.recv()

    first_card = response['hand'][0]
    play_request = {
        'card_name': first_card['name'],
        'card_color': first_card['color']
    }
    yield from player1.send(
        'view_possible_squares',
        message_override={'play_request': play_request})
    response, expected_response = yield from player1.recv('view_possible_squares')

    assert response['rt'] == expected_response['rt']
    assert isinstance(response['possible_squares'], list)


@pytest.mark.asyncio
def test_play_card(player1, player2):
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

    new_square = response['possible_squares'][0]
    play_request = {
        'card_name': card['name'],
        'card_color': card['color'],
        'x': new_square['x'],
        'y': new_square['y']
    }
    yield from player1.send('play_card', message_override={'play_request': play_request})

    response, player_moved_expected_response = yield from player1.recv('player_played')
    player_moved_expected_response['new_square'] = {
        'x': new_square['x'],
        'y': new_square['y']
    }
    # last_action will always differs
    assert 'last_action' in response
    assert 'description' in response['last_action']
    assert 'card' in response['last_action']
    assert 'color' in response['last_action']['card']
    assert 'name' in response['last_action']['card']
    assert 'description' in response['last_action']['card']
    del response['last_action']
    del player_moved_expected_response['last_action']

    assert response == player_moved_expected_response

    response, expected_response = yield from player1.recv('play_card')
    expected_response['your_turn'] = True
    del expected_response['hand']
    assert len(response['hand']) == 4
    del response['hand']
    assert response == expected_response

    response = yield from player2.recv()
    # last_action will always differs
    assert 'last_action' in response
    assert 'description' in response['last_action']
    assert 'card' in response['last_action']
    assert 'color' in response['last_action']['card']
    assert 'name' in response['last_action']['card']
    assert 'description' in response['last_action']['card']
    del response['last_action']

    assert response == player_moved_expected_response


@pytest.mark.asyncio
def test_play_trump_no_target(player1, player2):
    yield from create_game(player1, player2)
    yield from player1.send('play_trump_no_target')

    response, expected_response = yield from player1.recv('play_trump_no_target')
    assert response['rt'] == 'PLAY_TRUMP'
    assert response['active_trumps'] == expected_response['active_trumps']

    response, expected_response = yield from player2.recv('play_trump_no_target')
    assert response['rt'] == 'PLAY_TRUMP'
    assert response['active_trumps'] == expected_response['active_trumps']


@pytest.mark.asyncio
def test_play_trump_with_target(player1, player2):
    yield from create_game(player1, player2)
    yield from player1.send('play_trump_with_target')

    response, expected_response = yield from player1.recv('play_trump_with_target')
    assert response['rt'] == 'PLAY_TRUMP'
    assert response['active_trumps'] == expected_response['active_trumps']

    response, expected_response = yield from player2.recv('play_trump_with_target')
    assert response['rt'] == 'PLAY_TRUMP'
    assert response['active_trumps'] == expected_response['active_trumps']


@pytest.mark.asyncio
def test_reconnect(player1, player2, players):
    yield from create_game(player1, player2)
    game_id = yield from player1.get_game_id()
    player_id = yield from player1.get_player_id()

    player1.close()
    players.add()
    new_player = players[-1]
    yield from new_player.connect()

    msg = {
        'game_id': game_id,
        'player_id': player_id
    }
    yield from new_player.send('join_game', message_override=msg)
    response, expected_response = yield from new_player.recv('play_card')

    # Correct expected response
    expected_response['your_turn'] = True
    del expected_response['hand']
    expected_response['reconnect'] = {
        'players': [
            {'index': 0, 'name': 'Player 1', 'square': {'y': 8, 'x': 0}},
            {'index': 1, 'name': 'Player 2', 'square': {'y': 8, 'x': 4}}
        ]
    }

    assert len(response['hand']) == 5
    del response['hand']
    assert len(response['reconnect']['trumps']) == 5
    del response['reconnect']['trumps']
    assert response == expected_response


@pytest.mark.asyncio
def test_reconnect_game_creation(player1, player2, players):
    yield from player1.send('init_game')
    game_id = yield from player1.get_game_id()
    player_id = yield from player1.get_player_id()

    player1.close()
    players.add()
    new_player = players[-1]
    yield from new_player.connect()

    msg = {
        'game_id': game_id,
        'player_id': player_id
    }
    yield from new_player.send('join_game', message_override=msg)
    response, expected_response = yield from new_player.recv('join_game')

    # Correct expected response
    expected_response['game_id'] = game_id
    expected_response['player_id'] = player_id
    expected_response['is_game_master'] = True
    expected_response['index'] = 0
    del expected_response['slots'][1]

    assert response == expected_response
