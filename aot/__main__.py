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
import configparser
import daiquiri
import logging
import os
import shutil
from autobahn.asyncio.websocket import WebSocketServerFactory

from aot.api import Api
from aot.config import config

try:
    import uwsgi  # noqa
    on_uwsgi = True
except ImportError:
    on_uwsgi = False


def main(debug=False, type='prod', version='latest'):
    config.load_config(type, version)
    setup_logging(debug=debug)

    wsserver, loop = None, None
    # We can pass arguments to the uwsgi entry point so we store the values in the configuration.
    if on_uwsgi:
        uwsgi_config = configparser.ConfigParser()
        uwsgi_config.read('/etc/uwsgi.d/aot-api.ini')
        type = uwsgi_config['aot']['type']
        version = uwsgi_config['aot']['version']

    try:
        cleanup(None, None)
        wsserver, loop = startup(debug=debug)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup(wsserver, loop)


def setup_logging(debug=False):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    log_file = config['api']['log_file']
    logs_dir = os.path.dirname(log_file)
    os.makedirs(logs_dir, exist_ok=True)
    outputs = (
        'stderr',
        daiquiri.output.File(log_file),
    )
    daiquiri.setup(level=level, outputs=outputs)


def startup(debug=False):
    loop = asyncio.get_event_loop()
    loop.set_debug(debug)

    socket = config['api'].get('socket', None)
    if socket:
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
        shutil.chown(socket, group=config['api']['socket_group'])
    except (PermissionError, LookupError) as e:
        logging.exception(e)


def _create_tcp_server(loop):
    host = config['api']['host']
    port = config['api']['ws_port']
    ws_endpoint = f'ws://{host}:{port}'
    factory = WebSocketServerFactory(ws_endpoint)
    factory.protocol = Api
    return loop.create_server(factory, host, port)


def cleanup(wsserver, loop):
    if wsserver is not None:
        wsserver.close()
    if loop is not None:
        loop.close()

    socket = config['api'].get('socket', None)
    if socket:
        try:
            os.remove(socket)
        except FileNotFoundError:
            pass


if __name__ == '__main__':  # pragma: no cover
    parser = argparse.ArgumentParser(description='Start the AoT API')
    parser.add_argument(
        '--debug',
        help='Start in debug mode',
        action='store_true',
    )
    parser.add_argument(
        '--version',
        help='Version of the API being deployed',
        dest='version',
        default='latest',
    )
    parser.add_argument(
        '--type',
        help='The type of deployment',
        dest='type',
        default='dev',
        choices=['prod', 'dev', 'testing', 'staging'],
    )
    args = parser.parse_args()

    main(debug=args.debug, version=args.version, type=args.type)
