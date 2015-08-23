import json
import pytest

from aot.api import get_board
from aot.api import new_id


class MockRequest:
    def __init__(self):
        self.match_info = {}


@pytest.mark.asyncio
def test_get_board():
    request = MockRequest()
    request.match_info['name'] = 'standard'
    resp = yield from get_board(request)
    assert resp.headers['Content-Type'] == 'image/svg+xml; charset=utf-8'
    assert len(resp.text) > 1
    resp2 = yield from get_board(request)
    assert resp.text == resp2.text
