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
