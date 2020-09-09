from src.modules import Log
from src.modules import Config
from src.server import Server

if __name__ == '__main__':
    # Init Config
    config = Config()

    # Init Log
    log = Log(config)

    # Start the HTTP Server
    log.info('Starting HTTP Server')
    Server(config, log).listen()
