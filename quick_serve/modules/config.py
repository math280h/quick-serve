import configparser
from os import path


class Config:
    """Config Module - Handles everything config"""
    def __init__(self):
        """Intiliaze the Config Module"""
        self.options = configparser.RawConfigParser()
        self.options.read(path.join(path.dirname(path.dirname(path.abspath(__file__))), 'config.ini'))
        self.check_config()

    def check_config(self):
        """Checks if the config file provides everything we need, otherwise define it"""
        expected_config = {
            'Server': {
                'ListenAddress': '127.0.0.1',
                'Port': '80',
                'HttpVersion': '1.0',
                'ByteReadSize': '8192',
                'DefaultFile': 'index.html',
                'SupportedMethods[]': 'GET, PUT, HEAD, POST, DELETE, OPTIONS',
                'DefaultEncoding': 'UTF-8'
            },
            'General': {
                'ExtendedLogging': 'false',
                'WorkingDirectory': '/var/www'
            }
        }

        # Check each section and it's options
        for section in expected_config:
            try:
                # Try to add a section
                self.options.add_section(section)
            except configparser.DuplicateSectionError:
                # If DuplicateSection, we expect the user defined it
                print("Section Exists - Using User Input")
            for option in expected_config[section]:
                # For every Option in that section
                if not self.options.has_option(section, option):
                    # Try to create the Option if it didn't exist
                    self.options.set(section, option, expected_config[section][option])
