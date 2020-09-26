class Messenger:
    """Messenger Helper - Manages all responses to connection"""
    def __init__(self, config, log, conn):
        self.conn = conn
        self.config = config
        self.log = log

    async def send(self, data: str):
        """Send Response to Connection

        :param data: Data to respond with
        """
        try:
            self.conn.send(data.encode())
        except Exception as e:
            self.log.error("Unable to send response", e)

    async def get_headers(self, code: str, content_length=0, content_type="text/html; charset=utf-8;", allow=None):
        """Gather & Format Headers into single string

        :param code: HTTP Code (E.g. '200 OK')
        :param content_length: Encoded data Content-Length
        :param content_type: Data Content-Type (E.g. 'html/text; charset=utf-8;')
        :param allow: Send Allow Header (Used for 'OPTIONS' Request)
        :return: Headers as string
        """
        headers = "HTTP/{} {}\r\nServer: quick-serve\r\n".format(self.config.options.get("Server", "HttpVersion"), code)
        if content_length != 0:  # If Content-Length is present, append header
            headers += "Content-Length: {}\r\nContent-Type: {}\r\n".format(content_length, content_type)
        if allow is not None:  # If Allow is present, append header
            headers += "Allow: {}\r\n".format(self.config.options.get("Server", "SupportedMethods[]"))
        headers += "\r\n"  # Specify end of Headers
        return headers

    async def send_headers(self, code: str, content_length=0, content_type="text/html; charset=utf-8;", allow=None):
        """Send headers

        :param code: HTTP Code (E.g. '200 OK')
        :param content_length: Encoded data Content-Length
        :param content_type: Data Content-Type (E.g. 'html/text; charset=utf-8;')
        :param allow: Send Allow Header (Used for 'OPTIONS' Request)
        """
        headers = await self.get_headers(code, content_length, content_type, allow)
        await self.send(headers)

    async def send_data_with_headers(self, code: str, data: str, content_length=0, content_type="text/html; "
                                                                                                "charset=utf-8;"):
        """Send some data with the header response

        :param code: HTTP Code (E.g. '200 OK')
        :param data: Data to append
        :param content_length: Encoded data Content-Length
        :param content_type: Data Content-Type (E.g. 'html/text; charset=utf-8;')
        """
        headers = await self.get_headers(code, content_length, content_type)  # Gather headers
        request = headers + data  # Append Data to Headers
        await self.send(request)  # Send Request
