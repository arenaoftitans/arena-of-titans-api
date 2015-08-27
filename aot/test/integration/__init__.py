import asyncio
import json
import websockets

import aot
from aot.api.utils import RequestTypes


def get_request(request_type):
    with open('doc/api/requests/{}.json'.format(request_type)) as request_file:
        return request_file.read().encode('utf-8')


def get_response(request_type):
    with open('doc/api/responses/{}.json'.format(request_type)) as response_file:
        return json.load(response_file)


class PlayerWs:
    def __init__(self):
        self.recieve_index = 1
        self.number_asked = 0
        self.game_id = None

    @asyncio.coroutine
    def connect(self):
        ws_endpoint = 'ws://{host}:{port}'.format(
            host=aot.config['api']['host'],
            port=aot.config['api']['ws_port'])
        self.ws = yield from websockets.connect(ws_endpoint)

    @asyncio.coroutine
    def send(self, request_name, increment=True):
        message = get_request(request_name)
        if increment:
            self.recieve_index += 1
        yield from self.ws.send(message)

    @asyncio.coroutine
    def recv(self, response_name=None):
        for i in range(self.number_asked, self.recieve_index):
            self.number_asked += 1
            resp = yield from self.ws.recv()
            resp = json.loads(resp)
            if resp['rt'] == RequestTypes.GAME_INITIALIZED.value:
                self.game_id = resp['game_id']

        if response_name:
            expected_response = get_response(response_name)
        else:
            expected_response = None

        return resp, expected_response

    @asyncio.coroutine
    def close(self):
        yield from self.ws.close()
