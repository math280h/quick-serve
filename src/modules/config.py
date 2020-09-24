import configparser
from os import path


class Config:
    def __init__(self):
        # Init Config File
        self.options = configparser.RawConfigParser()
        self.options.read(path.join(path.dirname(path.dirname(path.abspath(__file__))), 'config.ini'))
        self.check_config()

    def check_config(self):
        # Check Config - If it doesn't exists create defaults
        expected_config = {
            'Server': {
                'ListenAddress': '127.0.0.1',
                'Port': '80',
                'HttpVersion': '1.0',
                'ByteReadSize': '8192',
                'DefaultFile': 'index.html',
                'SupportedMethods[]': 'GET, PUT, HEAD, POST, DELETE, OPTIONS'
            },
            'General': {
                'ExtendedLogging': 'false',
                'WorkingDirectory': '/var/www'
            }
        }

        # Check each section and it's options
        for section in expected_config:
            try:
                self.options.add_section(section)
            except configparser.DuplicateSectionError:
                print("Section Exists - Using User Input")
            for option in expected_config[section]:
                if not self.options.has_option(section, option):
                    self.options.set(section, option, expected_config[section][option])
