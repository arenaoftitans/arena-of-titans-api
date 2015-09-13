import pytest
import requests

import aot
from aot.api import get_board


class MockRequest:
    def __init__(self):
        self.match_info = {}


@pytest.mark.asyncio
def test_get_board():
    request = MockRequest()
    request.match_info['name'] = 'standard'
    url = 'http://{host}:{port}/board/{name}'\
        .format(
            host=aot.config['api']['host'],
            port=aot.config['api']['http_port'],
            name='standard')

    resp = requests.get(url)
    assert resp.headers['Content-Type'] == 'image/svg+xml; charset=utf-8'
    assert len(resp.text) > 1
    resp2 = yield from get_board(request)
    assert resp.text == resp2.text
