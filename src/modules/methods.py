class Methods:
    def __init__(self, config):
        self.config = config
        self.allowed_methods = self.config.options.get("Server", "SupportedMethods[]")

    def is_allowed(self, method):
        if method in self.allowed_methods:
            return True
        return False
