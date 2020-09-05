from src.modules import Log
from src.server import Server

if __name__ == '__main__':
    # Init Log
    log = Log()

    # Start the HTTP Server
    log.info('Starting HTTP Server')
    Server().listen()
