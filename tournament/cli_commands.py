"""
Provides a command line interface for the backend and frontend commands for the tournament.
"""

from argparse import ArgumentParser, HelpFormatter
from datetime import datetime

import tournament.config as cfg
from tournament import main as tourney
from tournament.submission import run_stage, Stage
from tournament.util.types import Submitter


def _create_backend_parser():
    """ Create a command parser for the backend commands """
    parser = ArgumentParser(formatter_class=HelpFormatter)
    subparsers = parser.add_subparsers(title='commands')

    subparsers.add_parser('check_config').set_defaults(
        func=lambda args: cfg.configuration_valid(), help='Check the configuration of the tournament.')

    subparsers.add_parser('clean').set_defaults(
        func=lambda args: tourney.clean(), help='Remove all submissions and reset the tournament state.')

    subparsers.add_parser('start_tournament').set_defaults(
        func=lambda args: tourney.start_tournament(), help='Start the tournament.')

    subparsers.add_parser('report').set_defaults(
        func=lambda args: tourney.make_report_request(datetime.now()), help='Get the results of the tournament.')

    shutdown_parser = subparsers.add_parser('shutdown')
    shutdown_parser.add_argument('--message', default="", help='The message to display when tournament is shutdown')
    shutdown_parser.set_defaults(func=lambda args: tourney.shutdown(args.message), help='Shut down the tournament.')

    subparsers.add_parser('get_diffs').set_defaults(
        func=lambda args: tourney.get_diffs(), help='Generate diffs of submitters mutants to verify mutants are valid.')

    subparsers.add_parser('rescore_invalid_progs').set_defaults(
        func=lambda args: tourney.rescore_invalid_progs(), help='Read the diffs file and rescore any invalid progs.')

    return parser


def _create_frontend_parser():
    """ Create a command parser for the frontend commands """

    parser = ArgumentParser(formatter_class=HelpFormatter)
    subparsers = parser.add_subparsers(title='commands')

    submitter_parser = ArgumentParser(add_help=False)
    submitter_parser.add_argument('submitter', type=Submitter, help='The submitter')

    elig_parser = subparsers.add_parser('check_eligibility', parents=[submitter_parser])
    elig_parser.add_argument('assg_name', type=str, help="The name of the assignment being submitted")
    elig_parser.add_argument('dir', type=str, help="The location of the submission")
    elig_parser.set_defaults(func=lambda args: run_stage(Stage.CHECK_ELIG, args.submitter, args.assg_name, args.dir),
                             help='Check the submitter is eligible to submit to the tournament.')

    compile_parser = subparsers.add_parser('compile', parents=[submitter_parser])
    compile_parser.set_defaults(func=lambda args: run_stage(Stage.COMPILE, args.submitter),
                                help='Compile tests and progs in a provided submission.')

    val_tests_parser = subparsers.add_parser('validate_tests', parents=[submitter_parser])
    val_tests_parser.set_defaults(func=lambda args: run_stage(Stage.VALIDATE_TESTS, args.submitter),
                                  help='Validate the tests in a provided submission.')

    val_progs_parser = subparsers.add_parser('validate_progs', parents=[submitter_parser])
    val_progs_parser.set_defaults(func=lambda args: run_stage(Stage.VALIDATE_PROGS, args.submitter),
                                  help='Validate the programs under test in a provided submission.')

    submit_parser = subparsers.add_parser('submit', parents=[submitter_parser])
    submit_parser.set_defaults(func=lambda args: run_stage(Stage.SUBMIT, args.submitter), help='Make a submission.')

    return parser


def parse_args(backend: bool = False):
    """ Parse a commands sent to the tournament """
    parser = _create_frontend_parser() if not backend else _create_backend_parser()

    try:
        return parser.parse_args()

    except SystemExit:
        exit(1)
