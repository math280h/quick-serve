import socket
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

from src.modules import Connection


class Server:
    def __init__(self, config, log):
        self.config = config
        self.log = log

        self.shutdown = False
        signal.signal(signal.SIGINT, self.signal_handler)

        self.host = self.config.options.get("Server", "ListenAddress")
        self.port = int(self.config.options.get("Server", "Port"))
        self.size = int(self.config.options.get("Server", "ByteReadSize"))

        # Bind Socket & set Socket Options
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def signal_handler(self):
        self.log.info("Shutting Down.")
        self.shutdown = True

    def listen(self):
        # Wait for a connection
        self.sock.listen()
        self.log.info('Server is now listening for connections')
        while True:
            # Accept connection
            client, address = self.sock.accept()
            # Split connection into thread
            with ThreadPoolExecutor() as executor:
                if self.shutdown:
                    executor.shutdown(wait=True)
                    sys.exit(0)
                executor.submit(Connection(self.config, self.log, client, address).handle)
