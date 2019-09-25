"""
Provides a command line interface for the backend and frontend commands for the tournament.
"""

from argparse import ArgumentParser, HelpFormatter
from enum import Enum


class BackendCommands(str, Enum):
    """ List of commands available for the tournament backend """
    START_TOURNAMENT = 'start_tournament'
    SHUTDOWN = 'shutdown'
    REPORT = 'report'
    CLEAN = 'clean'
    CHECK_CONFIG = 'check_config'
    CLOSE_SUBS = 'close_submissions'
    GET_DIFFS = 'get_diffs'
    RESCORE_INVALID = 'rescore_invalid_progs'


def add_parser(parser_list: dict, subparsers, command, help_text: str, parents: [ArgumentParser] = None):
    # add the parser for the start_server command
    command_name = command.value
    new_parser = subparsers.add_parser(command_name, help=help_text, parents=parents if parents else [])
    new_parser.set_defaults(type=command_name)
    parser_list[command_name] = new_parser


def create_backend_parser(parser_list):
    """ Create a command parser for the backend commands """
    parser = ArgumentParser(formatter_class=HelpFormatter)
    subparsers = parser.add_subparsers(title='commands')

    commands = \
        [(BackendCommands.START_TOURNAMENT, 'Start the tournament server'),
         (BackendCommands.SHUTDOWN, 'Shut down the tournament server'),
         (BackendCommands.REPORT, 'Get the results of the tournament.'),
         (BackendCommands.CLEAN, 'Remove all submissions from the tournament and reset the tournament state.'),
         (BackendCommands.CHECK_CONFIG, 'Check the configuration of the tournament.'),
         (BackendCommands.CLOSE_SUBS, 'Close new submissions to the tournament.'),
         (BackendCommands.GET_DIFFS, 'Generate diffs of submitters mutants to verify mutants are valid.'),
         (BackendCommands.RESCORE_INVALID, 'Read the diffs file and update (zero out) the score of any invalid progs')]

    for command, help_text in commands:
        add_parser(parser_list, subparsers, command, help_text)

    return parser


class FrontEndCommand(str, Enum):
    """ List of command available for the tournament frontend """
    CHECK_ELIGIBILITY = 'check_eligibility'
    COMPILE = 'compile'
    VALIDATE_TESTS = 'validate_tests'
    VALIDATE_PROGS = 'validate_progs'
    SUBMIT = 'submit'


def create_frontend_parser(parser_list):
    """ Create a command parser for the frontend commands """
    parser = ArgumentParser(formatter_class=HelpFormatter)
    subparsers = parser.add_subparsers(title='commands')

    # common parser for parsing the submission directory's path
    directory_parser = ArgumentParser(add_help=False)
    directory_parser.add_argument('dir', help="The directory of the submission to test")

    commands = \
        [(FrontEndCommand.CHECK_ELIGIBILITY, 'Check the submitter is eligible to submit to the tournament'),
         (FrontEndCommand.COMPILE, 'Prepare and compile a submission for validation'),
         (FrontEndCommand.VALIDATE_TESTS, 'Validate the tests in a provided submission'),
         (FrontEndCommand.VALIDATE_PROGS, 'Validate the programs under test in a provided submission'),
         (FrontEndCommand.SUBMIT, 'Make a submission')]

    for command, help_text in commands:
        add_parser(parser_list, subparsers, command, help_text, parents=[directory_parser])

    return parser


def parse_args(backend: bool = False):
    """ Parse a commands sent to the tournament """
    sub_parser_list = dict()
    parser = create_frontend_parser(sub_parser_list) if not backend else create_backend_parser(sub_parser_list)

    try:
        return parser.parse_args()

    except SystemExit:
        exit(1)
