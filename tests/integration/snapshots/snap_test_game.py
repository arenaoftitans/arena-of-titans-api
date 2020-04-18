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
    'rt': 'JOIN_GAME'
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
    'rt': 'JOIN_GAME'
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
            {
                'player_index': 0,
                'player_name': 'Game master',
                'trumps': [
                ]
            },
            {
                'player_index': 1,
                'player_name': 'Player',
                'trumps': [
                ]
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 0,
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
        'nb_turns': 0,
        'next_player': 0,
        'on_last_line': False,
        'power': {
            'cost': 10,
            'description': 'Disappear from the board and cannot be targeted by other players.',
            'duration': 2,
            'is_power': True,
            'must_target_player': False,
            'name': 'Night mist',
            'passive': False,
            'trump_cost_delta': 0,
            'trump_names': [
            ]
        },
        'rank': -1,
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
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'is_over': False,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'square': {
                    'x': 6,
                    'y': 7
                }
            },
            '1': {
                'active_trumps': [
                ],
                'square': {
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
            {
                'player_index': 0,
                'player_name': 'Game master',
                'trumps': [
                ]
            },
            {
                'player_index': 1,
                'player_name': 'Player',
                'trumps': [
                ]
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 0,
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
        'nb_turns': 0,
        'next_player': 0,
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
            'trump_cost_delta': 2
        },
        'rank': -1,
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
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'is_over': False,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'square': {
                    'x': 6,
                    'y': 7
                }
            },
            '1': {
                'active_trumps': [
                ],
                'square': {
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
            ],
            'board': {
                'updated_squares': [
                ]
            },
            'is_over': False,
            'players': {
                '0': {
                    'active_trumps': [
                    ],
                    'square': {
                        'x': 6,
                        'y': 7
                    }
                },
                '1': {
                    'active_trumps': [
                    ],
                    'square': {
                        'x': 6,
                        'y': 8
                    }
                }
            },
            'winners': [
            ]
        },
        'player': {
            'request': {
                'active_trumps': [
                    {
                        'player_index': 0,
                        'player_name': 'Game master',
                        'trumps': [
                        ]
                    },
                    {
                        'player_index': 1,
                        'player_name': 'Player',
                        'trumps': [
                        ]
                    }
                ],
                'can_power_be_played': False,
                'elapsed_time': 14,
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
                'nb_turns': 0,
                'next_player': 0,
                'on_last_line': False,
                'power': {
                    'cost': 10,
                    'description': 'Disappear from the board and cannot be targeted by other players.',
                    'duration': 2,
                    'is_power': True,
                    'must_target_player': False,
                    'name': 'Night mist',
                    'passive': False,
                    'trump_cost_delta': 0,
                    'trump_names': [
                    ]
                },
                'rank': -1,
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
            ],
            'board': {
                'updated_squares': [
                ]
            },
            'is_over': False,
            'players': {
                '0': {
                    'active_trumps': [
                    ],
                    'square': {
                        'x': 6,
                        'y': 7
                    }
                },
                '1': {
                    'active_trumps': [
                    ],
                    'square': {
                        'x': 6,
                        'y': 8
                    }
                }
            },
            'winners': [
            ]
        },
        'player': {
            'request': {
                'active_trumps': [
                    {
                        'player_index': 0,
                        'player_name': 'Game master',
                        'trumps': [
                        ]
                    },
                    {
                        'player_index': 1,
                        'player_name': 'Player',
                        'trumps': [
                        ]
                    }
                ],
                'can_power_be_played': False,
                'elapsed_time': 26,
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
                'nb_turns': 0,
                'next_player': 0,
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
                    'trump_cost_delta': 2
                },
                'rank': -1,
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
                'x': 5,
                'y': 7
            },
            {
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
            {
                'player_index': 0,
                'player_name': 'Game master',
                'trumps': [
                ]
            },
            {
                'player_index': 1,
                'player_name': 'Player',
                'trumps': [
                ]
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 93,
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
        'nb_turns': 0,
        'next_player': 0,
        'on_last_line': False,
        'power': {
            'cost': 10,
            'description': 'Disappear from the board and cannot be targeted by other players.',
            'duration': 2,
            'is_power': True,
            'must_target_player': False,
            'name': 'Night mist',
            'passive': False,
            'trump_cost_delta': 0,
            'trump_names': [
            ]
        },
        'rank': -1,
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
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'is_over': False,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'square': {
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'square': {
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
            {
                'player_index': 0,
                'player_name': 'Game master',
                'trumps': [
                ]
            },
            {
                'player_index': 1,
                'player_name': 'Player',
                'trumps': [
                ]
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 93,
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
        'nb_turns': 0,
        'next_player': 0,
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
            'trump_cost_delta': 2
        },
        'rank': -1,
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
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'is_over': False,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'square': {
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'square': {
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
            {
                'player_index': 0,
                'player_name': 'Game master',
                'trumps': [
                ]
            },
            {
                'player_index': 1,
                'player_name': 'Player',
                'trumps': [
                ]
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 0,
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
        'nb_turns': 0,
        'next_player': 1,
        'on_last_line': False,
        'power': {
            'cost': 10,
            'description': 'Disappear from the board and cannot be targeted by other players.',
            'duration': 2,
            'is_power': True,
            'must_target_player': False,
            'name': 'Night mist',
            'passive': False,
            'trump_cost_delta': 0,
            'trump_names': [
            ]
        },
        'rank': -1,
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
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'is_over': False,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'square': {
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'square': {
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
            {
                'player_index': 0,
                'player_name': 'Game master',
                'trumps': [
                ]
            },
            {
                'player_index': 1,
                'player_name': 'Player',
                'trumps': [
                ]
            }
        ],
        'can_power_be_played': True,
        'elapsed_time': 0,
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
        'nb_turns': 0,
        'next_player': 1,
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
            'trump_cost_delta': 2
        },
        'rank': -1,
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
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'is_over': False,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'square': {
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'square': {
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
            {
                'player_index': 0,
                'player_name': 'Game master',
                'trumps': [
                ]
            },
            {
                'player_index': 1,
                'player_name': 'Player',
                'trumps': [
                ]
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 0,
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
        'nb_turns': 1,
        'next_player': 0,
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
            'trump_cost_delta': 2
        },
        'rank': -1,
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
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'is_over': False,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'square': {
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'square': {
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
            {
                'player_index': 0,
                'player_name': 'Game master',
                'trumps': [
                ]
            },
            {
                'player_index': 1,
                'player_name': 'Player',
                'trumps': [
                ]
            }
        ],
        'can_power_be_played': False,
        'elapsed_time': 0,
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
        'nb_turns': 1,
        'next_player': 0,
        'on_last_line': False,
        'power': {
            'cost': 10,
            'description': 'Disappear from the board and cannot be targeted by other players.',
            'duration': 2,
            'is_power': True,
            'must_target_player': False,
            'name': 'Night mist',
            'passive': False,
            'trump_cost_delta': 0,
            'trump_names': [
            ]
        },
        'rank': -1,
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
        ],
        'board': {
            'updated_squares': [
            ]
        },
        'is_over': False,
        'players': {
            '0': {
                'active_trumps': [
                ],
                'square': {
                    'x': 5,
                    'y': 8
                }
            },
            '1': {
                'active_trumps': [
                ],
                'square': {
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
