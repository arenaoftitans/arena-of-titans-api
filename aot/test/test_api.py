from aot.test import (
    api,
    game,
)
from unittest.mock import MagicMock


def test_onClose(api, game):
    api._cache = MagicMock()
    api._load_game = MagicMock(return_value=game)
    api._clients[0] = None
    api._send_play_message = MagicMock()
    api._save_game = MagicMock()

    player = game.active_player
    game.pass_turn = MagicMock()
    game.disconnect = MagicMock(return_value=player)

    api.onClose(True, 1001, None)

    api._load_game.assert_called_once_with()
    api._send_play_message.assert_called_once_with(player, game)
    api._save_game.assert_called_once_with(game)
    assert 0 not in api._clients

    game.disconnect.assert_called_once_with(player.id)
    game.pass_turn.assert_called_once_with()
