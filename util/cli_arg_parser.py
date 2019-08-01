import argparse
import sys
from enum import Enum


# Formats the help message, removes some annoying text
class SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts


class BackendCommands(str, Enum):
    START_SERVER = 'start_server'
    SHUTDOWN = 'shutdown'
    REPORT = 'report'
    CLEAN = 'clean'
    CHECK_CONFIG = 'check_config'


def create_backend_parser(parser_list):
    parser = argparse.ArgumentParser(formatter_class=SubcommandHelpFormatter)
    subparsers = parser.add_subparsers(title='commands')

    # add the parser for the start_server command
    command_name = BackendCommands.START_SERVER.value
    start_server_parser = subparsers.add_parser(
        command_name, help='Start the tournament server'
    )
    start_server_parser.set_defaults(type=command_name)
    parser_list[command_name] = start_server_parser

    # add the parser for the shutdown command
    command_name = BackendCommands.SHUTDOWN.value
    shutdown_parser = subparsers.add_parser(
        command_name, help='Shut down the tournament server'
    )
    shutdown_parser.set_defaults(type=command_name)
    parser_list[command_name] = shutdown_parser

    # add the parser for the send_report command
    command_name = BackendCommands.REPORT.value
    report_parser = subparsers.add_parser(
        command_name, help='Get the results of the tournament.'
    )
    report_parser.add_argument('email', help='Who to notify when the report is generated')
    report_parser.set_defaults(type=command_name)
    parser_list[command_name] = report_parser

    # add the parser for the clean command
    command_name = BackendCommands.CLEAN.value
    clean_parser = subparsers.add_parser(
        command_name, help='Remove all submissions from the tournament and reset the tournament state.'
    )
    clean_parser.set_defaults(type=command_name)
    parser_list[command_name] = clean_parser

    # add the parser for the set_up command
    command_name = BackendCommands.CHECK_CONFIG.value
    check_config_parser = subparsers.add_parser(
        command_name, help='Check the configuration of the tournament.'
    )
    check_config_parser.set_defaults(type=command_name)
    parser_list[command_name] = check_config_parser

    return parser


class FrontEndCommand(str, Enum):
    CHECK_ELIGIBILITY = 'check_eligibility'
    VALIDATE_TESTS = 'validate_tests'
    VALIDATE_PROGS = 'validate_progs'
    SUBMIT = 'submit'


def create_frontend_parser(parser_list):
    parser = argparse.ArgumentParser(formatter_class=SubcommandHelpFormatter)
    subparsers = parser.add_subparsers(title='commands')

    # common parser for parsing the submission directory's path
    directory_parser = argparse.ArgumentParser(add_help=False)
    directory_parser.add_argument('dir', help="The directory of the submission to test")

    # add the parser for the check_eligibility command
    command_name = FrontEndCommand.CHECK_ELIGIBILITY.value
    check_elig_parser = subparsers.add_parser(
        command_name, help='Check the submitter is eligible to submit to the tournament', parents=[directory_parser]
    )
    check_elig_parser.set_defaults(type=command_name)
    parser_list[command_name] = check_elig_parser

    # add the parser for the validate_tests command
    command_name = FrontEndCommand.VALIDATE_TESTS.value
    val_test_parser = subparsers.add_parser(
        command_name, help='Validate the tests in a provided submission', parents=[directory_parser]
    )
    val_test_parser.set_defaults(type=command_name)
    parser_list[command_name] = val_test_parser

    # add the parser for the process_submission command
    command_name = FrontEndCommand.VALIDATE_PROGS.value
    val_mut_parser = subparsers.add_parser(
        command_name, help='Validate the programs under test in a provided submission', parents=[directory_parser]
    )
    val_mut_parser.set_defaults(type=command_name)
    parser_list[command_name] = val_mut_parser

    # add the parser for the submit command
    command_name = FrontEndCommand.SUBMIT.value
    submit_parser = subparsers.add_parser(
        command_name, help='Make a submission', parents=[directory_parser]
    )
    submit_parser.set_defaults(type=command_name)
    parser_list[command_name] = submit_parser

    return parser


def print_help_text(parser_list, root_parser):
    print()

    # When argparse fails it throws only a SystemExit. To figure out which command failed look at sys.argv[1]
    command_name = sys.argv[1]

    if command_name in parser_list:
        parser_list[sys.argv[1]].print_help()
    else:
        root_parser.print_help()


def parse_frontend_args():
    sub_parser_list = dict()
    parser = create_frontend_parser(sub_parser_list)

    try:
        return parser.parse_args()

    except SystemExit:
        exit(1)


def parse_backend_args():
    sub_parser_list = dict()
    parser = create_backend_parser(sub_parser_list)

    try:
        return parser.parse_args()

    except SystemExit:
        exit(1)