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
import logging

from .reload import run_reload
from .run import (
    cleanup,
    setup_config,
    setup_logging,
    startup,
)


def main(debug=False, type='prod', version='latest'):
    setup_config(type=type, version=version)
    setup_logging(debug=debug)

    wsserver, loop = None, None

    try:
        logging.info('API is starting')
        cleanup(None, None)
        wsserver, loop = startup(debug=debug)
        logging.info('API is ready')
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup(wsserver, loop)


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
    parser.add_argument(
        '--reload',
        help='Start the API in development mode and reload it on each modification',
        dest='reload',
        action='store_true',
    )
    args = parser.parse_args()

    if args.reload:
        run_reload()
    else:
        main(debug=args.debug, version=args.version, type=args.type)
