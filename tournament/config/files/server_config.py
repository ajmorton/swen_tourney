"""
Configuration for the hosting of the results server
"""
import json
import os

from tournament.util import paths, print_tourney_trace, Result


class ServerConfig:
    """ Configuration for the hosting of the results server """

    default_server_config = {
        'host': '127.0.0.1',
        'port': 8080
    }

    server_config = default_server_config

    def __init__(self):
        if not os.path.exists(paths.SERVER_CONFIG):
            print_tourney_trace(f"No server configuration file found at {paths.SERVER_CONFIG}. "
                                f"Using default configuration.")
            ServerConfig.write_default()
            self.server_config = self.default_server_config
        else:
            self.server_config = json.load(open(paths.SERVER_CONFIG, 'r'))

    def host(self) -> str:
        """ The host of the results server """
        return self.server_config['host']

    def port(self) -> int:
        """ The port on which the results server is accessible """
        return self.server_config['port']

    def check_server_config(self) -> Result:
        """ Write the details of the results server on tournament start up """
        return Result(True, f"Server is listening on {self.host()}:{self.port()}\n")

    @staticmethod
    def write_default():
        """ Create a default ServerConfig file """
        json.dump(ServerConfig.default_server_config, open(paths.SERVER_CONFIG, 'w'), indent=4, sort_keys=True)
