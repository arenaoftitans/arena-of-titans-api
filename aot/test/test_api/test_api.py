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


@pytest.mark.asyncio
def test_new_id():
    request = MockRequest()
    resp = yield from new_id(request)
    id = json.loads(resp.text)
    assert resp.headers['Content-Type'] == 'application/json'
    assert len(id['id']) > 1
    resp = yield from new_id(request)
    id2 = json.loads(resp.text)
    assert id != id2
