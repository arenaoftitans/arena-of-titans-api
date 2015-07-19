import asyncio
from autobahn.asyncio.websocket import WebSocketServerFactory
from aot.api import Api


def list_opt():
    """Do some operations on list"""
    # get the 1st number > 100
    a = [12, 34, 89, 700]
    b = [n for n in a if n > 100][0]
    print(b)
    # Multiply all number by 2
    print([n*2 for n in a])
    # Mulitply number > 100  by 3
    print([n*3 for n in a if n > 100])


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
