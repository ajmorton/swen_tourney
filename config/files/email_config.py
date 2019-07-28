from config.exceptions import NoConfigDefined
import os
import json
from util import paths
from util.types import Result


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
            EmailConfig.write_default()
            raise NoConfigDefined("No email configuration file found at {}. A default one has been created"
                                  .format(paths.EMAIL_CONFIG))
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
        json.dump(EmailConfig.default_email_config, open(paths.EMAIL_CONFIG, 'w'), indent=4)

    def check_non_default(self) -> Result:
        if self.email_config != EmailConfig.default_email_config:
            return Result((True, ""))
        else:
            return Result((False, "ERROR: Email configuration has not been configured.\n"
                                  "       Please update {} with the correct details\n".format(paths.EMAIL_CONFIG)))

