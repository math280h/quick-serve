import logging
from logging.config import fileConfig
from os import path


class Log:
    """Log Module - Handles everything with logging
    :param config: Config Module
    """
    def __init__(self, config) -> None:
        # Init Log Config
        fileConfig(path.join(path.dirname(path.dirname(path.abspath(__file__))), 'log_config.ini'))
        self.logger = logging.getLogger()

        # Define log level
        if config.options.get("General", "ExtendedLogging").lower() in ['true', '0']:
            self.logger.setLevel('DEBUG')
        else:
            self.logger.setLevel('ERROR')

    def info(self, data: str) -> None:
        """Log INFO"""
        self.logger.info(data)

    def error(self, data: str) -> None:
        """Log ERROR"""
        self.logger.error(data)

    def debug(self, data: str) -> None:
        """Log DEBUG"""
        self.logger.debug(data)

    def critical(self, data: str) -> None:
        """Log CRITICAL"""
        self.logger.critical(data)

    def fatal(self, data: str) -> None:
        """Log FATAL"""
        self.logger.fatal(data)
