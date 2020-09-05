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
        # Check General Setcion
        if not self.options.has_section("General"):
            self.options.add_section("General")
        if not self.options.has_option("General", "ExtendedLogging"):
            self.options.set("General", "ExtendedLogging", "false")
        if not self.options.has_option("General", "WorkingDirectory"):
            self.options.set("General", "WorkingDirectory", "/var/www")

        # Check Server Section
        if not self.options.has_section("Server"):
            self.options.add_section("General")
        if not self.options.has_option("Server", "ListenAddress"):
            self.options.set("Server", "ListenAddress", "127.0.0.1")
        if not self.options.has_option("Server", "Port"):
            self.options.set("Server", "Port", "80")
        if not self.options.has_option("Server", "HttpVersion"):
            self.options.set("Server", "HttpVersion", "1.1")
        if not self.options.has_option("Server", "ByteReadSize"):
            self.options.set("Server", "ByteReadSize", "1024")
        if not self.options.has_option("Server", "DefaultFile"):
            self.options.set("Server", "DefaultFile", "/index.html")
        if not self.options.has_option("Server", "SupportedMethods[]"):
            self.options.set("Server", "SupportedMethods[]", "GET, PUT, HEAD, POST, DELETE, OPTIONS")