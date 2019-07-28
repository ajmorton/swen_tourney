from config import paths
import os
import json


class ServerConfig:

    default_server_config = {
        'host': '127.0.0.1',
        'port': 11013
    }

    server_config = default_server_config

    def __init__(self):
        if not os.path.exists(paths.SERVER_CONFIG):
            print("No server configuration file found at {}. Using default configuration.".format(paths.SERVER_CONFIG))
            ServerConfig.write_default()
            self.server_config = self.default_server_config
        else:
            self.server_config = json.load(open(paths.SERVER_CONFIG, 'r'))

    def host(self) -> str:
        return self.server_config['host']

    def port(self) -> int:
        return self.server_config['port']

    @staticmethod
    def write_default():
        json.dump(ServerConfig.default_server_config, open(paths.SERVER_CONFIG, 'w'), indent=4)
