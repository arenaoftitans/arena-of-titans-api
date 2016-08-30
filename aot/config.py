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

    def load_config(self, type):
        with open('config/config.{type}.toml'.format(type=type), 'r') as config_file:
            self._config = toml.load(config_file)


config = Config()
