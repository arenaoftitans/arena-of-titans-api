from aot.test import (
    api,
    game,
)
from unittest.mock import MagicMock


def test_onClose(api, game):
    api._cache = MagicMock()
    api._cache.get_game = MagicMock(return_value=game)
    api._clients[0] = None
    api._send_play_message = MagicMock()
    api._save_game = MagicMock()
    api._loop = MagicMock()

    player = game.active_player
    game.pass_turn = MagicMock()
    game.disconnect = MagicMock(return_value=player)

    api.onClose(True, 1001, None)

    assert 0 not in api._clients

    api._loop.call_later.assert_called_once_with(
        api.DISCONNECTED_TIMEOUT_WAIT,
        api._disconnect_player
    )
    api._disconnect_player()

    api._cache.get_game.assert_called_once_with()
    api._send_play_message.assert_called_once_with(player, game)
    api._save_game.assert_called_once_with(game)

    game.disconnect.assert_called_once_with(player.id)
    game.pass_turn.assert_called_once_with()


def test_reconnect_to_game(api, game):
    timer = MagicMock()
    api._disconnect_timeouts[0] = timer
    api._reconnect_to_game(game)

    timer.cancel.assert_called_once_with()
