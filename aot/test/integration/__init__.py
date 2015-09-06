import asyncio
import json
import websockets

import aot
from aot.api.utils import RequestTypes


def get_request(request_type):
    with open('doc/api/requests/{}.json'.format(request_type)) as request_file:
        return json.load(request_file)


def get_response(request_type):
    with open('doc/api/responses/{}.json'.format(request_type)) as response_file:
        return json.load(response_file)


class PlayerWs:
    def __init__(self, index):
        self.index = index
        self.recieve_index = 1
        self.number_asked = 0
        self._game_id = None

    @asyncio.coroutine
    def connect(self):
        ws_endpoint = 'ws://{host}:{port}'.format(
            host=aot.config['api']['host'],
            port=aot.config['api']['ws_port'])
        self.ws = yield from websockets.connect(ws_endpoint)

    @asyncio.coroutine
    def send(self, request_name, message_override=dict(), increment=True):
        message = get_request(request_name)
        for key, value in message_override.items():
            message[key] = value
        if increment:
            self.recieve_index += 1
        yield from self.ws.send(json.dumps(message).encode('utf-8'))

    @asyncio.coroutine
    def recv(self, response_name=None):
        resp = None
        for i in range(self.number_asked, self.recieve_index):
            self.number_asked += 1
            resp = yield from self.ws.recv()
            # resp can be None
            resp = json.loads(resp) if resp else dict()
            if 'rt' in resp and resp['rt'] == RequestTypes.GAME_INITIALIZED.value:
                self._game_id = resp['game_id']
            # If at this stage, _game_id is still None, something went wrong and resp is most
            # likely an error.
            if self._game_id is None:
                break

        if response_name:
            expected_response = get_response(response_name)
        else:
            expected_response = None

        return resp, expected_response

    @asyncio.coroutine
    def get_game_id(self):
        if self._game_id is None:
            yield from self.recv()
        return self._game_id

    @asyncio.coroutine
    def close(self):
        yield from self.ws.close()
