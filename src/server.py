import socket
import threading
import logging
from logging.config import fileConfig
from os import path
import re


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
        self.sock.listen(5)
        logger.info('Server is now listening for connections')
        while True:
            # Accept connection
            client, address = self.sock.accept()
            # Split connection into thread
            threading.Thread(target=self.handle_client, args=(client, address)).start()

    def send_http_response(self, conn, code):
        conn.send("HTTP/{} {}\r\n\r\n".format(self.http_version, code).encode())

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
                self.send_http_response(conn, "500 Internal Server Error")
                conn.close()
                break

            # Make sure the request contains the minimum expected amount of data
            if len(req) < 3 or req[0] == '':
                logger.error('{} sent an invalid request'.format(address[0]))
                self.send_http_response(conn, "400 Bad Request")
                conn.close()
                break

            # Check for allowed methods
            if req[0] not in self.supported_methods:
                logger.error('{} sent unknown method: {}'.format(address[0], req[0]))
                self.send_http_response(conn, "405 Method Not Allowed")
                conn.close()
                break

            # Check Version is valid
            if req[2].split('/')[0] != 'HTTP' or not re.match("^[0-9][.][0-9]$", req[2].split('/')[1]):
                logger.error('{} sent an invalid request'.format(address[0]))
                self.send_http_response(conn, "400 Bad Request")
                conn.close()
                break

            # Define Method, Resource, Version from request
            method = req[0]
            resource = 'F:\\www' + req[1]
            client_version = req[2]

            # Check if the resource exists
            if path.isfile(resource):
                # Read the resource
                resource_data = open(resource, "r").read()

                # Send Response
                self.send_http_response(conn, "200 OK")
                conn.send("{}".format(resource_data).encode())
            else:
                # Send 404 because file doesn't exists
                self.send_http_response(conn, "404 Not Found")
                logger.info("404 - {} tried to access {}".format(address[0], resource))
                conn.send("Sorry, that file does not exist".encode())

            # Close Connection
            conn.close()
            break


if __name__ == '__main__':
    # Init Log Config
    log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log_config.ini')
    fileConfig(log_file_path)
    logger = logging.getLogger()

    # Start the HTTP Server
    logger.info('Starting HTTP Server')
    Server().listen()
