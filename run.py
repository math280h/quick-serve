import asyncio

from quick_serve.modules import Log
from quick_serve.modules import Config
from quick_serve.server import Server


class QuickServe:
    """Main Application"""
    def __init__(self):
        """Run the application"""
        # Init Config
        config = Config()

        # Init Log
        log = Log(config)

        # Start the HTTP Server
        log.info('Starting HTTP Server')
        asyncio.run(Server(config, log).listen())


if __name__ == '__main__':
    QuickServe()
