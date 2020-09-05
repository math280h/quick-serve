class Parser:
    def __init__(self):
        self.state = ''
        self.headers = {}
        self.encoding = "UTF-8"
        self.current_length = 0

    def set_state(self, state):
        if self.state == '':
            self.state = state
        elif self.state == 'BODY_INCOMPLETE':
            self.state = state

    def set_encoding(self):
        if "Content-Type" in self.headers:
            content_type = "".join(self.headers["Content-Type"].split()).split(";")
            for ctx in content_type:
                if "charset" in ctx:
                    self.encoding = ctx.split("=")[1].upper()

    def verify_headers(self, req, headers_ok):
        # Try to gather headers
        try:
            headers = req.decode().split("\r\n", 1)[1].split("\r\n\r\n")[0].split("\r\n")
            for header in headers:
                h = header.split(":")
                self.headers[h[0]] = h[1].strip()
        except (UnicodeDecodeError, IndexError) as e:
            if not headers_ok:
                self.set_state('NO_HEADERS')

    def check_for_body(self, req, headers_ok):
        # Check if we recieved a body and handle if we did
        try:
            if not headers_ok:
                body = req.decode(self.encoding).split("\r\n", 1)[1].split("\r\n\r\n")[1]
            else:
                body = req.decode(self.encoding)

            if "Content-Length" in self.headers:
                expected_length = int(self.headers["Content-Length"])
                self.current_length += len(body.encode())

                if expected_length != self.current_length:
                    self.set_state('BODY_INCOMPLETE')
                else:
                    self.set_state('DONE')
        except IndexError:
            self.set_state('BODY_INCOMPLETE')
        if self.state != 'BODY_INCOMPLETE':
            self.set_state('NO_BODY')

    def parse_request(self, req, headers_ok=False):
        # Verify Expected Headers
        self.verify_headers(req, headers_ok)
        # Set Encoding if header is present
        self.set_encoding()
        # Check if the request contains a body
        self.check_for_body(req, headers_ok)
        # Return current state
        return self.state
