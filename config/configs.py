from config.assignments.ant.AntAssignment import AntAssignment
from config import paths
import json
import os

# Which assignment the tournament is configured for
# TODO how to hotswap assignment imports?
assignment = AntAssignment()


class NoConfigDefined(Exception):
    pass


class EmailConfig:

    default_email_config = {
        'sender': "swen-tourney-noreply@unimelb.edu.au",  # the email to send tournament results from
        'password': "email_password_goes_here",  # the password of the email account
        'smtp_server': "smtp.unimelb.edu.au",  # the smtp server to connect to to send the emails
        'port': 587  # the port to connect to the SMTP server on
    }

    email_config = {}

    def __init__(self):
        if not os.path.exists(paths.EMAIL_CONFIG):
            raise NoConfigDefined
        else:
            self.email_config = json.load(open(paths.EMAIL_CONFIG, 'r'))

    def sender(self) -> str:
        return self.email_config['sender']

    def password(self) -> str:
        return self.email_config['password']

    def smtp_server(self) -> str:
        return self.email_config['smtp_server']

    def port(self) -> str:
        return self.email_config['port']

    @staticmethod
    def write_default():
        json.dump(EmailConfig.default_email_config, open(paths.SERVER_CONFIG, 'w'), indent=4)

    def check_non_default(self) -> bool:
        return self.email_config != EmailConfig.default_email_config


class ApprovedSubmitters:

    default_approved_submitters = {
        "student_a": {'email': "student_a@student.unimelb.edu.au"},
        "student_b": {'email': "student_b@student.unimelb.edu.au"},
        "student_c": {'email': "student_c@student.unimelb.edu.au"},
    }

    approved_submitters = {}

    def __init__(self):
        if not os.path.exists(paths.APPROVED_SUBMITTERS_LIST):
            raise NoConfigDefined
        else:
            self.approved_submitters = json.load(open(paths.APPROVED_SUBMITTERS_LIST, 'r'))

    def get_list(self) -> dict:
        return self.approved_submitters

    @staticmethod
    def write_default():
        json.dump(EmailConfig.default_email_config, open(paths.SERVER_CONFIG, 'w'), indent=4)

    def check_non_default(self) -> bool:
        return self.approved_submitters != ApprovedSubmitters.default_approved_submitters


class ServerConfig:

    default_server_config = {
        'host': '127.0.0.1',
        'port': 11013
    }

    server_config = {}

    def __init__(self):
        if not os.path.exists(paths.SERVER_CONFIG):
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


def get_email_config() -> dict:
    return json.load(open(paths.EMAIL_CONFIG, 'r'))


def get_approved_submitters() -> dict:
    return json.load(open(paths.APPROVED_SUBMITTERS_LIST, 'r'))


def create_default_configs():
    EmailConfig.write_default()
    ApprovedSubmitters.write_default()
    ServerConfig().write_default()


def check_configs_non_default() -> bool:
    email_config_non_default = EmailConfig().check_non_default()
    approved_submitters_non_default = ApprovedSubmitters().check_non_default()
    # the server config can be default, no need to check

    return email_config_non_default and approved_submitters_non_default
