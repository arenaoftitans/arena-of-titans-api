import sys

from os.path import exists

import toml


class Config:
    CONF_FILE_TEMPLATE = 'config/config.{type}.toml'

    def __init__(self):
        self._config = None

    def __getitem__(self, key):
        if self._config is None:
            raise RuntimeError(
                'Configuration is not loaded. '
                'Call load_config(type) before trying to use the configuration',
            )
        else:
            return self._config[key]

    def load_config(self, type, version='latest'):
        config_path = self.CONF_FILE_TEMPLATE.format(type=type)

        if type == 'dev' and not exists(config_path):
            docker_config_file = self.CONF_FILE_TEMPLATE.format(type='docker')
            # We must not use logging here. We need to load the configuration to configure it.
            print(f'Note: {config_path} not found, using {docker_config_file}', file=sys.stderr)
            config_path = docker_config_file

        with open(config_path, 'r') as config_file:
            self._config = toml.load(config_file)

        self._set_version_in_socket_name('api', version)
        self._set_version_in_socket_name('cache', version)

    def _set_version_in_socket_name(self, section_name, version):
        socket = self._config[section_name].get('socket', None)
        if socket:  # pragma: no cover
            socket = socket.format(version=version)
            self._config[section_name]['socket'] = socket


config = Config()
