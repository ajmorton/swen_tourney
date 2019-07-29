from smtplib import SMTP
from smtplib import SMTPHeloError, SMTPAuthenticationError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import socket

from util import format as fmt
from tournament.state.tourney_snapshot import TourneySnapshot
from util.types import FilePath
from config.configuration import EmailConfig, AssignmentConfig


def open_smtp_connection() -> SMTP:

    email_cfg = EmailConfig()

    smtp = SMTP(email_cfg.smtp_server(), email_cfg.port(), timeout=10)
    smtp.starttls()
    smtp.login(email_cfg.sender(), email_cfg.password())

    return smtp


def send_email(smtp: SMTP, sender_email: str, receiver_email: str, subject: str, message: str):

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message))

    smtp.sendmail(sender_email, receiver_email, msg.as_string())


def generate_mail_body(submitter: str, submitter_report, report_date: str, num_submitters: int,
                       best_average_bugs_detected: float, best_average_tests_evaded: float,) -> str:

    assg = AssignmentConfig().get_assignment()

    other_programs = len(assg.get_programs_list()) * (num_submitters - 1)
    other_tests = len(assg.get_test_list()) * (num_submitters - 1)

    body = ""
    body += "Hi {}\n".format(submitter)
    body += "Here are the results of the swen tournament as of {}:\n".format(report_date)
    body += "Your submission was run against {} others. Your results are:\n".format(num_submitters - 1)
    body += "\n"
    body += "Tests\n"
    for test in sorted(submitter_report['tests'].keys()):
        body += "  - {}: test detected {} of {} bugs\n".format(test, submitter_report['tests'][test], other_programs)
    body += "Detecting an average of {} bugs per test\n".format(submitter_report['average_bugs_detected'])
    body += "\n"
    body += "Mutants\n"
    for prog in sorted(submitter_report['progs'].keys()):
        body += "  - {}: mutant evaded detection in {} of {} tests\n".format(
            prog, submitter_report['progs'][prog], other_tests
        )
    body += "Evading an average of {} tests per mutant\n".format(submitter_report['average_tests_evaded'])
    body += "\n"
    body += "The most successful tester detected an average {} of {} bugs.\n".format(
        best_average_bugs_detected, other_programs
    )
    body += "The most successful mutants evaded an average {} of {} tests.\n".format(
        best_average_tests_evaded, other_tests
    )
    body += "\n"
    body += "This gives you a score of {}/5 for your tests, and {}/5 for your mutants\n".format(
        submitter_report['normalised_test_score'], submitter_report['normalised_prog_score']
    )

    return body


def send_results_to_submitters(smtp_connection: SMTP, sender_email: str, snapshot_file_path: FilePath):

    snapshot = TourneySnapshot(snapshot_file=snapshot_file_path)
    snapshot_date = snapshot.date().strftime(fmt.datetime_readable_string)
    num_submitters = snapshot.num_submitters()

    if num_submitters < 2:
        # no submissions have been run against each other. No email to send
        return

    results = snapshot.results()

    # gmail rate limits emails. After sending 50 wait for 5 minutes to avoid this
    send_count = 0

    for submitter in sorted(results.keys()):
        submitter_results = results[submitter]
        if submitter_results['latest_submission_date'] == TourneySnapshot.NO_DATE:
            # don't send an email to a submitter who has not made a submission
            continue

        if send_count >= 50:
            time.sleep(300)
            send_count = 0

        email_body = generate_mail_body(submitter, submitter_results, snapshot_date, num_submitters,
                                        snapshot.best_average_bugs_detected(), snapshot.best_average_tests_evaded())

        submitter_email = submitter_results['email']
        print("\tSending email to {} ({})".format(submitter, submitter_email))
        send_email(smtp_connection, sender_email, submitter_email, "SWEN Tournament results", email_body)
        send_count += 1


def send_confirmation_email(smtp_connection: SMTP, sender_email: str, receiver_email: str,
                            snapshot_file_path: FilePath):

    snapshot = TourneySnapshot(snapshot_file=snapshot_file_path)
    hostname = socket.gethostname()

    body = ""
    body += "Hi,\n"
    body += "A report for the state of the swen-tournament as of {} has been sent to" \
            " the {} students who have made a valid submission.\n".format(snapshot.date(), snapshot.num_submitters())
    body += "The details of this snapshot can be found on the tournament server {}:{}.".format(
        hostname, snapshot_file_path
    )

    print("\tSending confirmation email to {}".format(receiver_email))
    send_email(smtp_connection, sender_email, receiver_email, "SWEN Tournament results", body)
    pass


def email_results(results_file_path: FilePath, reporter_email: str):

    email_cfg = EmailConfig()
    sender_email = email_cfg.sender()

    print("Sending results from {}".format(sender_email))
    try:
        smtp_connection = open_smtp_connection()
        send_results_to_submitters(smtp_connection, sender_email, results_file_path)
        send_confirmation_email(smtp_connection, sender_email, reporter_email, results_file_path)
        smtp_connection.close()
    except socket.timeout:
        print("Error: Timeout while trying to connect to SMTP server")
    except OSError as os_error:
        print("Error raised while sending emails: {}".format(os_error))
        print("Email sending has been aborted.")
    except SMTPHeloError:
        print("No reply from SMTP server")
    except SMTPAuthenticationError:
        print("Login attempt failed")
