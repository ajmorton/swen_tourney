"""
Provides a command line interface for the backend and frontend commands for the tournament.
"""

from argparse import ArgumentParser, HelpFormatter, ArgumentError
from collections import OrderedDict
from datetime import datetime
import sys

import tournament.config as cfg
from tournament import main as tourney
from tournament.submission import run_stage, Stage
from tournament.util.types import Submitter


class ArgListFormatter(HelpFormatter):
    """ Prints all commands and their descriptions as a list when the help function is called """

    def _format_usage(self, usage, actions, groups, prefix):
        return sys.argv[0]

    @staticmethod
    def list_commands(choices: OrderedDict) -> str:
        """ Provided a list of choices in a subparser, return a formatted list with descriptions """
        right_align = max(map(len, choices))  # length of longest command name for text aligning
        return "".join(["\t{:<{}}\t{}\n".format(choice, right_align, choices[choice].description)
                        for choice in choices])

    def _metavar_formatter(self, action, default_metavar):
        if action.choices is not None:
            result = ArgListFormatter.list_commands(OrderedDict(action.choices))
        else:
            result = default_metavar

        # pylint suppressed -> We're overriding this function, can't rename it
        def format(tuple_size): # pylint: disable=redefined-builtin
            return result if isinstance(result, tuple) else (result,) * tuple_size

        return format


class ArgParser(ArgumentParser):
    """ Override the default _check_value to use ArgListFormatter when an invalid command is used """
    def _check_value(self, action, value):
        if action.choices is not None and value not in action.choices:
            msg = 'invalid choice: "{}". Choose from:\n{}'.format(
                value, ArgListFormatter.list_commands(OrderedDict(action.choices)))
            raise ArgumentError(action, msg)


def _create_backend_parser():
    """ Create a command parser for the backend commands """
    parser = ArgParser(formatter_class=ArgListFormatter)
    subparsers = parser.add_subparsers(title='commands')

    subparsers.add_parser('check_config', description='Check the configuration of the tournament.').set_defaults(
        func=lambda args: cfg.configuration_valid())

    subparsers.add_parser('clean', description='Remove all submissions and reset the tournament state.').set_defaults(
        func=lambda args: tourney.clean())

    subparsers.add_parser('start_tournament', description='Start the tournament.').set_defaults(
        func=lambda args: tourney.start_tournament())

    subparsers.add_parser('export_results', description='Export tournament results in csv format.').set_defaults(
        func=lambda args: tourney.create_results_csv())

    shutdown_parser = subparsers.add_parser('shutdown', description='Shut down the tournament.')
    shutdown_parser.add_argument('--message', default="", help='The message to display while tournament is shutdown')
    shutdown_parser.set_defaults(func=lambda args: tourney.shutdown(args.message))

    subparsers.add_parser('get_diffs', description='Generate diffs of submitters mutants to verify mutants are valid.')\
        .set_defaults(func=lambda args: tourney.get_diffs())

    subparsers.add_parser('rescore_invalid_progs', description='Read the diffs file and rescore any invalid progs.')\
        .set_defaults(func=lambda args: tourney.rescore_invalid_progs())

    return parser


def _create_frontend_parser():
    """ Create a command parser for the frontend commands """

    parser = ArgParser(formatter_class=ArgListFormatter)
    subparsers = parser.add_subparsers(title='commands')

    submitter_parser = ArgumentParser(add_help=False)
    submitter_parser.add_argument('submitter', type=Submitter, help='The submitter')

    elig_parser = subparsers.add_parser('check_eligibility', parents=[submitter_parser],
                                        description='Check the submitter is eligible to submit to the tournament.')
    elig_parser.add_argument('assg_name', type=str, help="The name of the assignment being submitted")
    elig_parser.add_argument('dir', type=str, help="The location of the submission")
    elig_parser.set_defaults(func=lambda args: run_stage(Stage.CHECK_ELIG, args.submitter, args.assg_name, args.dir))

    compile_parser = subparsers.add_parser('compile', parents=[submitter_parser],
                                           description='Compile tests and progs in a provided submission.')
    compile_parser.set_defaults(func=lambda args: run_stage(Stage.COMPILE, args.submitter),)

    val_tests_parser = subparsers.add_parser('validate_tests', parents=[submitter_parser],
                                             description='Validate the tests in a provided submission.')
    val_tests_parser.set_defaults(func=lambda args: run_stage(Stage.VALIDATE_TESTS, args.submitter))

    val_progs_parser = subparsers.add_parser('validate_progs', parents=[submitter_parser],
                                             description='Validate the programs under test in a provided submission.')
    val_progs_parser.set_defaults(func=lambda args: run_stage(Stage.VALIDATE_PROGS, args.submitter))

    submit_parser = subparsers.add_parser('submit', parents=[submitter_parser], description='Make a submission.')
    submit_parser.set_defaults(func=lambda args: run_stage(Stage.SUBMIT, args.submitter))

    return parser


def parse_args(backend: bool = False):
    """ Parse a commands sent to the tournament """
    parser = _create_frontend_parser() if not backend else _create_backend_parser()

    try:
        args = parser.parse_args()
        if not args.__contains__('func'):
            parser.print_help()
            exit(1)
        return args

    except SystemExit:
        exit(1)
