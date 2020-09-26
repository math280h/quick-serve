from io import BytesIO

from quick_serve.modules.parser import Parser
from quick_serve.modules.methods import Methods
from quick_serve.modules.messenger import Messenger
from quick_serve.modules.resource import Resource


class Connection:
    def __init__(self, config, log, conn, address, cache):
        self.conn = conn
        self.address = address

        self.log = log
        self.config = config
        self.parser = Parser(config)
        self.messenger = Messenger(config, log, conn)
        self.resource = Resource(config, log, cache)
        self.methods = Methods(config)

    async def handle(self):
        self.log.info('Accepted connection from: {}'.format(self.address[0]))
        state = ''
        with BytesIO() as buffer:
            self.log.debug("Collecting data in buffer")
            while True:
                try:
                    req = self.conn.recv(int(self.config.options.get("Server", "ByteReadSize")))
                except (BlockingIOError, ConnectionAbortedError, ConnectionResetError) as e:
                    self.log.debug('Connection was closed by client: {}'.format(e))
                if not req:
                    break

                if state == 'BODY_INCOMPLETE':
                    self.log.debug("Parsing Body")
                    state = self.parser.parse_request(req, headers_ok=True)
                    buffer.write(req)
                else:
                    self.log.debug("Parsing Request")
                    state = self.parser.parse_request(req)
                    buffer.write(req)
                if state == 'DONE' or state == 'NO_BODY' or state == 'INVALID_CONTENT_LENGTH':
                    self.log.debug("Done Parsing")
                    break

            buffer.seek(0)
            end_of_headers = False
            data = []
            body = ""

            for index, line in enumerate(buffer):
                if index == 0:
                    data = line.decode(self.parser.encoding).split()
                else:
                    if not end_of_headers:
                        if line == b'\r\n':
                            end_of_headers = True
                    else:
                        body += line.decode(self.parser.encoding)

            try:
                method = data[0]
            except IndexError:
                await self.messenger.send_headers("400 Bad Request")
                self.conn.close()
                return

            if not self.methods.is_allowed(method):
                await self.messenger.send_headers("405 Method Not Allowed")
                self.conn.close()
                return

            resource = await self.resource.check_valid_resource(data)
            if resource is False:
                await self.messenger.send_headers("400 Bad Request")
                self.conn.close()
                return

            if method == 'OPTIONS':
                await self.messenger.send_headers("200 OK", allow=True)
            else:
                data, content_length = await self.resource.get(resource, self.address[0])
                if data is not False and content_length is not None:
                    # Send Response
                    await self.messenger.send_data_with_headers("200 OK", data, content_length=content_length)
                    self.log.debug("Sent {} with content_length: {}".format("200 OK", content_length))
                else:
                    # Send 404 because file doesn't exists
                    await self.messenger.send_data_with_headers("404 Not Found", "Sorry, that file does not exist")
                    self.log.debug("404 - {} tried to access {}".format(self.address[0], resource))

            # Close connection when we have finished handling the request
            self.log.debug("Closing Connection with: {}".format(self.address[0]))
            self.conn.close()
            return
