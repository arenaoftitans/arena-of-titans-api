import asyncio
import json
import websockets

import aot


def get_request(request_type):
    with open('doc/api/requests/{}.json'.format(request_type)) as request_file:
        return request_file.read().encode('utf-8')


def get_response(request_type):
    with open('doc/api/responses/{}.json'.format(request_type)) as response_file:
        return json.load(response_file)


class PlayerWs:
    def __init__(self):
        self.recieve_index = 1

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
    def recv(self, response_name):
        for i in range(self.recieve_index):
            resp = yield from self.ws.recv()
        return json.loads(resp), get_response(response_name)

    @asyncio.coroutine
    def close(self):
        yield from self.ws.close()
