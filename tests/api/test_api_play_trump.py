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

from unittest.mock import AsyncMock, MagicMock

import pytest

from aot.api.utils import AotError
from aot.game.board import Color
from aot.game.trumps import CannotBeAffectedByTrumpsPower, NewTrumpsList, RemoveColor


@pytest.fixture()
def red_tower_trump():
    return RemoveColor(name="Tower", color=Color.RED, cost=4, duration=1, must_target_player=True)


@pytest.mark.asyncio
async def test_play_trump_wrong_trump(api, game):  # noqa: F811
    with pytest.raises(AotError) as e:
        await api._play_trump(game, {"name": "Inexistant name"})

    assert "wrong_trump" in str(e)


@pytest.mark.asyncio
async def test_play_trump_missing_target(api, game):  # noqa: F811
    for trump in game.active_player.trumps:
        if trump["must_target_player"]:
            break

    with pytest.raises(AotError) as e:
        await api._play_trump(game, {"name": trump["name"], "color": trump["color"]})

    assert "missing_trump_target" in str(e)


@pytest.mark.asyncio
async def test_play_trump_with_wrong_target(api, game):  # noqa: F811
    for trump in game.active_player.trumps:
        if trump["must_target_player"]:
            break

    with pytest.raises(AotError) as e:
        await api._play_trump(
            game, {"name": trump["name"], "color": trump["color"], "target_index": 10}
        )

    assert "The target of this trump does not exist" in str(e)


@pytest.mark.asyncio
async def test_play_trump_max_number_trumps_played(api, game):  # noqa: F811
    trump = game.active_player.trumps[0]
    trump["must_target_player"] = True
    game.active_player._number_trumps_played = game.active_player.MAX_NUMBER_TRUMPS_PLAYED
    game.active_player._gauge.can_play_trump = MagicMock(return_value=True)

    with pytest.raises(AotError) as e:
        await api._play_trump(
            game, {"name": trump["name"], "color": trump["color"], "target_index": 0}
        )

    assert "max_number_played_trumps" in str(e)


@pytest.mark.asyncio
async def test_play_trump_max_number_affecting_trumps(
    api, game, player, red_tower_trump
):  # noqa: F811
    trump = game.active_player.trumps[0]
    trump["must_target_player"] = True
    game.active_player._affecting_trumps = NewTrumpsList(
        [red_tower_trump.create_effect(initiator=player, target=player, context={})]
        * game.active_player.MAX_NUMBER_AFFECTING_TRUMPS
    )
    game.active_player._gauge.can_play_trump = MagicMock(return_value=True)

    with pytest.raises(AotError) as e:
        await api._play_trump(
            game, {"name": trump["name"], "color": trump["color"], "target_index": 0}
        )

    assert "max_number_trumps" in str(e)
    assert game.active_player._gauge.can_play_trump.called


@pytest.mark.asyncio
async def test_play_trump_gauge_too_low(api, game):  # noqa: F811
    trump = game.active_player.trumps[0]
    trump["must_target_player"] = True
    game.active_player._gauge.can_play_trump = MagicMock(return_value=False)

    with pytest.raises(AotError) as e:
        await api._play_trump(
            game, {"name": trump["name"], "color": trump["color"], "target_index": 0}
        )

    assert "gauge_too_low" in str(e)
    assert game.active_player._gauge.can_play_trump.called


@pytest.mark.asyncio
async def test_play_trump_with_target(api, game):  # noqa: F811
    game.active_player._gauge.can_play_trump = MagicMock(return_value=True)
    for trump in game.active_player.trumps:
        if trump["must_target_player"]:
            break
    api._send_trump_played_message = AsyncMock()
    game.add_action = MagicMock()

    await api._play_trump(game, {"name": trump["name"], "color": trump["color"], "target_index": 0})

    assert api._send_trump_played_message.called
    assert game.add_action.call_count == 1
    assert game.active_player._gauge.can_play_trump.called


@pytest.mark.asyncio
async def test_play_trump_without_target(api, game):  # noqa: F811
    game.active_player._gauge.can_play_trump = MagicMock(return_value=True)
    for trump in game.active_player.trumps:
        if not trump["must_target_player"]:
            break
    api._send_all_others = AsyncMock()
    api.sendMessage = AsyncMock()
    game.add_action = MagicMock()

    await api._play_trump(game, {"name": trump["name"], "color": trump["color"]})

    assert api._send_all_others.called
    call_args = api._send_all_others.call_args[0]
    assert call_args[0]["rt"] == "PLAY_TRUMP"
    assert api.sendMessage.called
    call_args = api.sendMessage.call_args[0]
    assert call_args[0]["rt"] == "PLAY_TRUMP"
    assert game.add_action.call_count == 1
    assert game.active_player._gauge.can_play_trump.called


@pytest.mark.asyncio
async def test_play_trump_with_target_with_passive_trump_disallow_trump(api, game):  # noqa: F811
    game.active_player._gauge.can_play_trump = MagicMock(return_value=True)
    for trump in game.active_player.trumps:
        if trump["must_target_player"]:
            break
    api._send_all_others = AsyncMock()
    api.sendMessage = AsyncMock()
    game.add_action = MagicMock()
    game.active_player._power = CannotBeAffectedByTrumpsPower(
        trump_args={"trump_names": ("Tower",)}, passive=True
    )

    await api._play_trump(game, {"name": trump["name"], "color": trump["color"], "target_index": 0})

    assert api._send_all_others.called
    call_args = api._send_all_others.call_args[0]
    assert call_args[0]["rt"] == "TRUMP_HAS_NO_EFFECT"
    assert api.sendMessage.called
    call_args = api.sendMessage.call_args[0]
    assert call_args[0]["rt"] == "TRUMP_HAS_NO_EFFECT"
    assert game.add_action.call_count == 1
    assert game.active_player._gauge.can_play_trump.called
