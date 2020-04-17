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

from cerberus import TypeDefinition, Validator

from aot.game.board import Color
from aot.game.config import GAME_CONFIGS

from ..utils import make_immutable
from .utils import RequestTypes, SlotState, sanitize

request_types_type = TypeDefinition("request_type", (RequestTypes,), ())
Validator.types_mapping["request_type"] = request_types_type

slot_state_type = TypeDefinition("slot_state", (SlotState,), ())
Validator.types_mapping["slot_state"] = slot_state_type

color_type = TypeDefinition("color", (Color,), ())
Validator.types_mapping["color"] = color_type


class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors


def _generate_heroes_list():
    heroes = set()
    for cfg in GAME_CONFIGS.values():
        heroes.update(hero.title() for hero in cfg["powers"].keys())

    return heroes


def _generate_cards_list():
    cards = set()
    for cfg in GAME_CONFIGS.values():
        cards.update(card["name"] for card in cfg["movements_cards"]["cards"])

    return cards


def _generate_trumps_list():
    trumps = set()
    for cfg in GAME_CONFIGS.values():
        trumps.update(trump["args"]["name"] for trump in cfg["trumps"])

    return trumps


def _to_request_type(value: str):
    return RequestTypes[value.upper()]


def _to_slot_state(value: str):
    return SlotState[value.upper()]


def _to_color(value: str):
    return Color[value.upper()]


def _check_slot_is_complete(field, value, error):
    if value["state"] == SlotState.TAKEN and not value.get("player_name"):
        error(field, "'player_name' cannot be empty if slot is taken")
    if value["state"] == SlotState.TAKEN and not value.get("hero"):
        error(field, "'hero' cannot be empty if slot is taken")


_REQUEST_TYPE_TO_REQUEST_VALIDATOR = make_immutable(
    {
        RequestTypes.CREATE_LOBBY: Validator(
            {
                "test": {"type": "boolean", "default": False},
                "player_name": {"type": "string", "coerce": (str, sanitize), "empty": False},
                "hero": {"type": "string", "allowed": _generate_heroes_list()},
            },
            require_all=True,
        ),
        RequestTypes.JOIN_GAME: Validator(
            {
                "game_id": {"type": "string", "empty": False},
                "hero": {"type": "string", "allowed": _generate_heroes_list()},
                "player_name": {"type": "string", "coerce": (str, sanitize), "empty": False},
            },
            require_all=True,
        ),
        RequestTypes.UPDATE_SLOT: Validator(
            {
                "slot": {
                    "type": "dict",
                    "require_all": True,
                    "check_with": _check_slot_is_complete,
                    "schema": {
                        "player_name": {
                            "type": "string",
                            "coerce": (str, sanitize),
                            "default": "",
                            "required": False,
                        },
                        "index": {"type": "integer"},
                        "state": {"type": "slot_state", "coerce": (str, _to_slot_state)},
                        "hero": {
                            "type": "string",
                            "allowed": _generate_heroes_list(),
                            "required": False,
                        },
                    },
                }
            },
            require_all=True,
        ),
        RequestTypes.CREATE_GAME: Validator(
            {
                "players": {
                    "type": "list",
                    "schema": {
                        "type": "dict",
                        "schema": {
                            "name": {"type": "string"},
                            "index": {"type": "integer", "min": 0},
                            "is_ai": {"type": "boolean", "default": False},
                        },
                    },
                }
            },
            require_all=True,
        ),
        RequestTypes.SPECIAL_ACTION_PLAY: Validator(
            {
                "cancel": {"type": "boolean", "default": False},
                "target_index": {"type": "integer", "min": 0},
                "x": {"type": "integer"},
                "y": {"type": "integer"},
            },
            require_all=True,
        ),
        RequestTypes.SPECIAL_ACTION_VIEW_POSSIBLE_ACTIONS: Validator(
            {
                "special_action_name": {"type": "string", "empty": False},
                "special_action_color": {
                    "type": "color",
                    "coerce": (str, _to_color),
                    "nullable": True,
                },
                "cancel": {"type": "boolean", "default": False},
                "target_index": {"type": "integer", "min": 0},
            },
            require_all=True,
        ),
        RequestTypes.PLAY_CARD: Validator(
            {
                "pass": {"type": "boolean", "default": False},
                "discard": {"type": "boolean", "default": False},
                "card_name": {"type": "string", "empty": False, "allowed": _generate_cards_list()},
                "card_color": {"type": "color", "coerce": (str, _to_color)},
                "x": {"type": "integer"},
                "y": {"type": "integer"},
            },
            require_all=True,
        ),
        RequestTypes.VIEW_POSSIBLE_SQUARES: Validator(
            {
                "card_name": {"type": "string", "empty": False, "allowed": _generate_cards_list()},
                "card_color": {"type": "color", "coerce": (str, _to_color)},
            },
            require_all=True,
        ),
        RequestTypes.PLAY_TRUMP: Validator(
            {
                "name": {"type": "string", "empty": False, "allowed": _generate_trumps_list()},
                "color": {"type": "color", "coerce": (str, _to_color), "nullable": True},
                "target_index": {"type": "integer", "min": 0},
                "square": {
                    "type": "dict",
                    "require_all": True,
                    "schema": {
                        "x": {"type": "integer"},
                        "y": {"type": "integer"},
                        "color": {"type": "color", "coerce": (str, _to_color)},
                    },
                },
            },
            require_all=True,
        ),
        RequestTypes.RECONNECT: Validator(
            {
                "game_id": {"type": "string", "empty": False},
                "player_id": {"type": "string", "empty": False},
            },
            require_all=True,
        ),
    }
)


def validate(message):
    message_validator = Validator(
        {
            "rt": {
                "type": "request_type",
                "coerce": (str, _to_request_type),
                "allowed": _REQUEST_TYPE_TO_REQUEST_VALIDATOR.keys(),
            },
            "request": {"type": "dict"},
        },
        require_all=True,
    )
    validated_message = message_validator.validated(message)
    if validated_message is None:
        raise ValidationError(message_validator.errors)

    request_validator = _REQUEST_TYPE_TO_REQUEST_VALIDATOR[validated_message["rt"]]
    validated_request = request_validator.validated(message["request"])
    if validated_request is None:
        raise ValidationError(request_validator.errors)

    validated_message["request"] = validated_request
    return validated_message
