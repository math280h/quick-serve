import asyncio

from src.modules import Log
from src.modules import Config
from src.server import Server


class QuickServe:
    def __init__(self):
        # Init Config
        config = Config()

        # Init Log
        log = Log(config)

        # Start the HTTP Server
        log.info('Starting HTTP Server')
        asyncio.run(Server(config, log).listen())


if __name__ == '__main__':
    QuickServe()
