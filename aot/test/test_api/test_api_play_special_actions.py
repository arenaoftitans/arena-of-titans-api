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

import pytest

from aot.api.utils import (
    AotError,
    AotErrorToDisplay,
    RequestTypes,
)
from aot.board import Square
from aot.cards.trumps import (
    SimpleTrump,
    Trump,
    TrumpList,
)
from aot.game import Player
from aot.test import (
    api,
    game,
)
from unittest.mock import MagicMock


def test_view_possible_action_no_name(api, game):
    with pytest.raises(AotError) as e:
        api._view_possible_actions(game, {})

    assert 'missing_action_name' in str(e)


def test_view_possible_action_no_target_index(api, game):
    with pytest.raises(AotError) as e:
        api._view_possible_actions(game, {'name': 'action'})

    assert 'missing_action_target' in str(e)


def test_view_possible_action_no_action_for_player(api, game):
    with pytest.raises(AotError) as e:
        api._view_possible_actions(game, {'name': 'action', 'target_index': 0})

    assert 'no_action' in str(e)


def test_view_possible_action_wrong_action(api, game):
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type=None, args=None))
    game.active_player.special_actions = actions

    with pytest.raises(AotError) as e:
        api._view_possible_actions(game, {'name': 'toto', 'target_index': 0})

    assert 'wrong_action' in str(e)


def test_view_possible_action(api, game):
    api.sendMessage = MagicMock()
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type='Teleport', args={}))
    game.active_player.special_actions = actions

    api._view_possible_actions(game, {'name': 'action', 'target_index': 0})

    args = api.sendMessage.call_args[0][0]
    assert api.sendMessage.called
    assert args['rt'] == RequestTypes.SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS
    assert isinstance(args['possible_squares'], set)


def test_play_special_action_no_name(api, game):
    with pytest.raises(AotError) as e:
        api._play_special_action(game, {})

    assert 'missing_action_name' in str(e)


def test_play_special_action_no_target_index(api, game):
    with pytest.raises(AotError) as e:
        api._play_special_action(game, {'name': 'action'})

    assert 'missing_action_target' in str(e)


def test_play_special_action_no_action_for_player(api, game):
    with pytest.raises(AotError) as e:
        api._play_special_action(game, {'name': 'action', 'target_index': 0})

    assert 'no_action' in str(e)


def test_play_special_action_wrong_action(api, game):
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type=None, args=None))
    game.active_player.special_actions = actions

    with pytest.raises(AotError) as e:
        api._play_special_action(game, {'name': 'toto', 'target_index': 0})

    assert 'wrong_action' in str(e)


def test_play_special_action_no_square(api, game):
    api.sendMessage = MagicMock()
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type='Teleport', args={}))
    game.active_player.special_actions = actions

    with pytest.raises(AotErrorToDisplay) as e:
        api._play_special_action(game, {'name': 'action', 'target_index': 0})

    assert 'wrong_square' in str(e)


def test_play_special_action(api, game):
    def consume_action(*args, **kwargs):
        game.active_player._special_actions_names.remove('action')

    api.sendMessage = MagicMock()
    api._notify_special_action = MagicMock()
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type='Teleport', args={}))
    game.active_player.special_actions = actions
    game.active_player.play_special_action = MagicMock(side_effect=consume_action)
    game.complete_special_actions = MagicMock()
    game.add_action = MagicMock()
    play_request = {
        'name': 'action',
        'target_index': 0,
        'x': 0,
        'y': 0,
    }

    api._play_special_action(game, play_request)

    assert game.active_player.play_special_action.called
    args = game.active_player.play_special_action.call_args_list
    assert len(args[0][0]) == 1
    assert isinstance(args[0][0][0], Trump)
    assert len(args[0][1]) == 2
    assert isinstance(args[0][1].get('target', None), Player)
    assert len(args[0][1].get('action_args', {})) == 1
    assert isinstance(args[0][1]['action_args'].get('square', None), Square)
    assert game.add_action.called
    game.complete_special_actions.assert_called_once_with()
    assert not api._notify_special_action.called


def test_play_special_action_actions_still_remaining(api, game):
    def consume_action(*args, **kwargs):
        game.active_player._special_actions_names.remove('action')

    api.sendMessage = MagicMock()
    api._notify_special_action = MagicMock()
    actions = TrumpList()
    actions.append(SimpleTrump(name='action', type='Teleport', args={}))
    actions.append(SimpleTrump(name='action2', type='Teleport', args={}))
    game.active_player.special_actions = actions
    game.active_player.play_special_action = MagicMock(side_effect=consume_action)
    game.complete_special_actions = MagicMock()
    game.add_action = MagicMock()
    play_request = {
        'name': 'action',
        'target_index': 0,
        'x': 0,
        'y': 0,
    }

    api._play_special_action(game, play_request)

    assert game.active_player.play_special_action.called
    args = game.active_player.play_special_action.call_args_list
    assert len(args[0][0]) == 1
    assert isinstance(args[0][0][0], Trump)
    assert len(args[0][1]) == 2
    assert isinstance(args[0][1].get('target', None), Player)
    assert len(args[0][1].get('action_args', {})) == 1
    assert isinstance(args[0][1]['action_args'].get('square', None), Square)
    assert game.add_action.called
    assert not game.complete_special_actions.called
    api._notify_special_action.assert_called_once_with('action2')
