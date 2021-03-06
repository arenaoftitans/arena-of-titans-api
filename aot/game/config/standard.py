#
#  Copyright (C) 2015-2020 by Last Run Contributors.
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

from .boards import load_board

STANDARD_CONFIG = {
    "number_players": 4,
    "number_trumps_per_player": 4,
    "colors": ["BLACK", "BLUE", "RED", "YELLOW"],
    "movements_cards": {
        "number_cards_per_color": 1,
        "cards": [
            {
                "name": "Assassin",
                "number_of_movements": 2,
                "movements_type": ["line", "diagonal"],
                "description": "Move two squares in line or diagonal.",
                "cost": 300,
                "special_actions": [
                    {
                        "type": "Teleport",
                        "args": {
                            "trump_args": {
                                "name": "Assassination",
                                "cost": 0,
                                "description": "Allow you to move back another player.",
                                "duration": 0,
                                "must_target_player": True,
                                "distance": 1,
                            }
                        },
                    }
                ],
            },
            {
                "name": "Bishop",
                "number_of_movements": 2,
                "movements_type": ["diagonal"],
                "complementary_colors": {
                    "BLACK": ["BLUE"],
                    "BLUE": ["YELLOW"],
                    "RED": ["BLACK"],
                    "YELLOW": ["RED"],
                },
                "description": "Move two squares in diagonal. Can move on two different colors.",
                "cost": 200,
            },
            {
                "name": "King",
                "number_of_movements": 3,
                "movements_type": ["line"],
                "description": "Move three squares in line.",
                "cost": 400,
            },
            {
                "name": "Knight",
                "number_of_movements": 1,
                "movements_type": ["knight"],
                "description": "Move one square in L.",
                "cost": 200,
            },
            {
                "name": "Queen",
                "number_of_movements": 2,
                "movements_type": ["line", "diagonal"],
                "description": "Move two squares in line or diagonal.",
                "cost": 300,
            },
            {
                "name": "Warrior",
                "number_of_movements": 1,
                "movements_type": ["line"],
                "description": "Move one square in line",
                "cost": 100,
            },
            {
                "name": "Wizard",
                "number_of_movements": 1,
                "movements_type": ["line", "diagonal"],
                "additional_movements_colors": ["ALL"],
                "description": "Move one squares in line or diagonal. "
                "Can move on a square of any color.",
                "cost": 200,
            },
        ],
    },
    "trumps": [
        {
            "type": "ModifyNumberMoves",
            "repeat_for_each_color": False,
            "weight": 3,
            "args": {
                "name": "Blizzard",
                "cost": 6,
                "description": "Reduce the number of cards a player can play by 1.",
                "duration": 1,
                "must_target_player": True,
                "delta_moves": -1,
            },
        },
        {
            "type": "RemoveColor",
            "repeat_for_each_color": True,
            "weight": 1,
            "args": {
                "name": "Fortress",
                "cost": 7,
                "description": "Prevent the player to move on some colors.",
                "duration": 2,
                "must_target_player": True,
            },
        },
        {
            "type": "ModifyTrumpDurations",
            "repeat_for_each_color": False,
            "weight": 5,
            "args": {
                "name": "Ram",
                "cost": 4,
                "description": "Destroy towers and reduce duration for fortress",
                "duration": 1,
                "must_target_player": False,
                "delta_duration": -1,
                "trump_names": ["Fortress", "Tower"],
            },
        },
        {
            "type": "ModifyNumberMoves",
            "repeat_for_each_color": False,
            "weight": 3,
            "args": {
                "name": "Reinforcements",
                "cost": 8,
                "description": "Allow the player to play one more move.",
                "duration": 1,
                "must_target_player": False,
                "delta_moves": 1,
            },
        },
        {
            "type": "RemoveColor",
            "repeat_for_each_color": True,
            "weight": 1,
            "args": {
                "name": "Tower",
                "cost": 4,
                "description": "Prevent the player to move on some colors.",
                "duration": 1,
                "must_target_player": True,
            },
        },
    ],
    "powers": {
        "arline": {
            "type": "CannotBeAffectedByTrumps",
            "repeat_for_each_color": False,
            "args": {
                "passive": False,
                "trump_args": {
                    "name": "Night mist",
                    "description": "Disappear from the board and cannot be targeted by other players.",  # noqa: E501
                    "is_player_visible": False,
                    "trump_names": (),
                    "cost": 10,
                    "duration": 2,
                    "must_target_player": False,
                },
            },
        },
        "djor": {
            "type": "PreventTrumpAction",
            "args": {
                "passive": True,
                "trump_cost_delta": 2,
                "trump_args": {
                    "name": "Impassable",
                    "description": "Your tower and fortress cannot be destroyed.",
                    "must_target_player": False,
                    "cost": 0,
                    "prevent_trumps_to_modify": ["Force of nature", "Ram"],
                    "enable_for_trumps": ["Fortress", "Tower"],
                },
            },
        },
        "garez": {
            "type": "ModifyCardColors",
            "args": {
                "trump_cost_delta": 2,
                "passive": True,
                "trump_args": {
                    "name": "Inveterate Ride",
                    "description": "Your knights can move on any colors",
                    "cost": 0,
                    "must_target_player": False,
                    "colors": ["ALL"],
                    "card_names": ["Knight"],
                },
            },
        },
        "mirindrel": {
            "type": "ChangeSquare",
            "args": {
                "passive": False,
                "trump_args": {
                    "name": "Terraforming",
                    "description": "Change the color of a square",
                    "cost": 8,
                    "must_target_player": False,
                },
            },
        },
        "razbrak": {
            "type": "CannotBeAffectedByTrumps",
            "args": {
                "passive": True,
                "trump_cost_delta": 2,
                "trump_args": {
                    "name": "Force of nature",
                    "description": "Towers and fortresses have no effect.",
                    "cost": 0,
                    "must_target_player": False,
                    "trump_names": ["Fortress", "Tower"],
                },
            },
        },
        "ulya": {
            "type": "ModifyCardNumberMoves",
            "args": {
                "passive": True,
                "trump_cost_delta": 2,
                "trump_args": {
                    "name": "Domination",
                    "description": "Make queens move of 3 squares instead of 2.",
                    "cost": 0,
                    "must_target_player": False,
                    "delta_moves": 1,
                    "card_names": ["Queen"],
                },
            },
        },
        "luni": {
            "type": "AddSpecialActionsToCard",
            "args": {
                "passive": False,
                "trump_cost_delta": 0,
                "trump_args": {
                    "name": "Secret blade",
                    "description": "Add the assassination special action to Warrior cards.",
                    "cost": 10,
                    "must_target_player": False,
                    "card_names": "Warrior",
                    "spectial_action_despriptions": [
                        {
                            "type": "Teleport",
                            "repeat_for_each_color": False,
                            "args": {
                                "trump_args": {
                                    "name": "Assassination",
                                    "cost": 0,
                                    "description": "Allow you to move back another player.",
                                    "duration": 0,
                                    "must_target_player": True,
                                    "distance": 1,
                                }
                            },
                        }
                    ],
                },
            },
        },
        "kharliass": {
            "type": "StealPower",
            "args": {
                "passive": False,
                "trump_cost_delta": 0,
                "trump_args": {
                    "name": "Metamorphosis",
                    "description": "Stole the power of one of your opponent",
                    "cost": 10,
                    "duration": 1,
                    "must_target_player": True,
                },
            },
        },
    },
    "board": load_board("standard"),
}
