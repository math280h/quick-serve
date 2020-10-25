import unittest
import requests

from quick_serve.modules import Config


class Connection(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = Config()

    def test_headers(self):
        """
        Test that we get the correct headers when requesting OPTIONS
        :return:
        """
        req = requests.options("http://{}:{}".format(self.config.options.get("Server", "ListenAddress"),
                                                     self.config.options.get("Server", "Port")))

        self.assertEqual(req.headers, {'Server': 'quick-serve', 'Allow': 'GET, PUT, HEAD, POST, DELETE, OPTIONS'})

    def test_connection(self):
        """
        Test that we can successfully connect to the server
        :return:
        """
        req = requests.get("http://{}:{}".format(self.config.options.get("Server", "ListenAddress"),
                                                 self.config.options.get("Server", "Port")))

        self.assertEqual(req.status_code, 200)


if __name__ == '__main__':
    # Start Unit tests
    unittest.main()
