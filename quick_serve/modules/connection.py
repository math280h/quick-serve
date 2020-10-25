from io import BytesIO

from quick_serve.modules.parser import Parser
from quick_serve.modules.methods import Methods
from quick_serve.modules.messenger import Messenger
from quick_serve.modules.request import Request


class Connection:
    """Connection Handler - This is responsible for handling connections after accept

    :param config: Config Module
    :param log: Log Module
    :param conn: Active Socket Connection
    :param address: Client Object
    :param cache: Cache Module
    """
    def __init__(self, config, log, conn, address, cache) -> None:
        # Define Connection & Client Parameters
        self.conn = conn
        self.address = address

        # Define Modules
        self.log = log
        self.config = config
        self.parser = Parser(config)
        self.messenger = Messenger(config, log, conn)
        self.methods = Methods(config)
        self.request = Request(config, log, conn, address, cache)

    async def wait_for_request(self, buffer: any) -> None:
        state = ""
        while True:
            try:
                # Try to receive data
                req = self.conn.recv(int(self.config.options.get("Server", "ByteReadSize")))
            except (BlockingIOError, ConnectionAbortedError, ConnectionResetError) as e:
                self.log.debug('Connection was closed by client: {}'.format(e))
                break
            if not req:
                break

            if state == 'BODY_INCOMPLETE':
                # Some of the body was missing from last request so read the next part as body
                self.log.debug("Parsing Body")
                state = self.parser.parse_request(req, headers_ok=True)
                buffer.write(req)
            else:
                # We don't know anything about the last request so try to parse it
                self.log.debug("Parsing Request")
                state = self.parser.parse_request(req)
                buffer.write(req)
            if state == 'DONE' or state == 'NO_BODY' or state == 'INVALID_CONTENT_LENGTH':
                # We reached a finish state, close buffer.
                self.log.debug("Done Parsing")
                break

    async def handle(self) -> None:
        """Handle the Connection"""
        self.log.info('Accepted connection from: {}'.format(self.address[0]))

        # Create a buffer for data and wait for all the data to be read
        with BytesIO() as buffer:
            self.log.debug("Collecting data in buffer")
            # While the buffer is open

            await self.wait_for_request(buffer)

            data, body, end_of_headers = await self.parser.parse_buffer(buffer)

            # Check if we received a method
            try:
                method = data[0]
            except IndexError:
                await self.messenger.send_headers("400 Bad Request")
                self.conn.close()
                return

            # Check if the method is allowed
            if not self.methods.is_allowed(method):
                await self.messenger.send_headers("405 Method Not Allowed")
                self.conn.close()
                return

            # Dependent on the request method, handle it
            await self.request.handle_request(method, data)

            # Close connection when we have finished handling the request
            self.log.debug("Closing Connection with: {}".format(self.address[0]))
            self.conn.close()
            return
