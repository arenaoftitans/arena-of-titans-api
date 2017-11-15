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

from unittest.mock import MagicMock

import pytest

from .. import (  # noqa: F401
    api,
    AsyncMagicMock,
    game,
)
from ...api.utils import (
    AotError,
    AotErrorToDisplay,
)
from ...cards.trumps import (
    SimpleTrump,
    TrumpList,
)


@pytest.mark.asyncio  # noqa: F811
async def test_process_play_request_not_your_turn(api, game):
    api._cache = MagicMock()
    api._cache.get_game = AsyncMagicMock(return_value=game)
    api._save_game = AsyncMagicMock()
    api.id = 'wrong_id'

    with pytest.raises(AotErrorToDisplay) as e:
        await api._process_play_request()

    assert 'not_your_turn' in str(e)
    assert api._save_game.call_count == 0


@pytest.mark.asyncio  # noqa: F811
async def test_process_play_request_your_turn(api, game):
    api._cache = MagicMock()
    api._cache.get_game = AsyncMagicMock(return_value=game)
    api._save_game = AsyncMagicMock()
    api.id = game.active_player.id
    api._play_game = AsyncMagicMock()

    await api._process_play_request()

    api._play_game.assert_called_once_with(game)
    api._save_game.assert_called_once_with(game)


@pytest.mark.asyncio  # noqa: F811
async def test_process_play_request_ai_after_player(api, game):
    game.active_player._is_ai = True
    api._cache = MagicMock()
    api._cache.get_game = AsyncMagicMock(return_value=game)
    api._cache.save_game = AsyncMagicMock()
    api._is_player_id_correct = MagicMock(return_value=True)
    api._play_game = AsyncMagicMock()
    api._play_ai = MagicMock()
    api._loop = MagicMock()

    await api._process_play_request()

    api._play_game.assert_called_once_with(game)
    assert api._play_ai.call_count == 0
    assert api._loop.call_later.call_count == 1
    assert api._loop.call_later.call_args[0][0] == api.AI_TIMEOUT
    assert callable(api._loop.call_later.call_args[0][1])


@pytest.mark.asyncio  # noqa: F811
async def test_process_play_request_ai_after_ai(api, game):
    api._cache = MagicMock()
    api._cache.get_game = AsyncMagicMock(return_value=game)
    api._cache.save_game = AsyncMagicMock()
    api._is_player_id_correct = MagicMock(return_value=False)
    api._play_game = MagicMock()
    api._play_ai = AsyncMagicMock()
    game.active_player._is_ai = True

    await api._process_play_request()

    assert api._play_game.call_count == 0
    api._play_ai.assert_called_once_with(game)


@pytest.mark.asyncio  # noqa: F811
async def test_play_ai(api, game):
    api._cache = MagicMock()
    api._send_play_message = AsyncMagicMock()
    api._send_debug = MagicMock()
    api._game_id = 'game_id'
    api._pending_ai.add('game_id')
    api._play_ai_after_timeout = MagicMock()
    game.active_player._is_ai = True
    game.play_auto = MagicMock()

    await api._play_ai(game)

    game.play_auto.assert_called_once_with()
    api._send_play_message.assert_called_once_with(game, game.active_player)
    api._play_ai_after_timeout.assert_called_once_with(game)
    assert api._send_debug.call_count == 0


def test_play_ai_after_timeout(api, game):  # noqa: F811
    api._loop = MagicMock()
    api._game_id = 'game_id'
    assert 'game_id' not in api._pending_ai

    api._play_ai_after_timeout(game)

    assert api._loop.call_later.call_count == 1
    assert api._loop.call_later.call_args[0][0] == api.AI_TIMEOUT
    assert callable(api._loop.call_later.call_args[0][1])
    assert 'game_id' in api._pending_ai


def test_play_ai_after_timeout_game_over(api, game):  # noqa: F811
    api._loop = MagicMock()
    api._game_id = 'game_id'
    game._is_over = True
    assert 'game_id' not in api._pending_ai

    api._play_ai_after_timeout(game)

    assert api._loop.call_later.call_count == 0


@pytest.mark.asyncio  # noqa: F811
async def test_play_ai_mode_debug(api, game):
    api._cache = MagicMock()
    api._send_play_message = AsyncMagicMock()
    api._send_debug = AsyncMagicMock()
    api._game_id = 'game_id'
    api._pending_ai.add('game_id')
    api._play_ai_after_timeout = MagicMock()
    game.active_player._is_ai = True
    game.play_auto = MagicMock()
    game._is_debug = True

    await api._play_ai(game)

    game.play_auto.assert_called_once_with()
    api._send_play_message.assert_called_once_with(game, game.active_player)
    api._play_ai_after_timeout.assert_called_once_with(game)
    assert api._send_debug.call_count == 1
    args_last_call = api._send_debug.call_args[0][0]
    assert args_last_call['player'] == 'Player 0'
    assert len(args_last_call['hand']) == 5


