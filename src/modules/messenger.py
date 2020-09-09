class Messenger:
    def __init__(self, config, conn):
        self.conn = conn
        self.config = config

    def send(self, data):
        try:
            self.conn.send(data.encode())
        except Exception as e:
            print(e)

    def send_headers(self, code, content_length=0, content_type="text/html; charset=utf-8;", allow=None):
        headers = "HTTP/{} {}\r\nServer: quick-serve\r\n".format(self.config.options.get("Server", "HttpVersion"), code)
        if content_length != 0:
            headers += "Content-Length: {}\r\nContent-Type: {}\r\n".format(content_length, content_type)
        if allow is not None:
            headers += "Allow: {}\r\n".format(self.config.options.get("Server", "SupportedMethods[]"))
        headers += "\r\n"
        self.send(headers)
