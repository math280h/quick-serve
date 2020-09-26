import socket
import signal
import sys
import asyncio
from diskcache import Cache

from quick_serve.modules import Connection


class Server:
    def __init__(self, config, log):
        self.config = config
        self.log = log
        self.cache = Cache()

        self.shutdown = False
        signal.signal(signal.SIGINT, self.signal_handler)

        self.host = self.config.options.get("Server", "ListenAddress")
        self.port = int(self.config.options.get("Server", "Port"))
        self.size = int(self.config.options.get("Server", "ByteReadSize"))

        # Bind Socket & set Socket Options
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def signal_handler(self, sig, frame):
        if sig == 2:
            self.log.info("Shutting Down.")
            self.shutdown = True
            self.sock.close()
            sys.exit(0)

    async def listen(self):
        # Wait for a connection
        self.sock.listen()
        self.log.info('Server is now listening for connections')
        while True:
            # Accept connection
            try:
                client, address = self.sock.accept()
            except OSError as e:
                if self.shutdown:
                    self.log.debug("Closing Socket...")
                    return
                else:
                    self.log.fatal("OSError Panic! Closing Socket... - {}".format(e))
                    self.sock.close()
                    sys.exit(0)

            # Create a task for the connection
            await asyncio.create_task(Connection(self.config, self.log, client, address, self.cache).handle())
