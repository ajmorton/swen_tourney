"""
Exception raised when validating configuration files
"""


class NoConfigDefined(Exception):
    """ Error raised when no configuration file is found """
    def __init__(self, message):
        super().__init__()
        self.message = message
