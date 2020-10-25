import socket
import signal
import sys
import asyncio
from diskcache import Cache

from quick_serve.modules import Connection


class Server:
    """Server, the main component that handles listening for connections and accepting them
    :param config: Configuration Class
    :param log: Log Class
    """
    def __init__(self, config, log) -> None:
        # Define Config, Log & Cache
        self.config = config
        self.log = log
        self.cache = Cache()

        # Stores bool about if the system is trying to shut down
        self.shutdown = False
        # Listen for SIGINT
        signal.signal(signal.SIGINT, self.signal_handler)

        # Get host, port & read size from the Config
        self.host = self.config.options.get("Server", "ListenAddress")
        self.port = int(self.config.options.get("Server", "Port"))
        self.size = int(self.config.options.get("Server", "ByteReadSize"))

        # Bind Socket & set Socket Options
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def signal_handler(self, sig: int, frame: any) -> None:
        """Handles SIGINT and other signals.

        :param sig: Signal Value
        :param frame: Signal Frame
        """
        # If SIG is SIGINT - Shut down the server
        if sig == 2:
            self.log.info("Shutting Down... Frame: " + frame.f_code.co_name)
            self.shutdown = True
            self.sock.close()
            sys.exit(0)

    async def listen(self) -> None:
        """Listen for Connections"""
        # Wait for a connection
        self.sock.listen()
        self.log.info('Server is now listening for connections')
        # While we are listening for connections
        while True:
            # Accept connection if any
            try:
                client, address = self.sock.accept()
            except OSError as e:
                # Shutdown System
                if self.shutdown:
                    self.log.debug("Closing Socket...")
                    return
                else:
                    # System appeared to crash
                    self.log.fatal("OSError Panic! Closing Socket... - {}".format(e))
                    self.sock.close()
                    sys.exit(0)

            # Create a task for the connection
            await asyncio.create_task(Connection(self.config, self.log, client, address, self.cache).handle())
