# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateGame.test_create_lobby game_master-0'] = {
    'request': {
        'api_version': 'latest',
        'game_id': 'test-game-id',
        'index': 0,
        'is_game_master': True,
        'player_id': 'test-game-master-id',
        'slots': [
            {
                'hero': 'Arline',
                'index': 0,
                'player_name': 'Game master',
                'state': 'TAKEN'
            },
            {
                'index': 1,
                'player_name': '',
                'state': 'OPEN'
            },
            {
                'index': 2,
                'player_name': '',
                'state': 'OPEN'
            },
            {
                'index': 3,
                'player_name': '',
                'state': 'OPEN'
            }
        ]
    },
    'rt': 'JOINED_LOBBY'
}

snapshots['TestCreateGame.test_create_lobby game_master-1'] = {
    'request': {
        'slots': [
            {
                'hero': 'Arline',
                'index': 0,
                'player_name': 'Game master',
                'state': 'TAKEN'
            },
            {
                'index': 1,
                'player_name': '',
                'state': 'OPEN'
            },
            {
                'index': 2,
                'player_name': '',
                'state': 'OPEN'
            },
            {
                'index': 3,
                'player_name': '',
                'state': 'OPEN'
            }
        ]
    },
    'rt': 'SLOT_UPDATED'
}

snapshots['TestCreateGame.test_join_game player-0'] = {
    'request': {
        'api_version': 'latest',
        'game_id': 'test-game-id',
        'index': 1,
        'is_game_master': False,
        'player_id': 'player_id',
        'slots': [
            {
                'hero': 'Arline',
                'index': 0,
                'player_name': 'Game master',
                'state': 'TAKEN'
            },
            {
                'hero': 'Ulya',
                'index': 1,
                'player_name': 'Player name',
                'state': 'TAKEN'
            },
            {
                'index': 2,
                'player_name': '',
                'state': 'OPEN'
            },
            {
                'index': 3,
                'player_name': '',
                'state': 'OPEN'
            }
        ]
    },
    'rt': 'JOINED_LOBBY'
}

snapshots['TestCreateGame.test_join_game player-1'] = {
    'request': {
        'slots': [
            {
                'hero': 'Arline',
                'index': 0,
                'player_name': 'Game master',
                'state': 'TAKEN'
            },
            {
                'hero': 'Ulya',
                'index': 1,
                'player_name': 'Player name',
                'state': 'TAKEN'
            },
            {
                'index': 2,
                'player_name': '',
                'state': 'OPEN'
            },
            {
                'index': 3,
                'player_name': '',
                'state': 'OPEN'
            }
        ]
    },
    'rt': 'SLOT_UPDATED'
}

snapshots['TestCreateGame.test_join_game game_master-0'] = {
    'request': {
        'slots': [
            {
                'hero': 'Arline',
                'index': 0,
                'player_name': 'Game master',
                'state': 'TAKEN'
            },
            {
                'hero': 'Ulya',
                'index': 1,
                'player_name': 'Player name',
                'state': 'TAKEN'
            },
            {
                'index': 2,
                'player_name': '',
                'state': 'OPEN'
            },
            {
                'index': 3,
                'player_name': '',
                'state': 'OPEN'
            }
        ]
    },
    'rt': 'SLOT_UPDATED'
}

snapshots['TestCreateGame.test_update_slot player-0'] = {
    'request': {
        'slots': [
            {
                'hero': 'Arline',
                'index': 0,
                'player_name': 'Game master',
                'state': 'TAKEN'
            },
            {
                'hero': 'Djor',
                'index': 1,
                'player_name': 'Player updated',
                'state': 'TAKEN'
            },
            {
                'index': 2,
                'player_name': '',
                'state': 'OPEN'
            },
            {
                'index': 3,
                'player_name': '',
                'state': 'OPEN'
            }
        ]
    },
    'rt': 'SLOT_UPDATED'
}

snapshots['TestCreateGame.test_update_slot game_master-0'] = {
    'request': {
        'slots': [
            {
                'hero': 'Arline',
                'index': 0,
                'player_name': 'Game master',
                'state': 'TAKEN'
            },
            {
                'hero': 'Djor',
                'index': 1,
                'player_name': 'Player updated',
                'state': 'TAKEN'
            },
            {
                'index': 2,
                'player_name': '',
                'state': 'OPEN'
            },
            {
                'index': 3,
                'player_name': '',
                'state': 'OPEN'
            }
        ]
    },
    'rt': 'SLOT_UPDATED'
}

snapshots['TestCreateGame.test_player_close_slot player-0'] = {
    'request': {
        'slots': [
            {
                'hero': 'Arline',
                'index': 0,
                'player_name': 'Game master',
                'state': 'TAKEN'
            },
            {
                'hero': 'Djor',
                'index': 1,
                'player_name': 'Player updated',
                'state': 'TAKEN'
            },
            {
                'index': 2,
                'player_name': '',
                'state': 'OPEN'
            },
            {
                'index': 3,
                'player_name': '',
                'state': 'OPEN'
            }
        ]
    },
    'rt': 'SLOT_UPDATED'
}

