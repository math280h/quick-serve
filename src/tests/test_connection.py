import socket
import unittest

HOST = '127.0.0.1'
PORT = 80


class Connection(unittest.TestCase):
    def test_welcome_message(self):
        """
        Test that we get a welcome message when connecting
        :return:
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        data = sock.recv(1024).decode('UTF-8')
        sock.close()

        self.assertEqual(data, 'quick-serve (v0.0.1)\n')

    def test_connection(self):
        """
        Test that we can successfully connect to the server
        :return:
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        success = True
        try:
            sock.connect((HOST, PORT))
        except ConnectionError:
            success = False
        sock.close()
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()
