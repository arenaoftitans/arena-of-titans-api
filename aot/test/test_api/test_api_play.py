################################################################################
# Copyright (C) 2016 by Arena of Titans Contributors.
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

from aot.api.utils import (
    AotError,
    AotErrorToDisplay,
)
from aot.api.utils import RequestTypes
from aot.test import (
    api,
    game,
)
from unittest.mock import MagicMock


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
    api._cache.save_game.assert_called_once_with(game)


def test_process_play_request_ai_after_player(api, game):
    game.active_player._is_ai = True
    api._cache = MagicMock()
    api._cache.get_game = MagicMock(return_value=game)
    api._is_player_id_correct = MagicMock(return_value=True)
    api._play_game = MagicMock()
    api._play_ai = MagicMock()
    api._loop = MagicMock()

    api._process_play_request()

    api._play_game.assert_called_once_with(game)
    assert api._play_ai.call_count == 0
    api._loop.call_later.assert_called_once_with(api.AI_TIMEOUT, api._process_play_request)


def test_process_play_request_ai_after_ai(api, game):
    api._cache = MagicMock()
    api._cache.get_game = MagicMock(return_value=game)
    api._is_player_id_correct = MagicMock(return_value=False)
    api._play_game = MagicMock()
    api._play_ai = MagicMock()
    game.active_player._is_ai = True

    api._process_play_request()

    assert api._play_game.call_count == 0
    api._play_ai.assert_called_once_with(game)


def test_play_ai(api, game):
    api._cache = MagicMock()
    api._loop = MagicMock()
    api._send_play_message = MagicMock()
    api._send_debug = MagicMock()
    game.active_player._is_ai = True
    game.play_auto = MagicMock()

    api._play_ai(game)

    game.play_auto.assert_called_once_with()
    api._send_play_message.assert_called_once_with(game, game.active_player)
    api._loop.call_later.assert_called_once_with(api.AI_TIMEOUT, api._process_play_request)
    assert api._send_debug.call_count == 0


def test_play_ai_mode_debug(api, game):
    api._cache = MagicMock()
    api._loop = MagicMock()
    api._send_play_message = MagicMock()
    api._send_debug = MagicMock()
    game.active_player._is_ai = True
    game.play_auto = MagicMock()
    game._is_debug = True

    api._play_ai(game)

    game.play_auto.assert_called_once_with()
    api._send_play_message.assert_called_once_with(game, game.active_player)
    api._loop.call_later.assert_called_once_with(api.AI_TIMEOUT, api._process_play_request)
    assert api._send_debug.call_count == 1
    args_last_call = api._send_debug.call_args[0][0]
    assert args_last_call['player'] == 'Player 0'
    assert len(args_last_call['hand']) == 5


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
