import socket
import threading
import logging
from logging.config import fileConfig
from os import path
import re
import configparser


class Server:
    def __init__(self):
        self.host = config.get("Server", "ListenAddress")
        self.port = int(config.get("Server", "Port"))
        self.size = int(config.get("Server", "ByteReadSize"))
        self.supported_methods = config.get("Server", "SupportedMethods[]")
        self.http_version = config.get("Server", "HttpVersion")
        self.extended_logging = config.get("General", "ExtendedLogging").lower() in ['true', '0']

        # Bind Socket & set Socket Options
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        # Wait for a connection (Max 5 in queue allowed)
        self.sock.listen()
        logger.info('Server is now listening for connections')
        while True:
            # Accept connection
            client, address = self.sock.accept()
            # Split connection into thread
            threading.Thread(target=self.handle_client, args=(client, address)).start()

    def send_http_headers(self, conn, code, content_length=0, content_type="text/html; charset=UTF-8", allow=None):
        conn.send("HTTP/{} {}\r\n".format(self.http_version, code).encode())
        if content_length != 0:
            conn.send("Content-Length: {}\r\n".format(content_length).encode())
        if allow is not None:
            conn.send("Allow: {}\r\n".format(config.get("Server", "SupportedMethods[]")).encode())
        conn.send("Server: quick-serve\r\n".encode())
        conn.send("Content-Type: {}\r\n\r\n".format(content_type).encode())

    def handle_client(self, conn, address):
        logger.info('Accepted connection from: {}'.format(address[0]))
        while True:
            # Recieve Data
            try:
                data = conn.recv(self.size)
            except (ConnectionResetError, ConnectionAbortedError) as e:
                if self.extended_logging:
                    logger.info('Connection was closed by client: {}'.format(e))
                break
            if not data:
                break

            # Decode Data
            try:
                request = data.decode('UTF-8').strip().split("\r\n", 1)

                # Define Request and Request Headers
                try:
                    req = request[0].split()
                    req_headers = request[1].split("\r\n")
                except IndexError:
                    if self.extended_logging:
                        logger.error('Request failed because no headers were present')
                    self.send_http_headers(conn, "400 Bad Request")
                    conn.close()
                    break
            except UnicodeDecodeError as e:
                if self.extended_logging:
                    logger.error('Decode Error: {}'.format(e))
                self.send_http_headers(conn, "500 Internal Server Error")
                conn.close()
                break

            # Make sure the request contains the minimum expected amount of data
            if len(req) < 3 or req[0] == '':
                if self.extended_logging:
                    logger.error('{} sent an invalid request'.format(address[0]))
                self.send_http_headers(conn, "400 Bad Request")
                conn.close()
                break

            # Check for allowed methods
            if req[0] not in self.supported_methods:
                logger.error('{} sent unknown method: {}'.format(address[0], req[0]))
                self.send_http_headers(conn, "405 Method Not Allowed")
                conn.close()
                break

            # Check Version is valid
            if req[2].split('/')[0] != 'HTTP' or not re.match("^[0-9][.][0-9]$", req[2].split('/')[1]):
                if self.extended_logging:
                    logger.error('{} sent an invalid request'.format(address[0]))
                self.send_http_headers(conn, "400 Bad Request")
                conn.close()
                break

            # Define Method, Resource, Version from request
            method = req[0]
            if req[1] == '' or req[1] == '/':
                req[1] = config.get("Server", "DefaultFile")
            resource = config.get("General", "WorkingDirectory") + req[1]
            client_version = req[2]

            # Check if the resource exists
            if method == 'OPTIONS':
                self.send_http_headers(conn, "200 OK", allow=True)
            else:
                if path.isfile(resource):
                    if self.extended_logging:
                        logging.info("{} {} {}".format(address[0], "Accessed:", resource))
                    # Read the resource
                    resource_data = open(resource, "r").read()
                    content_length = len(resource_data.encode())
                    # Send Response
                    self.send_http_headers(conn, "200 OK", content_length=content_length)
                    conn.send("{}".format(resource_data).encode())
                else:
                    # Send 404 because file doesn't exists
                    self.send_http_headers(conn, "404 Not Found")
                    if self.extended_logging:
                        logger.info("404 - {} tried to access {}".format(address[0], resource))
                    conn.send("Sorry, that file does not exist".encode())

            # Close Connection
            conn.close()
            break


def check_config():
    # Check Config - If it doesn't exists create defaults
    # Check General Setcion
    if not config.has_section("General"):
        config.add_section("General")
    if not config.has_option("General", "ExtendedLogging"):
        config.set("General", "ExtendedLogging", "false")
    if not config.has_option("General", "WorkingDirectory"):
        config.set("General", "WorkingDirectory", "/var/www")

    # Check Server Section
    if not config.has_section("Server"):
        config.add_section("General")
    if not config.has_option("Server", "ListenAddress"):
        config.set("Server", "ListenAddress", "127.0.0.1")
    if not config.has_option("Server", "Port"):
        config.set("Server", "Port", "80")
    if not config.has_option("Server", "HttpVersion"):
        config.set("Server", "HttpVersion", "1.1")
    if not config.has_option("Server", "ByteReadSize"):
        config.set("Server", "ByteReadSize", "1024")
    if not config.has_option("Server", "DefaultFile"):
        config.set("Server", "DefaultFile", "/index.html")
    if not config.has_option("Server", "SupportedMethods[]"):
        config.set("Server", "SupportedMethods[]", "GET, PUT, HEAD, POST, DELETE, OPTIONS")


if __name__ == '__main__':
    # Init Config File
    config = configparser.RawConfigParser()
    config.read(path.join(path.dirname(path.abspath(__file__)), 'config.ini'))

    # Check Configuration
    check_config()

    # Init Log Config
    fileConfig(path.join(path.dirname(path.abspath(__file__)), 'log_config.ini'))
    logger = logging.getLogger()

    # Start the HTTP Server
    logger.info('Starting HTTP Server')
    Server().listen()
