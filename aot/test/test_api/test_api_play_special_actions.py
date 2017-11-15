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
    RequestTypes,
)
from ...board import Square
from ...cards.trumps import (
    SimpleTrump,
    Trump,
    TrumpList,
)
from ...game.player import Player


@pytest.mark.asyncio  # noqa: F811
async def test_view_possible_action_no_name(api, game):
    with pytest.raises(AotError) as e:
        await api._view_possible_actions(game, {})

    assert 'missing_action_name' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_view_possible_action_no_name_and_cancel(api, game):
    with pytest.raises(AotError) as e:
        await api._view_possible_actions(game, {'cancel': True})

    assert 'missing_action_name' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_view_possible_action_no_target_index(api, game):
    with pytest.raises(AotError) as e:
        await api._view_possible_actions(game, {'special_action_name': 'action'})

    assert 'missing_action_target' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_view_possible_action_no_action_for_player(api, game):
    with pytest.raises(AotError) as e:
        await api._view_possible_actions(
            game,
            {'special_action_name': 'action', 'target_index': 0},
        )

    assert 'no_action' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_view_possible_action_wrong_action(api, game):
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type=None, args=None))
    game.active_player.special_actions = actions

    with pytest.raises(AotError) as e:
        await api._view_possible_actions(game, {'special_action_name': 'toto', 'target_index': 0})

    assert 'wrong_action' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_view_possible_action(api, game):
    api.sendMessage = AsyncMagicMock()
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type='Teleport', args={}))
    game.active_player.special_actions = actions

    await api._view_possible_actions(game, {'special_action_name': 'action', 'target_index': 0})

    args = api.sendMessage.call_args[0][0]
    assert api.sendMessage.called
    assert args['rt'] == RequestTypes.SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS
    assert isinstance(args['possible_squares'], set)


@pytest.mark.asyncio  # noqa: F811
async def test_play_special_action_no_name(api, game):
    with pytest.raises(AotError) as e:
        await api._play_special_action(game, {})

    assert 'missing_action_name' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_play_special_action_no_target_index(api, game):
    with pytest.raises(AotError) as e:
        await api._play_special_action(game, {'special_action_name': 'action'})

    assert 'missing_action_target' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_play_special_action_no_action_for_player(api, game):
    with pytest.raises(AotError) as e:
        await api._play_special_action(game, {'special_action_name': 'action', 'target_index': 0})

    assert 'no_action' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_play_special_action_wrong_action(api, game):
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type=None, args=None))
    game.active_player.special_actions = actions

    with pytest.raises(AotError) as e:
        await api._play_special_action(game, {'special_action_name': 'toto', 'target_index': 0})

    assert 'wrong_action' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_play_special_action_no_square(api, game):
    api.sendMessage = AsyncMagicMock()
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type='Teleport', args={}))
    game.active_player.special_actions = actions

    with pytest.raises(AotErrorToDisplay) as e:
        await api._play_special_action(game, {'special_action_name': 'action', 'target_index': 0})

    assert 'wrong_square' in str(e)


@pytest.mark.asyncio  # noqa: F811
async def test_play_special_action(api, game):
    def consume_action(*args, **kwargs):
        game.active_player._special_actions_names.remove('action')

    api._send_player_played_special_action = AsyncMagicMock()
    api._send_play_message_to_players = AsyncMagicMock()
    api._notify_special_action = AsyncMagicMock()
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type='Teleport', args={}))
    game.active_player.special_actions = actions
    game.play_special_action = MagicMock(side_effect=consume_action)
    game.complete_special_actions = MagicMock()
    game.add_action = MagicMock()
    play_request = {
        'special_action_name': 'action',
        'target_index': 0,
        'x': 0,
        'y': 0,
    }

    await api._play_special_action(game, play_request)

    assert game.play_special_action.called
    args = game.play_special_action.call_args_list
    assert len(args[0][0]) == 1
    assert isinstance(args[0][0][0], Trump)
    assert len(args[0][1]) == 2
    assert isinstance(args[0][1].get('target', None), Player)
    assert len(args[0][1].get('action_args', {})) == 1
    assert isinstance(args[0][1]['action_args'].get('square', None), Square)
    assert game.add_action.called
    assert api._send_player_played_special_action.called
    assert api._send_play_message_to_players.called
    game.complete_special_actions.assert_called_once_with()
    assert not api._notify_special_action.called


@pytest.mark.asyncio  # noqa: F811
async def test_play_special_action_actions_still_remaining(api, game):
    def consume_action(*args, **kwargs):
        game.active_player._special_actions_names.remove('action')

    api._send_player_played_special_action = AsyncMagicMock()
    api._send_play_message_to_players = AsyncMagicMock()
    api._notify_special_action = AsyncMagicMock()
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type='Teleport', args={}))
    actions.append(SimpleTrump(name='action2', type='Teleport', args={}))
    game.active_player.special_actions = actions
    game.play_special_action = MagicMock(side_effect=consume_action)
    game.complete_special_actions = MagicMock()
    game.add_action = MagicMock()
    play_request = {
        'special_action_name': 'action',
        'target_index': 0,
        'x': 0,
        'y': 0,
    }

    await api._play_special_action(game, play_request)

    assert game.play_special_action.called
    args = game.play_special_action.call_args_list
    assert len(args[0][0]) == 1
    assert isinstance(args[0][0][0], Trump)
    assert len(args[0][1]) == 2
    assert isinstance(args[0][1].get('target', None), Player)
    assert len(args[0][1].get('action_args', {})) == 1
    assert isinstance(args[0][1]['action_args'].get('square', None), Square)
    assert game.add_action.called
    assert api._send_player_played_special_action.called
    assert not api._send_play_message_to_players.called
    assert not game.complete_special_actions.called
    api._notify_special_action.assert_called_once_with('action2')


@pytest.mark.asyncio  # noqa: F811
async def test_cancel_special_action(api, game):
    def consume_action(*args, **kwargs):
        game.active_player._special_actions_names.remove('action')

    api._send_player_played_special_action = AsyncMagicMock()
    api._send_play_message_to_players = AsyncMagicMock()
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type='Teleport', args={}))
    game.active_player.special_actions = actions
    game.play_special_action = MagicMock()
    game.complete_special_actions = MagicMock()
    game.add_action = MagicMock()
    game.cancel_special_action = MagicMock(side_effect=consume_action)
    play_request = {
        'special_action_name': 'action',
        'cancel': True,
    }

    await api._play_special_action(game, play_request)

    assert game.cancel_special_action.called
    assert not game.add_action.called
    assert not api._send_player_played_special_action.called
    assert api._send_play_message_to_players.called
    assert game.complete_special_actions.called
