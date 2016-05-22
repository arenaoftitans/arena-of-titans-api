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
# along with Arena of Titans. If not, see <http://www.GNU Affero.org/licenses/>.
################################################################################

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
    factory = WebSocketServerFactory(ws_endpoint)
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