snapshots['TestCreateGame.test_player_close_slot game_master-0'] = {
    'request': {
        'slots': [
            {
                'hero': 'Arline',
                'index': 0,
                'player_name': 'Game master',
                'state': 'TAKEN'
            },
            {
                'hero': 'Djor',
                'index': 1,
                'player_name': 'Player updated',
                'state': 'TAKEN'
            },
            {
                'index': 2,
                'player_name': '',
                'state': 'OPEN'
            },
            {
                'index': 3,
                'player_name': '',
                'state': 'OPEN'
            }
        ]
    },
    'rt': 'SLOT_UPDATED'
}

snapshots['TestCreateGame.test_game_master_close_slot game_master-0'] = {
    'request': {
        'slots': [
            {
                'hero': 'Arline',
                'index': 0,
                'player_name': 'Game master',
                'state': 'TAKEN'
            },
            {
                'hero': 'Djor',
                'index': 1,
                'player_name': 'Player updated',
                'state': 'TAKEN'
            },
            {
                'index': 2,
                'state': 'CLOSED'
            },
            {
                'index': 3,
                'player_name': '',
                'state': 'OPEN'
            }
        ]
    },
    'rt': 'SLOT_UPDATED'
}

snapshots['TestCreateGame.test_game_master_close_slot player-0'] = {
    'request': {
        'slots': [
            {
                'hero': 'Arline',
                'index': 0,
                'player_name': 'Game master',
                'state': 'TAKEN'
            },
            {
                'hero': 'Djor',
                'index': 1,
                'player_name': 'Player updated',
                'state': 'TAKEN'
            },
            {
                'index': 2,
                'state': 'CLOSED'
            },
            {
                'index': 3,
                'player_name': '',
                'state': 'OPEN'
            }
        ]
    },
    'rt': 'SLOT_UPDATED'
}

snapshots['TestCreateGame.test_player_create_game player-0'] = {
    'error_to_display': 'Only the game master can use RequestTypes.CREATE_GAME request.',
    'extra_data': {
        'rt': 'CREATE_GAME'
    },
    'is_fatal': False
}

snapshots['TestCreateGame.test_game_master_create_game_missing_player game_master-0'] = {
    'error': 'Number of registered players differs with number of players descriptions or too many/too few players are registered.',
    'is_fatal': False
}

snapshots['TestCreateGame.test_game_master_create_game game_master-0'] = {
    'request': {
        'active_trumps': [
        ],
        'available_trumps': [
            {
                'apply_on_initiator': False,
                'color': None,
                'colors': [
                ],
                'cost': 6,
                'delta_moves': -1,
                'description': 'Reduce the number of cards a player can play by 1.',
                'duration': 1,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Blizzard',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLACK',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLUE',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'RED',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 10,
        'gauge_value': 0,
        'hand': [
            {
                'color': 'YELLOW',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'RED',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLUE',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLACK',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'YELLOW',
                'description': 'Move one square in line',
                'name': 'Warrior'
            }
        ],
        'has_remaining_moves_to_play': True,
        'has_won': False,
        'hero': 'Arline',
        'id': 'test-game-master-id',
        'index': 0,
        'name': 'Game master',
        'on_last_line': False,
        'power': {
            'cost': 10,
            'description': 'Disappear from the board and cannot be targeted by other players.',
            'duration': 2,
            'is_player_visible': False,
            'is_power': True,
            'must_target_player': False,
            'name': 'Night mist',
            'passive': False,
            'require_square_target': False,
            'trump_cost_delta': 0,
            'trump_names': [
            ]
        },
        'rank': -1,
        'special_action': None,
        'trump_target_indexes': [
            0,
            1
        ],
        'trumps_statuses': [
            False,
            False,
            False,
            False
        ],
        'your_turn': True
    },
    'rt': 'PLAYER_UPDATED'
}

snapshots['TestCreateGame.test_game_master_create_game game_master-1'] = {
    'request': {
        'actions': [
            {
                'card': None,
                'description': 'nothing_happened',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            }
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'current_player_index': 0,
        'id': 'test-game-id',
        'is_over': False,
        'nb_turns': 0,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Arline',
                'index': 0,
                'is_visible': True,
                'name': 'Game master',
                'square': {
                    'color': 'RED',
                    'x': 6,
                    'y': 7
                }
            },
            '1': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Djor',
                'index': 1,
                'is_visible': True,
                'name': 'Player',
                'square': {
                    'color': 'YELLOW',
                    'x': 6,
                    'y': 8
                }
            }
        },
        'winners': [
        ]
    },
    'rt': 'GAME_UPDATED'
}

