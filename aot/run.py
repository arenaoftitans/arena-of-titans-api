################################################################################
# Copyright (C) 2017 by Arena of Titans Contributors.
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

import asyncio
import logging
import os
import shutil
import sys

import daiquiri
from autobahn.asyncio.websocket import WebSocketServerFactory
from daiquiri_rollbar import RollbarOutput

from .api import Api
from .config import config


# Amount of time to wait for pending futures before forcing them to shutdown.
CLEANUP_TIMEOUT = 5


def setup_logging(debug=False):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    outputs = (
        'stderr',
    )

    if config['rollbar']['access_token'] is None:
        print(  # noqa: T001
            'Note: not loading rollbar, no access_token found.',
            file=sys.stderr,
        )
    else:
        rollbar_output = RollbarOutput(
            access_token=config['rollbar']['access_token'],
            environment=config['env'],
            level=config['rollbar']['level'],
        )
        outputs = (*outputs, rollbar_output)

    daiquiri.setup(level=level, outputs=outputs)


def startup(debug=False, debug_aio=False):
    loop = asyncio.get_event_loop()
    loop.set_debug(debug_aio)

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
        # Leave tasks a chance to complete.
        pending = asyncio.Task.all_tasks()
        if len(pending) > 0:
            loop.run_until_complete(asyncio.wait(pending, timeout=CLEANUP_TIMEOUT))
        # Quit all.
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    socket = config['api'].get('socket', None)
    if socket:
        try:
            os.remove(socket)
        except FileNotFoundError:
            pass
