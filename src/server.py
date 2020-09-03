import socket
import threading
import logging
from logging.config import fileConfig
from os import path
import re
import configparser


class Server:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 80
        self.size = 1024
        self.supported_methods = ['GET', 'PUT', 'HEAD', 'POST', 'DELETE', 'OPTIONS']
        self.http_version = '1.1'

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

    def send_http_headers(self, conn, code, content_length=0, content_type="text/html; charset=UTF-8"):
        conn.send("HTTP/{} {}\r\n".format(self.http_version, code).encode())
        if content_length != 0:
            conn.send("Content-Length: {}\r\n".format(content_length).encode())
        conn.send("Server: quick-serve\r\n".encode())
        conn.send("Content-Type: {}\r\n\r\n".format(content_type).encode())

    def handle_client(self, conn, address):
        logger.info('Accepted connection from: {}'.format(address[0]))
        while True:
            # Recieve Data
            try:
                data = conn.recv(self.size)
            except (ConnectionResetError, ConnectionAbortedError) as e:
                logging.info('Connection was closed by client: {}'.format(e))
                break
            if not data:
                break

            # Decode Data
            try:
                request = data.decode('UTF-8').strip().split("\r\n", 1)

                # Define Request and Request Headers
                req = request[0].split()
                req_headers = request[1].split("\r\n")
            except UnicodeDecodeError as e:
                logger.error('Decode Error: {}'.format(e))
                self.send_http_headers(conn, "500 Internal Server Error")
                conn.close()
                break

            # Make sure the request contains the minimum expected amount of data
            if len(req) < 3 or req[0] == '':
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
                logger.error('{} sent an invalid request'.format(address[0]))
                self.send_http_headers(conn, "400 Bad Request")
                conn.close()
                break

            # Define Method, Resource, Version from request
            method = req[0]
            if req[1] == '' or req[1] == '/':
                req[1] = '/index.html'
            resource = 'F:/www' + req[1]
            client_version = req[2]

            # Check if the resource exists
            if path.isfile(resource):
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
                logger.info("404 - {} tried to access {}".format(address[0], resource))
                conn.send("Sorry, that file does not exist".encode())

            # Close Connection
            conn.close()
            break


if __name__ == '__main__':
    # Init Config File
    config = configparser.ConfigParser()
    config.sections()
    config.read(path.dirname(path.abspath(__file__)), 'config.ini')

    # Init Log Config
    fileConfig(path.join(path.dirname(path.abspath(__file__)), 'log_config.ini'))
    logger = logging.getLogger()

    # Start the HTTP Server
    logger.info('Starting HTTP Server')
    Server().listen()
