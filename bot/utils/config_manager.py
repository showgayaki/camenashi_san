from utils.config_loader import load_config


class ConfigManager:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._config = load_config()
        return cls._instance

    @property
    def config(self):
        return self._config
