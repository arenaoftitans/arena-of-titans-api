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
import sys

import daiquiri
import sentry_sdk
from autobahn.asyncio.websocket import WebSocketServerFactory
from sentry_sdk.integrations.logging import LoggingIntegration

from .api.ws import AotWs
from .config import config

logger = daiquiri.getLogger(__name__)


def setup_logging(debug=False):
    if debug:
        level = logging.DEBUG
    elif config["log"]["level"]:
        level = getattr(logging, config["log"]["level"], logging.DEBUG)
    else:
        level = logging.INFO

    if config["sentry_dsn"] is None:
        print(  # noqa: T001
            "Note: not loading sentry, no dsn configured.",
            file=sys.stderr,
        )
    else:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.WARNING,  # Send warnings as events
        )
        sentry_sdk.init(
            config["sentry_dsn"],
            release=config["version"],
            environment=config["env"],
            integrations=[sentry_logging],
        )

    outputs = ("stderr",)

    daiquiri.setup(level=level, outputs=outputs)
    level_name = logging.getLevelName(level)
    logger.info(f"Logging configured with level: {level_name} and ouputs: {outputs}")


def startup(debug=False, debug_aio=False):
    loop = asyncio.get_event_loop()
    loop.set_debug(debug_aio)

    server = _create_tcp_server(loop)
    wsserver = loop.run_until_complete(server)

    return wsserver, loop


def _create_tcp_server(loop):
    host = config["api"]["host"]
    port = config["api"]["ws_port"]
    ws_endpoint = f"ws://{host}:{port}"
    logger.info(f"API listening to {ws_endpoint}")
    factory = WebSocketServerFactory(ws_endpoint)
    factory.protocol = AotWs
    return loop.create_server(factory, host, port)


def cleanup(wsserver, loop):
    if wsserver is not None:
        wsserver.close()
    if loop is not None:
        # Leave tasks a chance to complete.
        pending = asyncio.Task.all_tasks()
        if len(pending) > 0:
            loop.run_until_complete(asyncio.wait(pending, timeout=config["cleanup_timeout"]))
        # Quit all.
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
