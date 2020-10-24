from io import BytesIO

from quick_serve.modules.parser import Parser
from quick_serve.modules.methods import Methods
from quick_serve.modules.messenger import Messenger
from quick_serve.modules.resource import Resource


class Connection:
    """Connection Handler - This is responsible for handling connections after accept

    :param config: Config Module
    :param log: Log Module
    :param conn: Active Socket Connection
    :param address: Client Object
    :param cache: Cache Module
    """
    def __init__(self, config, log, conn, address, cache):
        # Define Connection & Client Parameters
        self.conn = conn
        self.address = address

        # Define Modules
        self.log = log
        self.config = config
        self.parser = Parser(config)
        self.messenger = Messenger(config, log, conn)
        self.resource = Resource(config, log, cache)
        self.methods = Methods(config)

    async def handle(self):
        """Handle the Connection"""
        self.log.info('Accepted connection from: {}'.format(self.address[0]))
        # Set current state as none
        state = ''
        # Create a buffer for data and wait for all the data to be read
        with BytesIO() as buffer:
            self.log.debug("Collecting data in buffer")
            # While the buffer is open
            while True:
                try:
                    # Try to recieve data
                    req = self.conn.recv(int(self.config.options.get("Server", "ByteReadSize")))
                except (BlockingIOError, ConnectionAbortedError, ConnectionResetError) as e:
                    self.log.debug('Connection was closed by client: {}'.format(e))
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

            # Point Buffer to the start
            buffer.seek(0)
            # Holds if we read all headers
            end_of_headers = False
            # Request Data
            data = []
            # Request Body
            body = ""

            # Get the full body plus headers
            for index, line in enumerate(buffer):
                if index == 0:
                    data = line.decode(self.parser.encoding).split()
                else:
                    if not end_of_headers:
                        if line == b'\r\n':
                            end_of_headers = True
                    else:
                        body += line.decode(self.parser.encoding)

            # Check if we recieved a method
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

            # Check if we received a valid resource
            resource = await self.resource.check_valid_resource(data)
            if resource is False:
                await self.messenger.send_headers("400 Bad Request")
                self.conn.close()
                return

            # Dependent on the request method, handle it
            if method == 'OPTIONS':
                # Send response with default headers and the ALLOWED header
                await self.messenger.send_headers("200 OK", allow=True)
            else:
                # Try to gather the resource
                data, content_length, mime_type, encoding = await self.resource.get(resource, self.address[0])
                if data is not False and content_length is not None:
                    # If the resource was found and loaded, Send Response
                    content_type = mime_type + "; charset=" + str(encoding).lower() + ";"
                    await self.messenger.send_data_with_headers("200 OK", data, content_length=content_length, content_type=content_type)
                    self.log.debug("Sent {} with content_length: {}".format("200 OK", content_length))
                else:
                    # If the resource was not found or loaded Send 404 because file doesn't exists
                    await self.messenger.send_data_with_headers("404 Not Found", "Sorry, that file does not exist")
                    self.log.debug("404 - {} tried to access {}".format(self.address[0], resource))

            # Close connection when we have finished handling the request
            self.log.debug("Closing Connection with: {}".format(self.address[0]))
            self.conn.close()
            return
