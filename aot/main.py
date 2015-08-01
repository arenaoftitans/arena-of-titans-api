import asyncio
from aiohttp import web
from autobahn.asyncio.websocket import WebSocketServerFactory

from aot.api import Api
from aot.api import get_board
from aot.api import new_id


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
    factory.protocol = Api
    server = loop.create_server(factory, '127.0.0.1', 9000)
    wsserver = loop.run_until_complete(server)

    webapp = web.Application(loop=loop)
    webapp.router.add_route('GET', '/newId', new_id)
    webapp.router.add_route('GET', '/board/{name}', get_board)
    server = loop.create_server(webapp.make_handler(), '127.0.0.1', 9090)
    httpserver = loop.run_until_complete(server)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        wsserver.close()
        httpserver.close()
        loop.close()
