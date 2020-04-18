#
#  Copyright (C) 2015-2020 by Arena of Titans Contributors.
#
#  This file is part of Arena of Titans.
#
#  Arena of Titans is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Arena of Titans is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
#

import pytest

from aot.api.utils import RequestTypes
from aot.api.validation import ValidationError, validate


@pytest.mark.parametrize(
    "message",
    [
        pytest.param({}, id="empty_message"),
        pytest.param({"rt": "toto", "request": {}}, id="wrong_request_type"),
    ],
)
def test_validate_invalid_messages(snapshot, message):
    with pytest.raises(ValidationError) as e:
        validate(message)

    snapshot.assert_match(e.value.errors)


def test_validate_valid_message(snapshot):
    validated = validate(
        {"rt": "create_lobby", "request": {"hero": "Arline", "player_name": "Game master"}}
    )

    assert validated["rt"] == RequestTypes.CREATE_LOBBY
    snapshot.assert_match(validated["request"])


def test_sanitize_player_name():
    message = validate(
        {
            "rt": "update_slot",
            "request": {
                "slot": {
                    "hero": "Arline",
                    "player_name": "<script>while(true)</script>",
                    "index": 0,
                    "state": "taken",
                }
            },
        }
    )

    assert message["request"]["slot"]["player_name"] == "while(true)"


@pytest.mark.parametrize(
    "message",
    [
        pytest.param(
            {
                "rt": "update_slot",
                "request": {
                    "slot": {"player_name": "<script></script>", "index": 0, "state": "taken"}
                },
            },
            id="update_slot",
        ),
        pytest.param(
            {"rt": "join_game", "request": {"game_id": "game_id", "player_name": "<p></p>"}},
            id="join_game",
        ),
    ],
)
def test_sanitize_empty_player_name(snapshot, message):
    with pytest.raises(ValidationError) as e:
        validate(message)

    snapshot.assert_match(e.value.errors)
