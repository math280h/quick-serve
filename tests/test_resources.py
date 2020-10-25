import unittest
import requests
from os import path

from quick_serve.modules import Config


def match_mime_type(ext):
    """Tries to match Mime Type to File Extension

    :param ext: File Extension as String
    :return: Mime Type as String
    """
    return {
        '.txt': 'text/plain',
        '.png': 'image/png',
        '.pdf': 'application/pdf',
        '.php': 'application/x-httpd-php',
        '.svg': 'image/svg+xml',
        '.ttf': 'font/ttf',
        '.zip': 'application/zip',
        '.htm': 'text/html',
        '.html': 'text/html',
        '.gif': 'image/gif',
        '.js': 'text/javascript',
        '.json': 'application/json'
    }.get(ext, "text/html")


class ResourceTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = Config()

    def test_content_type(self):
        """
        Test that we get the correct headers when requesting OPTIONS
        :return:
        """
        req = requests.get("http://{}:{}/{}".format(self.config.options.get("Server", "ListenAddress"),
                                                    self.config.options.get("Server", "Port"),
                                                    self.config.options.get("Server", "DefaultFile")))
        content_type = req.headers['Content-Type'].split(";")
        _, file_extension = path.splitext(self.config.options.get("Server", "DefaultFile"))
        expected_type = match_mime_type(file_extension)
        self.assertEqual(content_type[0], expected_type)

    def test_content_length(self):
        """
        Test that we get the correct headers when requesting OPTIONS
        :return:
        """
        req = requests.get("http://{}:{}/index.html".format(self.config.options.get("Server", "ListenAddress"),
                                                            self.config.options.get("Server", "Port")))
        self.assertEqual(req.headers['Content-Length'], str(len(req.text)))


if __name__ == '__main__':
    # Start Unit tests
    unittest.main()
