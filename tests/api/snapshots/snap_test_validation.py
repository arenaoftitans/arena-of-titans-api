# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_validate_invalid_messages[empty_message] 1'] = {
    'request': [
        'required field'
    ],
    'rt': [
        'required field'
    ]
}

snapshots['test_validate_invalid_messages[wrong_request_type] 1'] = {
    'rt': [
        "field 'rt' cannot be coerced: 'TOTO'",
        'must be of request_type type'
    ]
}

snapshots['test_validate_valid_message 1'] = {
    'game_id': 'test',
    'player_id': 'test',
    'test': False
}

snapshots['test_sanitize_empty_player_name[update_slot0] 1'] = {
    'slot': [
        "'player_name' cannot be empty if slot is taken"
    ]
}

snapshots['test_sanitize_empty_player_name[update_slot1] 1'] = {
    'player_name': [
        'empty values not allowed'
    ]
}
