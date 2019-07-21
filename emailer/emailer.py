import smtplib
from smtplib import SMTP_SSL as SMTP  # SSL connection
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tournament.config.paths as paths
import json
import time

from tournament.util.types.basetypes import FilePath
import tournament.config.config as config


def send_email(receiver: str, receiver_email: str, subject: str, message: str):

    email_config = json.load(open(paths.EMAIL_CONFIG, 'r'))
    sender = email_config['email']
    password = email_config['password']
    smtp_server = email_config['smtp_server']
    port = email_config['port']

    try:
        smtp_server = SMTP(smtp_server, port)
        smtp_server.login(sender, password)

        print("Sending email to {} ({})".format(receiver, receiver_email))

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message))

        try:
            smtp_server.sendmail(sender, receiver_email, msg.as_string())
        except smtplib.SMTPException as e:
            print("Error: unable to send email {}".format(e))
        smtp_server.close()

    except smtplib.SMTPHeloError:
        print("Server did not reply")
    except smtplib.SMTPAuthenticationError:
        print("Login attempt returned SMTPAuthenticationError")
    except smtplib.SMTPException:
        print("Authentication failed")


def send_report_ready_email(receiver_email: str, report_time: str, report_file_path: FilePath, hostname: str):
    subject = "swen-tournament report ready"

    body = ""
    body += "Hi,\n"
    body += "\n"
    body += "A report has been generated for the status of swen-tournament as of {}.\n".format(report_time)
    body += "It can be found at {} on the {} VPS.".format(report_file_path, hostname)

    send_email("", receiver_email, subject, body)


def generate_mail_body(submitter: str, submitter_report, report_date: str, num_submitters: int,
                       best_average_bugs_detected: float, best_average_tests_evaded: float,) -> str:

    other_programs = len(config.assignment.get_programs_list()) * (num_submitters - 1)
    other_tests = len(config.assignment.get_test_list()) * (num_submitters - 1)

    body = ""
    body += "Hi {}\n".format(submitter)
    body += "Here are the results of the swen tournament as of {}:\n".format(report_date)
    body += "Your submission was run against {} others. Your results are:\n".format(num_submitters - 1)
    body += "\n"
    body += "Tests\n"
    for test in submitter_report['tests'].keys():
        body += "  - {}: test detected {} of {} bugs\n".format(test, submitter_report['tests'][test], other_programs)
    body += "Detecting an average of {} bugs per test\n".format(submitter_report['average_bugs_detected'])
    body += "\n"
    body += "Mutants\n"
    for prog in submitter_report['progs'].keys():
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


def send_tournament_report_to_submitters(report_file_path: FilePath):

    report = json.load(open(report_file_path, 'r'))

    report_date = report['report_date']
    num_submitters = int(report['num_submitters'])

    results = report['results']

    # gmail rate limits emails. After sending 50 wait for 5 minutes to avoid this
    send_count = 0

    for submitter in results.keys():
        if send_count >= 50:
            time.sleep(300)
            send_count = 0
        submitter_report = results[submitter]
        email_body = generate_mail_body(submitter, submitter_report, report_date, num_submitters,
                                        report['best_average_bugs_detected'], report['best_average_tests_evaded'])

        send_email(submitter, submitter_report['email'], "SWEN Tournament results", email_body)
        send_count += 1


def send_confirmation_email(receiver_email: str, report_time: str, report_file_name: FilePath, hostname: str):

    body = ""
    body += "Hi,\n"
    body += "A report for the state of the swen-tournament as of {} has been sent to students.\n".format(report_time)
    body += "The results of this tournament can be found on the tournament server at {} on {}.".format(
        report_file_name, hostname
    )

    send_email("", receiver_email, "SWEN Tournament results", body)
    pass

