################################################################################
# Copyright (C) 2015-2018 by Arena of Titans Contributors.
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

import sys
from os import environ
from types import MappingProxyType

from dotenv import (
    find_dotenv,
    load_dotenv,
)


load_dotenv(find_dotenv())


_ENV_VARS = {
    'API_ALLOW_DEBUG',
    'API_HOST',
    'API_WS_PORT',
    'CACHE_HOST',
    'CACHE_PORT',
    'CACHE_TTL',
    'ENV',
    'ROLLBAR_ACCESS_TOKEN',
    'ROLLBAR_LEVEL',
    'VERSION',
}


print(  # noqa: T001
    'Using overridden values for',
    _ENV_VARS.intersection(environ.keys()),
    file=sys.stderr,
)


config = MappingProxyType({
    'api': {
        'allow_debug': environ.get('API_ALLOW_DEBUG', False),
        'host': environ.get('API_HOST', '0.0.0.0'),  # noqa: B104 (Binding to all interfaces)
        'ws_port': environ.get('API_WS_PORT', 8181),
    },
    'cache': {
        'host': environ.get('CACHE_HOST', 'aot-redis'),
        'port': environ.get('CACHE_PORT', 6379),
        'ttl': environ.get('CACHE_TTL', 2 * 24 * 60 * 60),  # 2 days
    },
    # Amount of time to wait for pending futures before forcing them to shutdown.
    'cleanup_timeout': environ.get('CLEANUP_TIMEOUT', 5),
    'env': environ.get('ENV', 'development'),
    'rollbar': {
        'access_token': environ.get('ROLLBAR_ACCESS_TOKEN', None),
        'level': environ.get('ROLLBAR_LEVEL', 30),
    },
    'version': environ.get('VERSION', 'latest'),
})
