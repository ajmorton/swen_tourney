import json
import os

config_file_path = os.path.dirname(os.path.abspath(__file__)) + '/config.json'

default_config = {
    'server': {
        'host': '127.0.0.1',
        'port': 11013
    }
}


def get_port():
    config = read_settings()
    return config['server']['port']


def get_host():
    config = read_settings()
    return config['server']['host']


def read_settings():
    # create a default config file if none exists
    if not os.path.isfile(config_file_path):
        with open(config_file_path, 'w') as config_file:
            json.dump(default_config, config_file)
            config_file.close()

    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
        config_file.close()
        return config
