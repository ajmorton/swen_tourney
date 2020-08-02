"""
Configuration for emailing tournament maintainers details of the tournament. Namely crash reports.
"""
import json
import os
import socket
from smtplib import SMTP, SMTPHeloError, SMTPAuthenticationError, SMTPConnectError

from tournament.config.exceptions import NoConfigDefined
from tournament.util import paths, Result


class EmailConfig:
    """
    Contains configuration details needed for sending emails to tournament maintainers and validation of the
    configuration.
    """

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
            EmailConfig._write_default()
            raise NoConfigDefined("No email configuration file found at {} . A default one has been created"
                                  .format(paths.EMAIL_CONFIG))
        else:
            self.email_config = json.load(open(paths.EMAIL_CONFIG, 'r'))

    def sender(self) -> str:
        """ The sender of the email """
        return self.email_config['sender']

    def password(self) -> str:
        """ The password to login to the SMTP server """
        return self.email_config['password']

    def smtp_server(self) -> str:
        """ The SMTP server to connect to in order to send emails """
        return self.email_config['smtp_server']

    def port(self) -> str:
        """ The port to connect to on the SMTP server """
        return self.email_config['port']

    def crash_report_recipients(self) -> str:
        """ The emails addressed of tournament maintainers to notify of a crash """
        return ", ".join(self.email_config['crash_report_recipients'])

    @staticmethod
    def _write_default():
        """ Create a default EmailConfig file """
        json.dump(EmailConfig.default_email_config, open(paths.EMAIL_CONFIG, 'w'), indent=4, sort_keys=True)

    def check_email_valid(self) -> Result:
        """ Check the email config file is valid for usage """
        valid = self._check_email_non_default()

        if valid:
            valid = self._check_connection()

        valid.traces += "\n"
        return valid

    def _check_email_non_default(self) -> Result:
        """ Check the email config has been updated with non-default values """
        if self.email_config != EmailConfig.default_email_config:
            return Result(True, "Emails will be sent from: {}".format(self.sender()))
        else:
            return Result(False, "ERROR: Email has not been configured.\n"
                                 "       Please update {} with the correct details".format(paths.EMAIL_CONFIG))

    def _check_connection(self) -> Result:
        """ Check that using the details in the email config and email can be sent via the SMTP server """
        smtp_server = self.smtp_server()
        port = self.port()
        email = self.sender()
        password = self.password()

        try:
            smtp = SMTP(smtp_server, port, timeout=10)
            smtp.starttls()
            smtp.login(email, password)
        except socket.timeout:
            return Result(False, "\tERROR: Timeout while trying to connect {}:{}".format(smtp_server, port))
        except (SMTPHeloError, SMTPConnectError):
            return Result(False, "\tERROR: Cannot connect to {}:{}".format(smtp_server, port))
        except SMTPAuthenticationError:
            return Result(False, "\tERROR: Login attempt for {} failed".format(email))

        return Result(True, "\tSuccessful connection and authentication with SMTP server")
