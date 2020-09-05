import logging
from logging.config import fileConfig
from os import path
from src.modules.config import Config


class Log:
    def __init__(self):
        # Init Log Config
        fileConfig(path.join(path.dirname(path.dirname(path.abspath(__file__))), 'log_config.ini'))
        self.logger = logging.getLogger()

        if Config().options.get("General", "ExtendedLogging").lower() in ['true', '0']:
            self.logger.setLevel('DEBUG')

    def info(self, data):
        self.logger.info(data)

    def error(self, data):
        self.logger.error(data)

    def debug(self, data):
        self.logger.debug(data)