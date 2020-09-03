import unittest
import requests

HOST = '127.0.0.1'
PORT = 80


class Connection(unittest.TestCase):
    def test_headers(self):
        """
        Test that we get the correct headers when requesting OPTIONS
        :return:
        """
        req = requests.options("http://127.0.0.1")

        self.assertEqual(req.headers, {'Allow': 'GET, PUT, HEAD, POST, DELETE, OPTIONS', 'Server': 'quick-serve',
                                       'Content-Type': 'text/html; charset=UTF-8'})

    def test_connection(self):
        """
        Test that we can successfully connect to the server
        :return:
        """
        req = requests.get("http://127.0.0.1")

        self.assertEqual(req.status_code, 200)


if __name__ == '__main__':
    # Start Unit tests
    unittest.main()
