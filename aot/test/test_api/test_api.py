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

import pytest

from aot import get_game
from aot.api.api import (
    AotError,
    AotErrorToDisplay,
)
from aot.api.utils import RequestTypes
from aot.test import (
    api,
    game,
)
from unittest.mock import MagicMock


def test_new_game_no_game_id(api):
    api._game_id = None
    assert api._creating_new_game


def test_new_game_with_game_id(api):
    api._game_id = 'game_id'
    assert not api._creating_new_game


def test_new_game_request_on_old_connection(api):
    api._game_id = 'game_id'
    api._rt = 'INIT_GAME'
    api._message = {}
    assert api._creating_new_game


def test_onMessage_unkwon_request_type(api):
    api._send_error = MagicMock()

    try:
        api.onMessage(b'{}', False)
    except AotError as e:
        assert str(e) == 'unknown_request'
        api._send_error.assert_called_once_with('ttt')


def test_onMessage_new_game(api):
    api._game_id = None
    api._create_new_game = MagicMock()
    api.sendMessage = MagicMock()

    api.onMessage(b'{"rt": "INIT_GAME"}', False)

    api._create_new_game.assert_called_once_with()


def test_onMessage_creating_game(api):
    api._process_create_game_request = MagicMock()
    api._cache = MagicMock()
    api._cache.has_game_started = MagicMock(return_value=False)
    api._game_id = 'game_id'
    api.sendMessage = MagicMock()

    api.onMessage(b'{"rt": "INIT_GAME", "game_id": "game_id"}', False)

    api._process_create_game_request.assert_called_once_with()


def test_onMessage_process_play_request(api):
    api._process_play_request = MagicMock()
    api._cache = MagicMock()
    api._cache.has_game_started = MagicMock(return_value=True)
    api._game_id = 'game_id'

    api.onMessage(b'{"rt": "VIEW_POSSIBLE_SQUARES", "game_id": "game_id"}', False)

    api._process_play_request.assert_called_once_with()


def test_create_new_game(api, mock):
    api_cache = MagicMock()
    mock.patch('aot.api.api.ApiCache', return_value=api_cache)
    api._get_initialiazed_game_message = MagicMock()
    api_cache.affect_next_slot = MagicMock(return_value=api.INDEX_FIRST_PLAYER)
    api._message = {
        'player_name': 'Game Master',
        'hero': 'daemon',
    }
    api.sendMessage = MagicMock()

    api._create_new_game()

    assert isinstance(api._game_id, str)
    assert len(api._game_id) == 22
    api_cache.create_new_game.assert_called_once_with(test=False)
    api_cache.affect_next_slot.assert_called_once_with(
        api._message['player_name'],
        api._message['hero'],
    )
    api_cache.save_session.assert_called_once_with(api.INDEX_FIRST_PLAYER)
    api._get_initialiazed_game_message.assert_called_once_with(api.INDEX_FIRST_PLAYER)
    assert api.sendMessage.call_count == 1


def test_process_create_game_request_not_allowed(api):
    api._cache = MagicMock()
    api._cache.is_game_master = MagicMock(return_value=False)
    api._rt = RequestTypes.CREATE_GAME

    try:
        api._process_create_game_request()
        raise AssertionError
    except AotErrorToDisplay as e:
        assert str(e) == 'game_master_request'


def test_process_create_game_request_update_slot_not_game_master(api):
    api._cache = MagicMock()
    api._cache.is_game_master = MagicMock(return_value=False)
    api._rt = RequestTypes.SLOT_UPDATED
    api._modify_slots = MagicMock()

    api._process_create_game_request()

    api._modify_slots.assert_called_once_with()


def test_process_create_game_request_update_slot_game_master(api):
    api._cache = MagicMock()
    api._cache.is_game_master = MagicMock(return_value=True)
    api._rt = RequestTypes.SLOT_UPDATED
    api._modify_slots = MagicMock()

    api._process_create_game_request()

    api._modify_slots.assert_called_once_with()


def test_process_create_game_request_create_game(api):
    api._cache = MagicMock()
    api._cache.is_game_master = MagicMock(return_value=True)
    api._rt = RequestTypes.CREATE_GAME
    api._create_game = MagicMock()

    api._process_create_game_request()

    api._create_game.assert_called_once_with()


def test_modify_slots_empty_request(api):
    api._message = {}

    try:
        api._modify_slots()
        raise AssertionError
    except AotErrorToDisplay as e:
        assert str(e) == 'no_slot'


def test_modify_slots_inexistant_slot(api):
    api._message = {
        'slot': {},
    }
    api._cache = MagicMock()
    api._cache.slot_exists = MagicMock(return_value=False)

    try:
        api._modify_slots()
        raise AssertionError
    except AotError as e:
        assert str(e) == 'inexistant_slot'


def test_modify_slots(api):
    api._send_all = MagicMock()
    api._cache = MagicMock()
    api._cache.slot_exists = MagicMock(return_value=True)
    slot = {
        'player_id': 'player_id',
    }
    api._message = {
        'slot': slot,
    }

    api._modify_slots()

    api._cache.update_slot.assert_called_once_with(slot)
    assert api._send_all.call_count == 1


def test_create_game_no_create_game_request(api):
    api._cache = MagicMock()
    api._cache.number_taken_slots = MagicMock(return_value=2)
    api._message = {
    }

    try:
        api._create_game()
        raise AssertionError
    except AotError as e:
        assert str(e) == 'no_request'


