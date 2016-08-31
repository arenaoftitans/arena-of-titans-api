import toml


class Config:
    def __init__(self):
        self._config = None

    def __getitem__(self, key):
        if self._config is None:
            raise RuntimeError(
                'Configuration is not loaded. '
                'Call load_config(type) before trying to use the coniguration'
            )
        else:
            return self._config[key]

    def load_config(self, type, version='latest'):
        with open('config/config.{type}.toml'.format(type=type), 'r') as config_file:
            self._config = toml.load(config_file)

        self._set_version_in_socket_name('api', version)
        self._set_version_in_socket_name('cache', version)

    def _set_version_in_socket_name(self, section_name, version):
        socket = self._config[section_name].get('socket', None)
        if socket:
            socket = socket.format(version=version)
            self._config[section_name]['socket'] = socket


config = Config()
