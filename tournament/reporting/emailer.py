"""
When the tournament hits a critical error that requires a shutdown tournament maintainers should be notified.
This code handles the notification of maintainers via email.
"""
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTPHeloError, SMTPAuthenticationError, SMTPConnectError

from tournament.config import EmailConfig
from tournament.util import paths
from tournament.util import print_tourney_trace, print_tourney_error


def _send_email(smtp: SMTP, sender_email: str, receiver_emails: [str], subject: str, message: str):
    """ Send an email to recipients """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_emails
    msg['Subject'] = subject
    msg.attach(MIMEText(message))
    smtp.sendmail(sender_email, receiver_emails, msg.as_string())


def email_crash_report():
    """ Construct an email with the details of a tournament crash and send to the designated recipients """

    try:
        cfg = EmailConfig()

        # connect to smtp server
        smtp = SMTP(cfg.smtp_server(), cfg.port(), timeout=10)
        smtp.starttls()
        smtp.login(cfg.sender(), cfg.password())

        message = "Hi,\n\n"
        message += "The swen-tourney code has raised an exception and has been stopped.\n" \
                   "Please correct this error and restart the tournament. " \
                   "Details on this crash can be found at {} on {}.".format(paths.TRACE_FILE, socket.gethostname())

        print_tourney_trace("\tSending crash report email to {}".format(cfg.crash_report_recipients()))
        _send_email(smtp, cfg.sender(), cfg.crash_report_recipients(), "SWEN Tournament crash", message)
        smtp.close()

    except socket.timeout:
        print_tourney_error("Timeout while trying to connect to SMTP server")
    except (SMTPHeloError, SMTPConnectError):
        print_tourney_error("Cannot connect to SMTP server")
    except SMTPAuthenticationError:
        print_tourney_error("Login attempt failed")
    except OSError as os_error:
        print_tourney_error("Error raised while sending emails: {}".format(os_error))
        print_tourney_error("Email sending has been aborted.")