snapshots['TestCreateGame.test_game_master_create_game player-0'] = {
    'request': {
        'active_trumps': [
        ],
        'available_trumps': [
            {
                'apply_on_initiator': False,
                'color': None,
                'colors': [
                ],
                'cost': 8,
                'delta_moves': -1,
                'description': 'Reduce the number of cards a player can play by 1.',
                'duration': 1,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Blizzard',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLACK',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLUE',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'RED',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 10,
        'gauge_value': 0,
        'hand': [
            {
                'color': 'YELLOW',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'RED',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLUE',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLACK',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'YELLOW',
                'description': 'Move one square in line',
                'name': 'Warrior'
            }
        ],
        'has_remaining_moves_to_play': True,
        'has_won': False,
        'hero': 'Djor',
        'id': 'player_id',
        'index': 1,
        'name': 'Player',
        'on_last_line': False,
        'power': {
            'cost': 0,
            'description': 'Your tower and fortress cannot be destroyed.',
            'enable_for_trumps': [
                'Fortress',
                'Tower'
            ],
            'is_power': True,
            'must_target_player': False,
            'name': 'Impassable',
            'passive': True,
            'prevent_trumps_to_modify': [
                'Force of nature',
                'Ram'
            ],
            'require_square_target': False,
            'trump_cost_delta': 2
        },
        'rank': -1,
        'special_action': None,
        'trump_target_indexes': [
            0,
            1
        ],
        'trumps_statuses': [
            False,
            False,
            False,
            False
        ],
        'your_turn': False
    },
    'rt': 'PLAYER_UPDATED'
}

snapshots['TestCreateGame.test_game_master_create_game player-1'] = {
    'request': {
        'actions': [
            {
                'card': None,
                'description': 'nothing_happened',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            }
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'current_player_index': 0,
        'id': 'test-game-id',
        'is_over': False,
        'nb_turns': 0,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Arline',
                'index': 0,
                'is_visible': True,
                'name': 'Game master',
                'square': {
                    'color': 'RED',
                    'x': 6,
                    'y': 7
                }
            },
            '1': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Djor',
                'index': 1,
                'is_visible': True,
                'name': 'Player',
                'square': {
                    'color': 'YELLOW',
                    'x': 6,
                    'y': 8
                }
            }
        },
        'winners': [
        ]
    },
    'rt': 'GAME_UPDATED'
}

snapshots['TestPlayGame.test_reconnect_game_master game_master-0'] = {
    'request': {
        'game': {
            'actions': [
                {
                    'card': None,
                    'description': 'nothing_happened',
                    'initiator': {
                        'index': 0,
                        'name': 'Game master'
                    },
                    'special_action': None,
                    'target': None,
                    'trump': None
                }
            ],
            'board': {
                'updated_squares': [
                ]
            },
            'current_player_index': 0,
            'id': 'test-game-id',
            'is_over': False,
            'nb_turns': 0,
            'players': {
                '0': {
                    'active_trumps': [
                    ],
                    'can_pawn_be_selected': True,
                    'hero': 'Arline',
                    'index': 0,
                    'is_visible': True,
                    'name': 'Game master',
                    'square': {
                        'color': 'RED',
                        'x': 6,
                        'y': 7
                    }
                },
                '1': {
                    'active_trumps': [
                    ],
                    'can_pawn_be_selected': True,
                    'hero': 'Djor',
                    'index': 1,
                    'is_visible': True,
                    'name': 'Player',
                    'square': {
                        'color': 'YELLOW',
                        'x': 6,
                        'y': 8
                    }
                }
            },
            'winners': [
            ]
        },
        'player': {
            'active_trumps': [
            ],
            'available_trumps': [
                {
                    'apply_on_initiator': False,
                    'color': None,
                    'colors': [
                    ],
                    'cost': 6,
                    'delta_moves': -1,
                    'description': 'Reduce the number of cards a player can play by 1.',
                    'duration': 1,
                    'is_player_visible': True,
                    'must_target_player': True,
                    'name': 'Blizzard',
                    'prevent_trumps_to_modify': [
                    ],
                    'require_square_target': False
                },
                {
                    'apply_on_initiator': False,
                    'color': 'BLACK',
                    'colors': [
                    ],
                    'cost': 7,
                    'description': 'Prevent the player to move on some colors.',
                    'duration': 2,
                    'is_player_visible': True,
                    'must_target_player': True,
                    'name': 'Fortress',
                    'prevent_trumps_to_modify': [
                    ],
                    'require_square_target': False
                },
                {
                    'apply_on_initiator': False,
                    'color': 'BLUE',
                    'colors': [
                    ],
                    'cost': 7,
                    'description': 'Prevent the player to move on some colors.',
                    'duration': 2,
                    'is_player_visible': True,
                    'must_target_player': True,
                    'name': 'Fortress',
                    'prevent_trumps_to_modify': [
                    ],
                    'require_square_target': False
                },
                {
                    'apply_on_initiator': False,
                    'color': 'RED',
                    'colors': [
                    ],
                    'cost': 7,
                    'description': 'Prevent the player to move on some colors.',
                    'duration': 2,
                    'is_player_visible': True,
                    'must_target_player': True,
                    'name': 'Fortress',
                    'prevent_trumps_to_modify': [
                    ],
                    'require_square_target': False
                }
            ],
            'can_power_be_played': False,
            'elapsed_time': 10,
            'gauge_value': 0,
            'hand': [
                {
                    'color': 'YELLOW',
                    'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                    'name': 'Wizard'
                },
                {
                    'color': 'RED',
                    'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                    'name': 'Wizard'
                },
                {
                    'color': 'BLUE',
                    'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                    'name': 'Wizard'
                },
                {
                    'color': 'BLACK',
                    'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                    'name': 'Wizard'
                },
                {
                    'color': 'YELLOW',
                    'description': 'Move one square in line',
                    'name': 'Warrior'
                }
            ],
            'has_remaining_moves_to_play': True,
            'has_won': False,
            'hero': 'Arline',
            'id': 'test-game-master-id',
            'index': 0,
            'name': 'Game master',
            'on_last_line': False,
            'power': {
                'cost': 10,
                'description': 'Disappear from the board and cannot be targeted by other players.',
                'duration': 2,
                'is_player_visible': False,
                'is_power': True,
                'must_target_player': False,
                'name': 'Night mist',
                'passive': False,
                'require_square_target': False,
                'trump_cost_delta': 0,
                'trump_names': [
                ]
            },
            'rank': -1,
            'special_action': None,
            'trump_target_indexes': [
                0,
                1
            ],
            'trumps_statuses': [
                False,
                False,
                False,
                False
            ],
            'your_turn': True
        }
    },
    'rt': 'JOIN_GAME'
}

