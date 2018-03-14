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
    'CACHE_SIGN_KEY',
    'CACHE_TIMEOUT',
    'CACHE_TTL',
    'ENV',
    'LOG_LEVEL',
    'ROLLBAR_ACCESS_TOKEN',
    'ROLLBAR_LEVEL',
    'VERSION',
}


print(  # noqa: T001
    'Using overridden values for',
    _ENV_VARS.intersection(environ.keys()),
    file=sys.stderr,
)


class Config:
    def __init__(self):
        self._config = None

    def __getitem__(self, value):
        if self._config is None:
            raise RuntimeError('Config is not loaded, cannot access it')

        return self._config[value]

    def setup_config(self):
        # API must not start in prod like nev if we don't have a sign key for cache.
        # This is for security reasons.
        env = environ.get('ENV', 'development')
        cache_sign_key = environ.get('CACHE_SIGN_KEY', '')
        if env != 'development' and not cache_sign_key:
            raise EnvironmentError('You must supply a CACHE_SIGN_KEY env var')

        self._config = MappingProxyType({
            'api': {
                'allow_debug': bool(environ.get('API_ALLOW_DEBUG', False)),
                # Binding to all interfaces, bandit don't allow this (#104)
                'host': environ.get('API_HOST', '0.0.0.0'),  # noqa: B104
                'ws_port': int(environ.get('API_WS_PORT', 8181)),
            },
            'cache': {
                'host': environ.get('CACHE_HOST', 'aot-redis'),
                'port': int(environ.get('CACHE_PORT', 6379)),
                # Sign key must be of type bytes, not str.
                'sign_key': cache_sign_key.encode('utf-8'),
                'timeout': int(environ.get('CACHE_TIMEOUT', 5)),
                'ttl': int(environ.get('CACHE_TTL', 2 * 24 * 60 * 60)),  # 2 days
            },
            # Amount of time to wait for pending futures before forcing them to shutdown.
            'cleanup_timeout': int(environ.get('CLEANUP_TIMEOUT', 5)),
            'env': env,
            'log': {
                'level': environ.get('LOG_LEVEL', None),
            },
            'rollbar': {
                'access_token': environ.get('ROLLBAR_ACCESS_TOKEN', None),
                'level': int(environ.get('ROLLBAR_LEVEL', 30)),
            },
            'version': environ.get('VERSION', 'latest'),
        })


config = Config()
