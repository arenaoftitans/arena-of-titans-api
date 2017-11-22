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
import configparser
import json
import logging
import os
import shutil
import sys

import daiquiri
from autobahn.asyncio.websocket import WebSocketServerFactory
from daiquiri_rollbar import RollbarOutput

from .api import Api
from .config import config

try:
    import uwsgi  # noqa
    on_uwsgi = True
except ImportError:
    on_uwsgi = False


def setup_config(type='prod', version='latest'):
    # We cannot pass arguments to the uwsgi entry point.
    # So we store the values in the configuration.
    if on_uwsgi:
        uwsgi_config = configparser.ConfigParser()
        uwsgi_config.read('/etc/uwsgi.d/aot-api.ini')
        type = uwsgi_config['aot']['type']
        version = uwsgi_config['aot']['version']

    config.load_config(type, version)


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

    if config['api'].get('rollbar_enabled', False) and \
            os.path.exists(config['api'].get('rollbar_config', None)):
        with open(config['api']['rollbar_config'], 'r') as rollbar_file:
            rollbar_config = json.load(rollbar_file)
            rollbar_config = rollbar_config[config['type']]['api']
        rollbar_output = RollbarOutput(**rollbar_config)
        outputs = (*outputs, rollbar_output)
    else:
        print(
            'Note: not loading rollbar',
            'Enabled: {}'.format(config['api'].get('rollbar_enabled', False)),
            'Config file: {}'.format(config['api'].get('rollbar_config', None)),
            file=sys.stderr,
        )

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
        loop.close()

    socket = config['api'].get('socket', None)
    if socket:
        try:
            os.remove(socket)
        except FileNotFoundError:
            pass
