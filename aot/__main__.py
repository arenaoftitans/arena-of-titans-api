################################################################################
# Copyright (C) 2015-2016 by Arena of Titans Contributors.
#
# This file is part of Arena of Titans.
#
# Arena of Titans is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Arena of Titans is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
################################################################################

import argparse
import asyncio
import logging
import os
import shutil
from autobahn.asyncio.websocket import WebSocketServerFactory

import aot
from aot.api import Api

try:
    import uwsgi  # noqa
    on_uwsgi = True
except ImportError:
    on_uwsgi = False


def main(debug=False, socket_id=''):
    wsserver, loop = None, None

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    try:
        wsserver, loop = startup(debug=debug, socket_id=socket_id)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup(wsserver, loop)


def startup(debug=False, socket_id=''):
    loop = asyncio.get_event_loop()
    loop.set_debug(debug)

    socket = aot.config['api'].get('socket', None)
    if socket:
        socket = socket.replace('$1', socket_id)
        server = _create_unix_server(loop, socket)
    else:
        server = _create_tcp_server(loop)

    wsserver = loop.run_until_complete(server)
    if socket:
        _correct_permissions_unix_server(socket)

    return wsserver, loop


def _create_unix_server(loop, socket):
    factory = WebSocketServerFactory(None)
    factory.protocol = Api
    server = loop.create_unix_server(factory, socket)

    return server


def _correct_permissions_unix_server(socket):
    os.chmod(socket, 0o660)
    try:
        shutil.chown(socket, group=aot.config['api']['socket_group'])
    except PermissionError as e:
        logging.exception(e)


def _create_tcp_server(loop):
    host = aot.config['api']['host']
    ws_endpoint = 'ws://{host}:{port}'.format(
        host=host,
        port=aot.config['api']['ws_port'])
    factory = WebSocketServerFactory(ws_endpoint)
    factory.protocol = Api
    return loop.create_server(factory, host, aot.config['api']['ws_port'])


def cleanup(wsserver, loop):
    if wsserver is not None:
        wsserver.close()
    if loop is not None:
        loop.close()
    try:
        os.remove(aot.config['api']['socket'])
    except FileNotFoundError:
        pass


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(description='Start the AoT API')
    parser.add_argument(
        '--debug',
        help='Start in debug mode',
        action='store_true',
    )
    parser.add_argument(
        '--socket-id',
        help='Id of the unix socket',
        dest='socket_id',
        default='',
    )
    args = parser.parse_args()

    main(debug=args.debug, socket_id=args.socket_id)
