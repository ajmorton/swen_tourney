import json
import os

from util import paths
from util.funcs import print_tourney_trace


class ServerConfig:

    default_server_config = {
        'host': '127.0.0.1',
        'port': 8080
    }

    server_config = default_server_config

    def __init__(self):
        if not os.path.exists(paths.SERVER_CONFIG):
            print_tourney_trace("No server configuration file found at {}. Using default configuration.".format(
                paths.SERVER_CONFIG))
            ServerConfig.write_default()
            self.server_config = self.default_server_config
        else:
            self.server_config = json.load(open(paths.SERVER_CONFIG, 'r'))

    def host(self) -> str:
        return self.server_config['host']

    def port(self) -> int:
        return self.server_config['port']

    def check_server_config(self) -> bool:
        print("Server is listening on {}:{}".format(self.host(), self.port()))
        print()
        return True

    @staticmethod
    def write_default():
        json.dump(ServerConfig.default_server_config, open(paths.SERVER_CONFIG, 'w'), indent=4, sort_keys=True)
