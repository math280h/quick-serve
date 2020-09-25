from io import BytesIO

from src.modules.parser import Parser
from src.modules.methods import Methods
from src.modules.messenger import Messenger
from src.modules.resource import Resource


class Connection:
    def __init__(self, config, log, conn, address):
        self.conn = conn
        self.address = address

        self.log = log
        self.config = config
        self.parser = Parser()
        self.messenger = Messenger(config, conn)
        self.resource = Resource(config, log)

    async def handle(self):
        self.log.info('Accepted connection from: {}'.format(self.address[0]))
        state = ''
        with BytesIO() as buffer:
            while True:
                try:
                    req = self.conn.recv(int(self.config.options.get("Server", "ByteReadSize")))
                except (BlockingIOError, ConnectionAbortedError, ConnectionResetError) as e:
                    self.log.debug('Connection was closed by client: {}'.format(e))
                if not req:
                    break

                if state == 'BODY_INCOMPLETE':
                    state = self.parser.parse_request(req, headers_ok=True)
                    buffer.write(req)
                else:
                    state = self.parser.parse_request(req)
                    buffer.write(req)
                if state == 'DONE' or state == 'NO_BODY':
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
                self.messenger.send_headers("400 Bad Request")
                self.conn.close()
                return

            try:
                if data[1] == '' or data[1] == '/':
                    data[1] = self.config.options.get("Server", "DefaultFile")
            except IndexError:
                self.messenger.send_headers("400 Bad Request")
                self.conn.close()
                return

            resource = self.config.options.get("General", "WorkingDirectory") + data[1]

            if not Methods(self.config).is_allowed(method):
                self.messenger.send_headers("405 Method Not Allowed")
                self.conn.close()
                return

            if method == 'OPTIONS':
                self.messenger.send_headers("200 OK", allow=True)
            else:
                data, content_length = await self.resource.get(resource, self.address[0])
                if data is not False and content_length is not None:
                    # Send Response
                    self.messenger.send_headers("200 OK", content_length=content_length)
                    self.log.debug("Sent {} with content_length: {}".format("200 OK", content_length))
                    self.messenger.send(data)
                else:
                    # Send 404 because file doesn't exists
                    self.messenger.send_headers("404 Not Found")
                    self.messenger.send("Sorry, that file does not exist")
                    self.log.debug("404 - {} tried to access {}".format(self.address[0], resource))

            # Close connection when we have finished handling the request
            self.log.debug("Closing Connection with: {}".format(self.address[0]))
            self.conn.close()
            return
