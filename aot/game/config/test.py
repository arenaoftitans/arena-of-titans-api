from .boards import load_board

TEST_CONFIG = {
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
                        "name": "Assassination",
                        "cost": 0,
                        "description": "Allow you to move back another player.",
                        "duration": 0,
                        "repeat_for_each_color": False,
                        "must_target_player": True,
                        "parameters": {"type": "Teleport", "distance": 1},
                    }
                ],
            },
            {
                "name": "King",
                "number_of_movements": 3,
                "movements_type": ["line"],
                "description": "Move three squares in line.",
                "cost": 400,
            },
            {
                "name": "Queen",
                "number_of_movements": 2,
                "movements_type": ["line", "diagonal"],
                "description": "Move two squares in line or diagonal.",
                "cost": 300,
            },
            {
                "name": "Knight",
                "number_of_movements": 1,
                "movements_type": ["knight"],
                "description": "Move one square in L.",
                "cost": 200,
            },
            {
                "name": "Wizard",
                "number_of_movements": 1,
                "movements_type": ["line", "diagonal"],
                "additional_movements_colors": ["ALL"],
                "description": "Move one squares in line or diagonal. Can move on a square of any color.",  # noqa: E501
                "cost": 200,
            },
            {
                "name": "Warrior",
                "number_of_movements": 1,
                "movements_type": ["line"],
                "description": "Move one square in line",
                "cost": 100,
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
        ],
    },
    "trumps": [
        {
            "name": "Reinforcements",
            "cost": 6,
            "description": "Allow the player to play one more move.",
            "duration": 1,
            "repeat_for_each_color": False,
            "must_target_player": False,
            "parameters": {"type": "ModifyNumberMoves", "delta_moves": 1},
            "weight": 1,
        },
        {
            "name": "Tower",
            "cost": 4,
            "description": "Prevent the player to move on some colors.",
            "duration": 1,
            "repeat_for_each_color": True,
            "must_target_player": True,
            "parameters": {"type": "RemoveColor"},
            "weight": 1,
        },
    ],
    "powers": {
        "garez": {
            "name": "Inveterate Ride",
            "description": "Your knights can move on any colors",
            "passive": True,
            "cost": 0,
            "trump_cost_delta": 2,
            "must_target_player": False,
            "parameters": {
                "type": "ModifyCardColors",
                "add_colors": ["ALL"],
                "remove_colors": [],
                "card_names": ["Knight"],
            },
        }
    },
    "board": load_board("test"),
}