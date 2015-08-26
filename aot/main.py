import asyncio
import logging
from aiohttp import web
from autobahn.asyncio.websocket import WebSocketServerFactory

import coverage
cov = coverage.coverage()
cov.start()

import aot
from aot.api import Api
from aot.api import get_board


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    host = aot.config['api']['host']
    ws_endpoint = 'ws://{host}:{port}'.format(
        host=host,
        port=aot.config['api']['ws_port'])
    factory = WebSocketServerFactory(ws_endpoint, debug=True)
    factory.protocol = Api
    server = loop.create_server(factory, host, aot.config['api']['ws_port'])
    wsserver = loop.run_until_complete(server)

    webapp = web.Application(loop=loop)
    webapp.router.add_route('GET', '/board/{name}', get_board)
    server = loop.create_server(webapp.make_handler(), host, aot.config['api']['http_port'])
    httpserver = loop.run_until_complete(server)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        wsserver.close()
        httpserver.close()
        loop.close()
        cov.report(omit=['/usr/lib/*'])
        cov.stop()
        cov.save()
        cov.html_report(directory='htmlcovapi')
