from config.exceptions import NoConfigDefined
import os
import json
from util import paths

from smtplib import SMTP, SMTPHeloError, SMTPAuthenticationError, SMTPConnectError
import socket


class EmailConfig:

    default_email_config = {
        'sender': "swen-tourney-noreply@unimelb.edu.au",  # the email to send tournament results from
        'password': "email_password_goes_here",  # the password of the email account
        'smtp_server': "smtp.unimelb.edu.au",  # the smtp server to connect to to send the emails
        'port': 587,  # the port to connect to the SMTP server on
        'crash_report_recipients': ["recipient_1@mail.com", "recipient_2@mail.com"]  # who to notify of tourney crashes
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

    def crash_report_recipients(self) -> str:
        return ", ".join(self.email_config['crash_report_recipients'])

    @staticmethod
    def write_default():
        json.dump(EmailConfig.default_email_config, open(paths.EMAIL_CONFIG, 'w'), indent=4, sort_keys=True)

    def check_email_valid(self) -> bool:
        valid = self.check_email_non_default()

        if valid:
            valid = self.check_connection()

        print()
        return valid

    def check_email_non_default(self) -> bool:
        if self.email_config != EmailConfig.default_email_config:
            print("Emails will be sent from: {}".format(self.sender()))
            return True
        else:
            print("ERROR: Email has not been configured.\n"
                  "       Please update {} with the correct details".format(paths.EMAIL_CONFIG))
            return False

    def check_connection(self) -> bool:
        smtp_server = self.smtp_server()
        port = self.port()
        email = self.sender()
        password = self.password()

        try:
            smtp = SMTP(smtp_server, port, timeout=10)
            smtp.starttls()
            smtp.login(email, password)
        except socket.timeout:
            print("\tERROR: Timeout while trying to connect {}:{}".format(smtp_server, port))
            return False
        except (SMTPHeloError, SMTPConnectError):
            print("\tERROR: Cannot connect to {}:{}".format(smtp_server, port))
            return False
        except SMTPAuthenticationError:
            print("\tERROR: Login attempt for {} failed".format(email))
            return False

        print("\tSuccessful connection and authentication with SMTP server")

        return True
