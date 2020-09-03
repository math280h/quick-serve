import requests
import unittest

HOST = '127.0.0.1'
PORT = 80


class Get(unittest.TestCase):

    def test_get_content(self):
        """
        Test that we get content back when requesting default file
        :return:
        """
        req = requests.get("http://127.0.0.1/")

        self.assertTrue(req.text)

    def test_path_security(self):
        """
        Test that we cannot access paths outside of the working directory
        :return:
        """
        req = requests.get("http://127.0.0.1/../README.md")

        self.assertEqual(req.status_code, 404)


if __name__ == '__main__':
    unittest.main()
