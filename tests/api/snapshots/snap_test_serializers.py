# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_serialize_actions[trump_played] 1'] = {
    'card': None,
    'description': 'played_trump',
    'initiator': {
        'index': 0,
        'name': 'Player 0'
    },
    'special_action': None,
    'target': {
        'index': 0,
        'name': 'Player 0'
    },
    'trump': {
        'apply_on_initiator': False,
        'color': None,
        'colors': [
        ],
        'cost': 8,
        'delta_moves': 1,
        'description': 'Allow the player to play one more move.',
        'duration': 1,
        'is_player_visible': True,
        'must_target_player': False,
        'name': 'Reinforcements',
        'prevent_trumps_to_modify': [
        ],
        'require_square_target': False
    }
}

snapshots['test_serialize_actions[power_played] 1'] = {
    'card': None,
    'description': 'played_trump',
    'initiator': {
        'index': 0,
        'name': 'Player 0'
    },
    'special_action': None,
    'target': {
        'index': 0,
        'name': 'Player 0'
    },
    'trump': {
        'card_names': [
            'Knight'
        ],
        'colors': [
            'ALL'
        ],
        'cost': 0,
        'description': 'Your knights can move on any colors',
        'must_target_player': False,
        'name': 'Inveterate Ride',
        'passive': True,
        'require_square_target': False,
        'trump_cost_delta': 2
    }
}

snapshots['test_serialize_actions[special_action] 1'] = {
    'card': None,
    'description': 'played_trump',
    'initiator': {
        'index': 0,
        'name': 'Player 0'
    },
    'special_action': {
        'color': 'YELLOW',
        'cost': 0,
        'description': 'Allow you to move back another player.',
        'distance': 1,
        'duration': 0,
        'must_target_player': True,
        'name': 'Assassination'
    },
    'target': {
        'index': 0,
        'name': 'Player 0'
    },
    'trump': None
}