@pytest.mark.asyncio  # noqa: F811
async def test_play_game_no_request(api, game):
    api._message = {}

    with pytest.raises(AotError) as e:
        await api._play_game(game)

    assert 'no_request' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_play_game_unknown_request(api, game):
    api._message = {
        'play_request': {},
        'rt': 'TOTO',
    }

    with pytest.raises(AotError) as e:
        await api._play_game(game)

    assert 'unknown_request' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_play_game(api, game):
    requests_to_test = [
        'VIEW_POSSIBLE_SQUARES',
        'PLAY',
        'PLAY_TRUMP',
        'SPECIAL_ACTION_PLAY',
        'SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS',
    ]
    # If not present, will use '_' + request.lower()
    requests_to_method = {
        'SPECIAL_ACTION_PLAY': '_play_special_action',
        'SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS': '_view_possible_actions',
    }
    for request in requests_to_test:
        method_name = requests_to_method.get(request, '_' + request.lower())
        setattr(api, method_name, AsyncMagicMock())

    for request in requests_to_test:
        api._message = {
            'play_request': request,
        }
        api._rt = request
        await api._play_game(game)

    for request in requests_to_test:
        method_name = requests_to_method.get(request, '_' + request.lower())
        print(method_name)
        mm = getattr(api, method_name)
        mm.assert_called_once_with(game, request)


@pytest.mark.asyncio  # noqa: F811
async def test_view_possible_squares_wrong_card(api, game):
    with pytest.raises(AotErrorToDisplay) as e:
        await api._view_possible_squares(game, {})

    assert 'wrong_card' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_view_possible_squares(api, game):
    api.sendMessage = AsyncMagicMock()
    card = game.active_player.hand[0]

    await api._view_possible_squares(game, {
        'card_name': card.name,
        'card_color': card.color,
    })

    assert api.sendMessage.call_count == 1


@pytest.mark.asyncio  # noqa: F811
async def test_play_pass(api, game):
    game.pass_turn = MagicMock()
    api._send_play_message = AsyncMagicMock()

    await api._play(game, {'pass': True})

    game.pass_turn.assert_called_once_with()
    api._send_play_message.assert_called_once_with(game, game.active_player)


@pytest.mark.asyncio  # noqa: F811
async def test_play_discard_wrong_card(api, game):
    game.discard = MagicMock()

    with pytest.raises(AotErrorToDisplay) as e:
        await api._play(game, {'discard': True})

    assert 'wrong_card' in str(e)
    assert game.discard.call_count == 0


@pytest.mark.asyncio  # noqa: F811
async def test_play_discard(api, game):
    game.discard = MagicMock()
    api._send_play_message = AsyncMagicMock()
    card = game.active_player.hand[0]

    await api._play(game, {
        'discard': True,
        'card_name': card.name,
        'card_color': card.color,
    })

    game.discard.assert_called_once_with(card)
    api._send_play_message.assert_called_once_with(game, game.active_player)


@pytest.mark.asyncio  # noqa: F811
async def test_play_wrong_card(api, game):
    game.play_card = MagicMock()
    api._send_play_message = AsyncMagicMock()

    with pytest.raises(AotErrorToDisplay) as e:
        await api._play(game, {})

    assert 'wrong_card' in str(e)
    assert game.play_card.call_count == 0


@pytest.mark.asyncio  # noqa: F811
async def test_play_wrong_square(api, game):
    game.play_card = MagicMock()
    api._send_play_message = AsyncMagicMock()
    card = game.active_player.hand[0]

    with pytest.raises(AotErrorToDisplay) as e:
        await api._play(game, {
            'card_name': card.name,
            'card_color': card.color,
        })

    assert 'wrong_square' in str(e)
    assert game.play_card.call_count == 0


@pytest.mark.asyncio  # noqa: F811
async def test_play_card(api, game):
    card = game.active_player.hand[0]
    square = game.get_square(0, 0)
    game.play_card = MagicMock(return_value=False)
    game.get_square = MagicMock(return_value=square)
    game.can_move = MagicMock(return_value=True)
    api._send_play_message = AsyncMagicMock()
    api._notify_special_actions = MagicMock()

    await api._play(game, {
        'card_name': card.name,
        'card_color': card.color,
        'x': 0,
        'y': 0,
    })

    game.play_card.assert_called_once_with(card, square)
    api._send_play_message.assert_called_once_with(game, game.active_player)
    assert not api._notify_special_actions.called


@pytest.mark.asyncio  # noqa: F811
async def test_play_card_with_special_actions(api, game):
    card = game.active_player.hand[0]
    square = game.get_square(0, 0)
    special_actions = TrumpList()
    special_actions.append(SimpleTrump(name='Action', type=None, args=None))
    game.active_player.special_actions = special_actions
    game.play_card = MagicMock(return_value=True)
    game.get_square = MagicMock(return_value=square)
    game.can_move = MagicMock(return_value=True)
    api._send_play_message = AsyncMagicMock()
    api._notify_special_action = AsyncMagicMock()

    await api._play(game, {
        'card_name': card.name,
        'card_color': card.color,
        'x': 0,
        'y': 0,
    })

    game.play_card.assert_called_once_with(card, square)
    api._send_play_message.assert_called_once_with(game, game.active_player)
    api._notify_special_action.assert_called_once_with('action')
