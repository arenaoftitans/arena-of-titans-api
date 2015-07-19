import asyncio
from autobahn.asyncio.websocket import WebSocketServerFactory

from aot.api import Api


if __name__ == "__main__":
    list_opt()

    factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
    factory.protocol = Api

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 9000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
