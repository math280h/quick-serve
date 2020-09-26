class Methods:
    """Method Helper - is used to check for e.g. allowed methods

    :param config
    """
    def __init__(self, config):
        self.config = config
        self.allowed_methods = self.config.options.get("Server", "SupportedMethods[]")

    def is_allowed(self, method: str):
        """Checks if a method is allowed

        :param method: HTTP Method
        :return: Boolean
        """
        if method in self.allowed_methods:
            return True
        return False
