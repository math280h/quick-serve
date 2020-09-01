import socket
import unittest

HOST = '127.0.0.1'
PORT = 80


def get_last_response(payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.send(payload.encode())
    while True:
        data = sock.recv(2048).decode('UTF-8').splitlines()
        if 'quick-serve' not in data:
            data = sock.recv(2048).decode('UTF-8')
            break
    sock.close()
    return data


class Get(unittest.TestCase):

    def test_undefined_word(self):
        """
        Test that we get an error when asking for an undefined error
        :return:
        """
        data = get_last_response("GET test")

        self.assertEqual(data, 'ERROR undefined\n', "Should be: ERROR undefined")

    def test_invalid(self):
        """
        Test that we get an error when supplying invalid command
        :return:
        """
        data = get_last_response("GET")

        self.assertEqual(data, 'ERROR invalid command\n')


if __name__ == '__main__':
    unittest.main()
