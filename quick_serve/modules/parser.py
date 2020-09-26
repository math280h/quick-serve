class Parser:
    """Parser for incomming HTTP data"""
    def __init__(self, config):
        self.state = ''
        self.headers = {}
        self.encoding = config.options.get("Server", "DefaultEncoding")
        self.current_length = 0

    def set_state(self, state):
        """Overwrite current state if it's either empty or the body is incomplete"""
        if self.state == '' or self.state == 'BODY_INCOMPLETE':
            self.state = state

    def set_encoding(self):
        """If the Content-Type header is set, try to get the encoding"""
        if "Content-Type" in self.headers:  # Check if the Content-Type header is present
            content_type = "".join(self.headers["Content-Type"].split()).split(";")  # Split Content-Type into an array
            for ctx in content_type:  # Walk through each parameter in Content-Type
                if "charset" in ctx:
                    self.encoding = ctx.split("=")[1].upper()  # Set the Encoding to the one specified in the Headers

    def verify_headers(self, req, headers_ok: bool):
        """Verify that the expected headers are present

        :param req: HTTP Request
        :param headers_ok: Boolean based on if headers were already verified
        """
        if not headers_ok:  # If headers were not already gathered
            try:
                headers = req.decode().split("\r\n", 1)[1].split("\r\n\r\n")[0].split("\r\n")  # Split the request
                # headers into an array
                for header in headers:
                    h = header.split(":")
                    self.headers[h[0]] = h[1].strip()  # Store the header and it's value
            except (UnicodeDecodeError, IndexError):
                self.set_state('NO_HEADERS')

    def check_for_body(self, req, headers_ok: bool):
        """If a body is present in the request, try to get it

        :param req: HTTP Request
        :param headers_ok: Boolean based on if headers were already verified
        """
        try:
            if not headers_ok:  # If we didn't already read the headers, split the request so we only get the body
                body = req.decode(self.encoding).split("\r\n", 1)[1].split("\r\n\r\n")[1]
            else:  # Read the full data as the body
                body = req.decode(self.encoding)

            if "Content-Length" in self.headers:  # If Content-Length is in the headers
                expected_length = int(self.headers["Content-Length"])  # Get the Expected length of the Body
                self.current_length += len(body.encode())  # Calculate how far we are into the body

                if expected_length != self.current_length:  # If there is missing data from the body
                    self.set_state('BODY_INCOMPLETE')
                else:  # Full body recieved
                    self.set_state('DONE')
            else:  # No Content-Length was present
                self.set_state('INVALID_CONTENT_LENGTH')
        except IndexError:  # Some of the body was in the request together with the headers and we are missing some
            self.set_state('BODY_INCOMPLETE')
        if self.state != 'BODY_INCOMPLETE':  # We didn't find a body in the reqeuest
            self.set_state('NO_BODY')

    def parse_request(self, req, headers_ok=False):
        """Parse an HTTP Request

        :param req: HTTP Request
        :param headers_ok: Boolean based on if headers were already verified
        :return: state - NO_HEADERS, BODY_INCOMPLETE, DONE, INVALID_CONTENT_LENGTH, NO_BODY
        """
        # Verify Expected Headers
        self.verify_headers(req, headers_ok)
        # Set Encoding if header is present
        self.set_encoding()
        # Check if the request contains a body
        self.check_for_body(req, headers_ok)
        # Return current state
        return self.state