snapshots['TestPlayGame.test_reconnect_player_wrong_game_id player-0'] = {
    'error_to_display': 'errors.player_already_connected',
    'is_fatal': True
}

snapshots['TestPlayGame.test_reconnect_player_wrong_player_id player-0'] = {
    'error_to_display': 'You cannot join this game. No slots opened.',
    'is_fatal': False
}

snapshots['TestPlayGame.test_reconnect_player player-0'] = {
    'request': {
        'game': {
            'actions': [
                {
                    'card': None,
                    'description': 'nothing_happened',
                    'initiator': {
                        'index': 0,
                        'name': 'Game master'
                    },
                    'special_action': None,
                    'target': None,
                    'trump': None
                }
            ],
            'board': {
                'updated_squares': [
                ]
            },
            'current_player_index': 0,
            'id': 'test-game-id',
            'is_over': False,
            'nb_turns': 0,
            'players': {
                '0': {
                    'active_trumps': [
                    ],
                    'can_pawn_be_selected': True,
                    'hero': 'Arline',
                    'index': 0,
                    'is_visible': True,
                    'name': 'Game master',
                    'square': {
                        'color': 'RED',
                        'x': 6,
                        'y': 7
                    }
                },
                '1': {
                    'active_trumps': [
                    ],
                    'can_pawn_be_selected': True,
                    'hero': 'Djor',
                    'index': 1,
                    'is_visible': True,
                    'name': 'Player',
                    'square': {
                        'color': 'YELLOW',
                        'x': 6,
                        'y': 8
                    }
                }
            },
            'winners': [
            ]
        },
        'player': {
            'active_trumps': [
            ],
            'available_trumps': [
                {
                    'apply_on_initiator': False,
                    'color': None,
                    'colors': [
                    ],
                    'cost': 8,
                    'delta_moves': -1,
                    'description': 'Reduce the number of cards a player can play by 1.',
                    'duration': 1,
                    'is_player_visible': True,
                    'must_target_player': True,
                    'name': 'Blizzard',
                    'prevent_trumps_to_modify': [
                    ],
                    'require_square_target': False
                },
                {
                    'apply_on_initiator': False,
                    'color': 'BLACK',
                    'colors': [
                    ],
                    'cost': 9,
                    'description': 'Prevent the player to move on some colors.',
                    'duration': 2,
                    'is_player_visible': True,
                    'must_target_player': True,
                    'name': 'Fortress',
                    'prevent_trumps_to_modify': [
                        'Force of nature',
                        'Ram'
                    ],
                    'require_square_target': False
                },
                {
                    'apply_on_initiator': False,
                    'color': 'BLUE',
                    'colors': [
                    ],
                    'cost': 9,
                    'description': 'Prevent the player to move on some colors.',
                    'duration': 2,
                    'is_player_visible': True,
                    'must_target_player': True,
                    'name': 'Fortress',
                    'prevent_trumps_to_modify': [
                        'Force of nature',
                        'Ram'
                    ],
                    'require_square_target': False
                },
                {
                    'apply_on_initiator': False,
                    'color': 'RED',
                    'colors': [
                    ],
                    'cost': 9,
                    'description': 'Prevent the player to move on some colors.',
                    'duration': 2,
                    'is_player_visible': True,
                    'must_target_player': True,
                    'name': 'Fortress',
                    'prevent_trumps_to_modify': [
                        'Force of nature',
                        'Ram'
                    ],
                    'require_square_target': False
                }
            ],
            'can_power_be_played': False,
            'elapsed_time': 10,
            'gauge_value': 0,
            'hand': [
                {
                    'color': 'YELLOW',
                    'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                    'name': 'Wizard'
                },
                {
                    'color': 'RED',
                    'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                    'name': 'Wizard'
                },
                {
                    'color': 'BLUE',
                    'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                    'name': 'Wizard'
                },
                {
                    'color': 'BLACK',
                    'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                    'name': 'Wizard'
                },
                {
                    'color': 'YELLOW',
                    'description': 'Move one square in line',
                    'name': 'Warrior'
                }
            ],
            'has_remaining_moves_to_play': True,
            'has_won': False,
            'hero': 'Djor',
            'id': 'player_id',
            'index': 1,
            'name': 'Player',
            'on_last_line': False,
            'power': {
                'cost': 0,
                'description': 'Your tower and fortress cannot be destroyed.',
                'enable_for_trumps': [
                    'Fortress',
                    'Tower'
                ],
                'is_power': True,
                'must_target_player': False,
                'name': 'Impassable',
                'passive': True,
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False,
                'trump_cost_delta': 2
            },
            'rank': -1,
            'special_action': None,
            'trump_target_indexes': [
                0,
                1
            ],
            'trumps_statuses': [
                False,
                False,
                False,
                False
            ],
            'your_turn': False
        }
    },
    'rt': 'JOIN_GAME'
}

