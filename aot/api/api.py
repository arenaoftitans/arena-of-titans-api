import json
import pickle
from autobahn.asyncio.websocket import WebSocketServerProtocol
import redis
from aot.game import Game
from aot.board import Square


class Api(WebSocketServerProtocol):
    _redis = redis.Redis()
    _clients = {}

    def onOpen(self):
        Api._clients[self._wskey] = self
        game = Game()
        self._save_game(game)

    def onMessage(self, payload, isBinary):
        game = self._load_game()
        msg = json.loads(payload.decode('utf-8'))
        response = {}
        if msg['type'] == 'create':
            game.create(msg['value'])
            response['type'] = 'create'
            response['value'] = True
        elif msg['type'] == 'view':
            card = self._get_card(msg)
            response['type'] = 'view'
            response['value'] = game.view_possible_squares(card)
        elif msg['type'] == 'play':
            coords = [int(c.strip()) for c in msg['coords'].split(',')]
            card = self._get_card(msg)
            response['type'] = 'play'
            response['value'] = game.play(card, coords)

        self._save_game(game)
        Api._clients[self._wskey].sendMessage(
            json.dumps(response, default=to_json).encode('utf-8'), False
        )

    def onClose(self, wasClean, code, reason):
        del Api._clients[self._wskey]

    def _save_game(self, game):
        Api._redis.set('python-game', pickle.dumps(game))

    def _load_game(self):
        return pickle.loads(Api._redis.get('python-game'))

    def _get_card(self, msg):
        if 'value' in msg:
            card = msg['value']
        else:
            card = msg['card']
        color, name = card.split('_')
        color = color.lower()
        name = name.lower().title()
        return name, color


def to_json(python_object):
    if isinstance(python_object, set):
        return list(python_object)
    elif isinstance(python_object, Square):
        return {'__class__': 'square',
                'x': python_object.x,
                'y':  python_object.y
                }
    raise TypeError(repr(python_object) + ' is not JSON serializable')
