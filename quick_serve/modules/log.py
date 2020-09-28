import logging
from logging.config import fileConfig
from os import path


class Log:
    """Log Module - Handles everything with logging
    :param config: Config Module
    """
    def __init__(self, config):
        # Init Log Config
        fileConfig(path.join(path.dirname(path.dirname(path.abspath(__file__))), 'log_config.ini'))
        self.logger = logging.getLogger()

        # Define log level
        if config.options.get("General", "ExtendedLogging").lower() in ['true', '0']:
            self.logger.setLevel('DEBUG')
        else:
            self.logger.setLevel('ERROR')

    def info(self, data):
        """Log INFO"""
        self.logger.info(data)

    def error(self, data):
        """Log ERROR"""
        self.logger.error(data)

    def debug(self, data):
        """Log DEBUG"""
        self.logger.debug(data)

    def critical(self, data):
        """Log CRITICAL"""
        self.logger.critical(data)

    def fatal(self, data):
        """Log FATAL"""
        self.logger.fatal(data)