def test_create_game_too_many_players(api):
    api._cache = MagicMock()
    api._cache.number_taken_slots = MagicMock(return_value=9)
    api._message = {
        'create_game_request': [{'name': i} for i in range(9)],
    }

    try:
        api._create_game()
        raise AssertionError
    except AotError as e:
        assert str(e) == 'registered_different_description'


def test_create_game_too_few_players(api):
    api._cache = MagicMock()
    api._cache.number_taken_slots = MagicMock(return_value=1)
    api._message = {
        'create_game_request': [{'name': 0}],
    }

    try:
        api._create_game()
        raise AssertionError
    except AotError as e:
        assert str(e) == 'registered_different_description'


def test_create_game_wrong_registration(api):
    api._cache = MagicMock()
    api._cache.number_taken_slots = MagicMock(return_value=2)
    api._message = {
        'create_game_request': [],
    }

    try:
        api._create_game()
        raise AssertionError
    except AotError as e:
        assert str(e) == 'registered_different_description'


def test_create_game(mock, api):
    create_game_request = [{
            'name': str(i),
            'index': i,
            'id': str(i),
        } for i in range(2)
    ]
    game = get_game(create_game_request)
    mock.patch('aot.api.api.get_game', return_value=game)
    api._cache = MagicMock()
    api._send_to = MagicMock()
    api._send_game_created_message = MagicMock()
    api._cache.number_taken_slots = MagicMock(return_value=2)
    api._message = {
        'create_game_request': create_game_request,
    }

    api._create_game()

    api._cache.save_game.assert_called_once_with(game)
    api._send_game_created_message.assert_called_once_with(game)
    api._send_to.call_count == 2


def test_process_play_request_not_your_turn(api, game):
    api._cache = MagicMock()
    api._cache.get_game = MagicMock(return_value=game)
    api.id = 'wrong_id'

    try:
        api._process_play_request()
        raise AssertionError
    except AotErrorToDisplay as e:
        assert str(e) == 'not_your_turn'


def test_process_play_request_your_turn(api, game):
    api._cache = MagicMock()
    api._cache.get_game = MagicMock(return_value=game)
    api.id = game.active_player.id
    api._play_game = MagicMock()

    api._process_play_request()

    api._play_game.assert_called_once_with(game)


def test_play_game_no_request(api, game):
    api._message = {}

    try:
        api._play_game(game)
        raise AssertionError
    except AotError as e:
        assert str(e) == 'no_request'


def test_play_game_unknown_request(api, game):
    api._message = {
        'play_request': {},
        'rt': 'TOTO',
    }

    try:
        api._play_game(game)
        raise AssertionError
    except AotError as e:
        assert str(e) == 'unknown_request'


def test_play_game(api, game):
    requests_to_test = ['VIEW_POSSIBLE_SQUARES', 'PLAY', 'PLAY_TRUMP']
    for request in requests_to_test:
        setattr(api, '_' + request.lower(), MagicMock())

    for request in requests_to_test:
        api._message = {
            'play_request': request,
        }
        api._rt = request
        api._play_game(game)

    for request in requests_to_test:
        mm = getattr(api, '_' + request.lower())
        mm.assert_called_once_with(game, request)


def test_view_possible_squares_wrong_card(api, game):
    try:
        api._view_possible_squares(game, {})
        raise AssertionError
    except AotErrorToDisplay as e:
        assert str(e) == 'wrong_card'


def test_view_possible_squares(api, game):
    api.sendMessage = MagicMock()
    card = game.active_player.hand[0]

    api._view_possible_squares(game, {
        'card_name': card.name,
        'card_color': card.color,
    })

    assert api.sendMessage.call_count == 1


def test_play_pass(api, game):
    game.pass_turn = MagicMock()
    api._send_play_message = MagicMock()

    api._play(game, {'pass': True})

    game.pass_turn.assert_called_once_with()
    api._send_play_message.assert_called_once_with(game, game.active_player)


def test_play_discard_wrong_card(api, game):
    game.discard = MagicMock()

    try:
        api._play(game, {'discard': True})
        raise AssertionError
    except AotErrorToDisplay as e:
        assert str(e) == 'wrong_card'
        assert game.discard.call_count == 0


def test_play_discard(api, game):
    game.discard = MagicMock()
    api._send_play_message = MagicMock()
    card = game.active_player.hand[0]

    api._play(game, {
        'discard': True,
        'card_name': card.name,
        'card_color': card.color,
    })

    game.discard.assert_called_once_with(card)
    api._send_play_message.assert_called_once_with(game, game.active_player)


def test_play_wrong_card(api, game):
    game.play_card = MagicMock()
    api._send_play_message = MagicMock()

    try:
        api._play(game, {})
        raise AssertionError
    except AotErrorToDisplay as e:
        assert str(e) == 'wrong_card'
        assert game.play_card.call_count == 0


def test_play_wrong_square(api, game):
    game.play_card = MagicMock()
    api._send_play_message = MagicMock()
    card = game.active_player.hand[0]

    try:
        api._play(game, {
            'card_name': card.name,
            'card_color': card.color,
        })
        raise AssertionError
    except AotErrorToDisplay as e:
        assert str(e) == 'wrong_square'
        assert game.play_card.call_count == 0


def test_play_card(api, game):
    card = game.active_player.hand[0]
    square = game.get_square(0, 0)
    game.play_card = MagicMock()
    game.get_square = MagicMock(return_value=square)
    game.can_move = MagicMock(return_value=True)
    api._send_play_message = MagicMock()

    api._play(game, {
        'card_name': card.name,
        'card_color': card.color,
        'x': 0,
        'y': 0,
    })

    game.play_card.assert_called_once_with(card, square)
    api._send_play_message.assert_called_once_with(game, game.active_player)
