import unittest
import requests

from src.modules import Config


class Get(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = Config()

    def test_get_content(self):
        """
        Test that we get content back when requesting default file
        :return:
        """
        req = requests.get("http://{}:{}/".format(self.config.options.get("Server", "ListenAddress"), self.config.options.get("Server", "Port")))

        self.assertTrue(req.text)

    def test_path_security(self):
        """
        Test that we cannot access paths outside of the working directory
        :return:
        """
        req = requests.get("http://{}:{}/../README.md".format(self.config.options.get("Server", "ListenAddress"), self.config.options.get("Server", "Port")))

        self.assertEqual(req.status_code, 404)


if __name__ == '__main__':
    unittest.main()
