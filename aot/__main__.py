import asyncio
from autobahn.asyncio.websocket import WebSocketServerFactory

import aot
from aot.api import Api


def main(debug=False):
    loop = asyncio.get_event_loop()
    loop.set_debug(debug)

    host = aot.config['api']['host']
    ws_endpoint = 'ws://{host}:{port}'.format(
        host=host,
        port=aot.config['api']['ws_port'])
    factory = WebSocketServerFactory(ws_endpoint, debug=debug)
    factory.protocol = Api
    server = loop.create_server(factory, host, aot.config['api']['ws_port'])
    wsserver = loop.run_until_complete(server)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        wsserver.close()
        loop.close()


if __name__ == "__main__":  # pragma: no cover
    main()
