################################################################################
# Copyright (C) 2015-2020 by Last Run Contributors.
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

import os
import sys

from environs import Env

from .utils import make_immutable


class Config:
    ENV_VARS = {
        "API_ALLOW_DEBUG",
        "API_HOST",
        "API_WS_PORT",
        "AI_DELAY",
        "CACHE_HOST",
        "CACHE_PORT",
        "CACHE_SIGN_KEY",
        "CACHE_TIMEOUT",
        "CACHE_TTL",
        "ENV",
        "LOG_LEVEL",
        "SENTRY_DSN",
        "VERSION",
    }

    def __init__(self):
        self._config = None
        self.env = Env()
        self.env.read_env()

        print(  # noqa: T001
            "Using overridden values for",
            self.ENV_VARS.intersection(os.environ.keys()),
            file=sys.stderr,
        )

    def __getitem__(self, value):
        if self._config is None:
            raise RuntimeError("Config is not loaded, cannot access it.")

        return self._config[value]

    def setup_config(self):
        # API must not start in prod like nev if we don't have a sign key for cache.
        # This is for security reasons.
        env = self.env.str("ENV", "production")
        cache_sign_key = self.env.str("CACHE_SIGN_KEY", "")
        if env != "development" and not cache_sign_key:
            raise EnvironmentError("You must supply a CACHE_SIGN_KEY env var")

        self._config = make_immutable(
            {
                "api": {
                    "allow_debug": self.env.bool("API_ALLOW_DEBUG", False),
                    # Binding to all interfaces, bandit don't allow this (#104)
                    "host": self.env.str("API_HOST", "0.0.0.0"),  # noqa: S104
                    "min_elapsed_time_to_consider": 8,  # In seconds.
                    "ws_port": self.env.int("API_WS_PORT", 8181),
                },
                "ai": {"delay": self.env.int("AI_DELAY", 5)},
                "cache": {
                    "host": self.env.str("CACHE_HOST", "127.0.0.1"),
                    "port": self.env.int("CACHE_PORT", 6379),
                    # Sign key must be of type bytes, not str.
                    "sign_key": cache_sign_key.encode("utf-8"),
                    "timeout": self.env.int("CACHE_TIMEOUT", 5),
                    "ttl": self.env.int("CACHE_TTL", 2 * 24 * 60 * 60),  # 2 days
                },
                # Amount of time to wait for pending futures before forcing them to shutdown.
                "cleanup_timeout": self.env.int("CLEANUP_TIMEOUT", 5),
                "env": env,
                "log": {"level": self.env.str("LOG_LEVEL", None)},
                "sentry_dsn": self.env.str("SENTRY_DSN", None),
                "version": self.env.str("VERSION", "latest"),
            }
        )

    @property
    def is_testing(self):
        return self._config["env"] == "pytest"


config = Config()
