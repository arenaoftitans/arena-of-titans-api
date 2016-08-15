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


def test_play_trump_wrong_trump(api, game):
    try:
        api._play_trump(game, {})
        raise AssertionError
    except AotError as e:
        assert str(e) == 'wrong_trump'


def test_play_trump_missing_target(api, game):
    for trump in game.active_player.trumps:
        if trump['must_target_player']:
            break

    try:
        api._play_trump(game, {
            'name': trump['name'],
        })
        raise AssertionError
    except AotError as e:
        assert str(e) == 'missing_trump_target'


def test_play_trump_with_wrong_target(api, game):
    for trump in game.active_player.trumps:
        if trump['must_target_player']:
            break

    try:
        api._play_trump(game, {
            'name': trump['name'],
            'target_index': 10,
        })
        raise AssertionError
    except AotError as e:
        assert str(e) == 'wrong_trump_target'


def test_play_trump_max_number_trumps_played(api, game):
    trump = game.active_player.trumps[0]
    trump['must_target_player'] = True
    game.active_player.play_trump = MagicMock(return_value=False)
    game.active_player._can_play = False

    try:
        api._play_trump(game, {
            'name': trump['name'],
            'target_index': 0,
        })
        raise AssertionError
    except AotError as e:
        assert str(e) == 'max_number_played_trumps'


def test_play_trump_max_number_affecting_trumps(api, game):
    trump = game.active_player.trumps[0]
    trump['must_target_player'] = True
    game.active_player.play_trump = MagicMock(return_value=False)

    try:
        api._play_trump(game, {
            'name': trump['name'],
            'target_index': 0,
        })
        raise AssertionError
    except AotError as e:
        assert str(e) == 'max_number_trumps'


def test_play_trump_with_target(api, game):
    for trump in game.active_player.trumps:
        if trump['must_target_player']:
            break
    api._send_all = MagicMock()
    game.add_action = MagicMock()

    api._play_trump(game, {
        'name': trump['name'],
        'target_index': 0,
    })

    assert api._send_all.call_count == 1
    assert game.add_action.call_count == 1


def test_play_trump_without_target(api, game):
    for trump in game.active_player.trumps:
        if not trump['must_target_player']:
            break
    api._send_all = MagicMock()
    game.add_action = MagicMock()

    api._play_trump(game, {
        'name': trump['name'],
    })

    assert api._send_all.call_count == 1
    assert game.add_action.call_count == 1