snapshots['TestPlayGame.test_reconnect_player_already_connected player-0'] = {
    'error_to_display': 'errors.player_already_connected',
    'is_fatal': True
}

snapshots['TestPlayGame.test_play_card_not_your_turn player-0'] = {
    'error_to_display': 'Not your turn.',
    'is_fatal': False
}

snapshots['TestPlayGame.test_play_card_not_in_hand game_master-0'] = {
    'error_to_display': "This card doesn't exist or is not in your hand.",
    'is_fatal': False
}

snapshots['TestPlayGame.test_play_card_wrong_square game_master-0'] = {
    'error_to_display': "This square doesn't exist or you cannot move there yet.",
    'is_fatal': False
}

snapshots['TestPlayGame.test_view_possible_squares game_master-0'] = {
    'request': {
        'possible_squares': [
            {
                'color': 'RED',
                'x': 5,
                'y': 7
            },
            {
                'color': 'YELLOW',
                'x': 5,
                'y': 8
            }
        ]
    },
    'rt': 'VIEW_POSSIBLE_SQUARES'
}

snapshots['TestPlayGame.test_play_card game_master-0'] = {
    'request': {
        'active_trumps': [
        ],
        'available_trumps': [
            {
                'apply_on_initiator': False,
                'color': None,
                'colors': [
                ],
                'cost': 6,
                'delta_moves': -1,
                'description': 'Reduce the number of cards a player can play by 1.',
                'duration': 1,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Blizzard',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLACK',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLUE',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'RED',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 10,
        'gauge_value': 1,
        'hand': [
            {
                'color': 'RED',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLUE',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLACK',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'YELLOW',
                'description': 'Move one square in line',
                'name': 'Warrior'
            }
        ],
        'has_remaining_moves_to_play': True,
        'has_won': False,
        'hero': 'Arline',
        'id': 'test-game-master-id',
        'index': 0,
        'name': 'Game master',
        'on_last_line': False,
        'power': {
            'cost': 10,
            'description': 'Disappear from the board and cannot be targeted by other players.',
            'duration': 2,
            'is_player_visible': False,
            'is_power': True,
            'must_target_player': False,
            'name': 'Night mist',
            'passive': False,
            'require_square_target': False,
            'trump_cost_delta': 0,
            'trump_names': [
            ]
        },
        'rank': -1,
        'special_action': None,
        'trump_target_indexes': [
            0,
            1
        ],
        'trumps_statuses': [
            False,
            False,
            False,
            False
        ],
        'your_turn': True
    },
    'rt': 'PLAYER_UPDATED'
}

snapshots['TestPlayGame.test_play_card game_master-1'] = {
    'request': {
        'actions': [
            {
                'card': {
                    'color': 'YELLOW',
                    'name': 'Wizard'
                },
                'description': 'played_card',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            }
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'current_player_index': 0,
        'id': 'test-game-id',
        'is_over': False,
        'nb_turns': 0,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Arline',
                'index': 0,
                'is_visible': True,
                'name': 'Game master',
                'square': {
                    'color': 'YELLOW',
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Djor',
                'index': 1,
                'is_visible': True,
                'name': 'Player',
                'square': {
                    'color': 'YELLOW',
                    'x': 6,
                    'y': 8
                }
            }
        },
        'winners': [
        ]
    },
    'rt': 'GAME_UPDATED'
}

snapshots['TestPlayGame.test_play_card player-0'] = {
    'request': {
        'active_trumps': [
        ],
        'available_trumps': [
            {
                'apply_on_initiator': False,
                'color': None,
                'colors': [
                ],
                'cost': 8,
                'delta_moves': -1,
                'description': 'Reduce the number of cards a player can play by 1.',
                'duration': 1,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Blizzard',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLACK',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLUE',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'RED',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 10,
        'gauge_value': 0,
        'hand': [
            {
                'color': 'YELLOW',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'RED',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLUE',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLACK',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'YELLOW',
                'description': 'Move one square in line',
                'name': 'Warrior'
            }
        ],
        'has_remaining_moves_to_play': True,
        'has_won': False,
        'hero': 'Djor',
        'id': 'player_id',
        'index': 1,
        'name': 'Player',
        'on_last_line': False,
        'power': {
            'cost': 0,
            'description': 'Your tower and fortress cannot be destroyed.',
            'enable_for_trumps': [
                'Fortress',
                'Tower'
            ],
            'is_power': True,
            'must_target_player': False,
            'name': 'Impassable',
            'passive': True,
            'prevent_trumps_to_modify': [
                'Force of nature',
                'Ram'
            ],
            'require_square_target': False,
            'trump_cost_delta': 2
        },
        'rank': -1,
        'special_action': None,
        'trump_target_indexes': [
            0,
            1
        ],
        'trumps_statuses': [
            False,
            False,
            False,
            False
        ],
        'your_turn': False
    },
    'rt': 'PLAYER_UPDATED'
}

snapshots['TestPlayGame.test_play_card player-1'] = {
    'request': {
        'actions': [
            {
                'card': {
                    'color': 'YELLOW',
                    'name': 'Wizard'
                },
                'description': 'played_card',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            }
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'current_player_index': 0,
        'id': 'test-game-id',
        'is_over': False,
        'nb_turns': 0,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Arline',
                'index': 0,
                'is_visible': True,
                'name': 'Game master',
                'square': {
                    'color': 'YELLOW',
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Djor',
                'index': 1,
                'is_visible': True,
                'name': 'Player',
                'square': {
                    'color': 'YELLOW',
                    'x': 6,
                    'y': 8
                }
            }
        },
        'winners': [
        ]
    },
    'rt': 'GAME_UPDATED'
}

snapshots['TestPlayGame.test_discard_card game_master-0'] = {
    'request': {
        'active_trumps': [
        ],
        'available_trumps': [
            {
                'apply_on_initiator': False,
                'color': None,
                'colors': [
                ],
                'cost': 6,
                'delta_moves': -1,
                'description': 'Reduce the number of cards a player can play by 1.',
                'duration': 1,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Blizzard',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLACK',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLUE',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'RED',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 10,
        'gauge_value': 1,
        'hand': [
            {
                'color': 'BLUE',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLACK',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'YELLOW',
                'description': 'Move one square in line',
                'name': 'Warrior'
            },
            {
                'color': 'RED',
                'description': 'Move one square in line',
                'name': 'Warrior'
            },
            {
                'color': 'BLUE',
                'description': 'Move one square in line',
                'name': 'Warrior'
            }
        ],
        'has_remaining_moves_to_play': False,
        'has_won': False,
        'hero': 'Arline',
        'id': 'test-game-master-id',
        'index': 0,
        'name': 'Game master',
        'on_last_line': False,
        'power': {
            'cost': 10,
            'description': 'Disappear from the board and cannot be targeted by other players.',
            'duration': 2,
            'is_player_visible': False,
            'is_power': True,
            'must_target_player': False,
            'name': 'Night mist',
            'passive': False,
            'require_square_target': False,
            'trump_cost_delta': 0,
            'trump_names': [
            ]
        },
        'rank': -1,
        'special_action': None,
        'trump_target_indexes': [
            0,
            1
        ],
        'trumps_statuses': [
            False,
            False,
            False,
            False
        ],
        'your_turn': False
    },
    'rt': 'PLAYER_UPDATED'
}

snapshots['TestPlayGame.test_discard_card game_master-1'] = {
    'request': {
        'actions': [
            {
                'card': {
                    'color': 'YELLOW',
                    'name': 'Wizard'
                },
                'description': 'played_card',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            },
            {
                'card': {
                    'color': 'RED',
                    'name': 'Wizard'
                },
                'description': 'discarded_card',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            }
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'current_player_index': 1,
        'id': 'test-game-id',
        'is_over': False,
        'nb_turns': 0,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Arline',
                'index': 0,
                'is_visible': True,
                'name': 'Game master',
                'square': {
                    'color': 'YELLOW',
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Djor',
                'index': 1,
                'is_visible': True,
                'name': 'Player',
                'square': {
                    'color': 'YELLOW',
                    'x': 6,
                    'y': 8
                }
            }
        },
        'winners': [
        ]
    },
    'rt': 'GAME_UPDATED'
}

snapshots['TestPlayGame.test_discard_card player-0'] = {
    'request': {
        'active_trumps': [
        ],
        'available_trumps': [
            {
                'apply_on_initiator': False,
                'color': None,
                'colors': [
                ],
                'cost': 8,
                'delta_moves': -1,
                'description': 'Reduce the number of cards a player can play by 1.',
                'duration': 1,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Blizzard',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLACK',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLUE',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'RED',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            }
        ],
        'can_power_be_played': True,
        'elapsed_time': 10,
        'gauge_value': 0,
        'hand': [
            {
                'color': 'YELLOW',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'RED',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLUE',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLACK',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'YELLOW',
                'description': 'Move one square in line',
                'name': 'Warrior'
            }
        ],
        'has_remaining_moves_to_play': True,
        'has_won': False,
        'hero': 'Djor',
        'id': 'player_id',
        'index': 1,
        'name': 'Player',
        'on_last_line': False,
        'power': {
            'cost': 0,
            'description': 'Your tower and fortress cannot be destroyed.',
            'enable_for_trumps': [
                'Fortress',
                'Tower'
            ],
            'is_power': True,
            'must_target_player': False,
            'name': 'Impassable',
            'passive': True,
            'prevent_trumps_to_modify': [
                'Force of nature',
                'Ram'
            ],
            'require_square_target': False,
            'trump_cost_delta': 2
        },
        'rank': -1,
        'special_action': None,
        'trump_target_indexes': [
            0,
            1
        ],
        'trumps_statuses': [
            False,
            False,
            False,
            False
        ],
        'your_turn': True
    },
    'rt': 'PLAYER_UPDATED'
}

snapshots['TestPlayGame.test_discard_card player-1'] = {
    'request': {
        'actions': [
            {
                'card': {
                    'color': 'YELLOW',
                    'name': 'Wizard'
                },
                'description': 'played_card',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            },
            {
                'card': {
                    'color': 'RED',
                    'name': 'Wizard'
                },
                'description': 'discarded_card',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            }
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'current_player_index': 1,
        'id': 'test-game-id',
        'is_over': False,
        'nb_turns': 0,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Arline',
                'index': 0,
                'is_visible': True,
                'name': 'Game master',
                'square': {
                    'color': 'YELLOW',
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Djor',
                'index': 1,
                'is_visible': True,
                'name': 'Player',
                'square': {
                    'color': 'YELLOW',
                    'x': 6,
                    'y': 8
                }
            }
        },
        'winners': [
        ]
    },
    'rt': 'GAME_UPDATED'
}

snapshots['TestPlayGame.test_pass_turn player-0'] = {
    'request': {
        'active_trumps': [
        ],
        'available_trumps': [
            {
                'apply_on_initiator': False,
                'color': None,
                'colors': [
                ],
                'cost': 8,
                'delta_moves': -1,
                'description': 'Reduce the number of cards a player can play by 1.',
                'duration': 1,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Blizzard',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLACK',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLUE',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'RED',
                'colors': [
                ],
                'cost': 9,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                    'Force of nature',
                    'Ram'
                ],
                'require_square_target': False
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 10,
        'gauge_value': 0,
        'hand': [
            {
                'color': 'YELLOW',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'RED',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLUE',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLACK',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'YELLOW',
                'description': 'Move one square in line',
                'name': 'Warrior'
            }
        ],
        'has_remaining_moves_to_play': True,
        'has_won': False,
        'hero': 'Djor',
        'id': 'player_id',
        'index': 1,
        'name': 'Player',
        'on_last_line': False,
        'power': {
            'cost': 0,
            'description': 'Your tower and fortress cannot be destroyed.',
            'enable_for_trumps': [
                'Fortress',
                'Tower'
            ],
            'is_power': True,
            'must_target_player': False,
            'name': 'Impassable',
            'passive': True,
            'prevent_trumps_to_modify': [
                'Force of nature',
                'Ram'
            ],
            'require_square_target': False,
            'trump_cost_delta': 2
        },
        'rank': -1,
        'special_action': None,
        'trump_target_indexes': [
            0,
            1
        ],
        'trumps_statuses': [
            False,
            False,
            False,
            False
        ],
        'your_turn': False
    },
    'rt': 'PLAYER_UPDATED'
}

snapshots['TestPlayGame.test_pass_turn player-1'] = {
    'request': {
        'actions': [
            {
                'card': {
                    'color': 'YELLOW',
                    'name': 'Wizard'
                },
                'description': 'played_card',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            },
            {
                'card': {
                    'color': 'RED',
                    'name': 'Wizard'
                },
                'description': 'discarded_card',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            },
            {
                'card': None,
                'description': 'passed_turn',
                'initiator': {
                    'index': 1,
                    'name': 'Player'
                },
                'special_action': None,
                'target': None,
                'trump': None
            }
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'current_player_index': 0,
        'id': 'test-game-id',
        'is_over': False,
        'nb_turns': 1,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Arline',
                'index': 0,
                'is_visible': True,
                'name': 'Game master',
                'square': {
                    'color': 'YELLOW',
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Djor',
                'index': 1,
                'is_visible': True,
                'name': 'Player',
                'square': {
                    'color': 'YELLOW',
                    'x': 6,
                    'y': 8
                }
            }
        },
        'winners': [
        ]
    },
    'rt': 'GAME_UPDATED'
}

snapshots['TestPlayGame.test_pass_turn game_master-0'] = {
    'request': {
        'active_trumps': [
        ],
        'available_trumps': [
            {
                'apply_on_initiator': False,
                'color': None,
                'colors': [
                ],
                'cost': 6,
                'delta_moves': -1,
                'description': 'Reduce the number of cards a player can play by 1.',
                'duration': 1,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Blizzard',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLACK',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'BLUE',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            },
            {
                'apply_on_initiator': False,
                'color': 'RED',
                'colors': [
                ],
                'cost': 7,
                'description': 'Prevent the player to move on some colors.',
                'duration': 2,
                'is_player_visible': True,
                'must_target_player': True,
                'name': 'Fortress',
                'prevent_trumps_to_modify': [
                ],
                'require_square_target': False
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 10,
        'gauge_value': 1,
        'hand': [
            {
                'color': 'BLUE',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'BLACK',
                'description': 'Move one squares in line or diagonal. Can move on a square of any color.',
                'name': 'Wizard'
            },
            {
                'color': 'YELLOW',
                'description': 'Move one square in line',
                'name': 'Warrior'
            },
            {
                'color': 'RED',
                'description': 'Move one square in line',
                'name': 'Warrior'
            },
            {
                'color': 'BLUE',
                'description': 'Move one square in line',
                'name': 'Warrior'
            }
        ],
        'has_remaining_moves_to_play': True,
        'has_won': False,
        'hero': 'Arline',
        'id': 'test-game-master-id',
        'index': 0,
        'name': 'Game master',
        'on_last_line': False,
        'power': {
            'cost': 10,
            'description': 'Disappear from the board and cannot be targeted by other players.',
            'duration': 2,
            'is_player_visible': False,
            'is_power': True,
            'must_target_player': False,
            'name': 'Night mist',
            'passive': False,
            'require_square_target': False,
            'trump_cost_delta': 0,
            'trump_names': [
            ]
        },
        'rank': -1,
        'special_action': None,
        'trump_target_indexes': [
            0,
            1
        ],
        'trumps_statuses': [
            False,
            False,
            False,
            False
        ],
        'your_turn': True
    },
    'rt': 'PLAYER_UPDATED'
}

snapshots['TestPlayGame.test_pass_turn game_master-1'] = {
    'request': {
        'actions': [
            {
                'card': {
                    'color': 'YELLOW',
                    'name': 'Wizard'
                },
                'description': 'played_card',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            },
            {
                'card': {
                    'color': 'RED',
                    'name': 'Wizard'
                },
                'description': 'discarded_card',
                'initiator': {
                    'index': 0,
                    'name': 'Game master'
                },
                'special_action': None,
                'target': None,
                'trump': None
            },
            {
                'card': None,
                'description': 'passed_turn',
                'initiator': {
                    'index': 1,
                    'name': 'Player'
                },
                'special_action': None,
                'target': None,
                'trump': None
            }
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'current_player_index': 0,
        'id': 'test-game-id',
        'is_over': False,
        'nb_turns': 1,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Arline',
                'index': 0,
                'is_visible': True,
                'name': 'Game master',
                'square': {
                    'color': 'YELLOW',
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'can_pawn_be_selected': True,
                'hero': 'Djor',
                'index': 1,
                'is_visible': True,
                'name': 'Player',
                'square': {
                    'color': 'YELLOW',
                    'x': 6,
                    'y': 8
                }
            }
        },
        'winners': [
        ]
    },
    'rt': 'GAME_UPDATED'
}
