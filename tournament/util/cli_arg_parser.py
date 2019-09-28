"""
Provides a command line interface for the backend and frontend commands for the tournament.
"""

from argparse import ArgumentParser, HelpFormatter
from datetime import datetime

import tournament.config.configuration as cfg
from tournament import submission as sub
from tournament.daemon import main as daemon
from tournament.main import main as tourney
from tournament.util.types import Submitter


def create_backend_parser():
    """ Create a command parser for the backend commands """
    parser = ArgumentParser(formatter_class=HelpFormatter)
    subparsers = parser.add_subparsers(title='commands')

    subparsers.add_parser('check_config').set_defaults(
        func=lambda args: cfg.configuration_valid(), help='Check the configuration of the tournament.')
    subparsers.add_parser('clean').set_defaults(
        func=lambda args: daemon.clean(), help='Remove all submissions and reset the tournament state.')
    subparsers.add_parser('start_tournament').set_defaults(
        func=lambda args: daemon.start_tournament(), help='Start the tournament server.')
    subparsers.add_parser('report').set_defaults(
        func=lambda args: daemon.make_report_request(datetime.now()), help='Get the results of the tournament.')
    subparsers.add_parser('shutdown').set_defaults(
        func=lambda args: daemon.shutdown(), help='Shut down the tournament server.')
    subparsers.add_parser('close_subs').set_defaults(
        func=lambda args: daemon.close_submissions(), help='Close new submissions to the tournament.')
    subparsers.add_parser('get_diffs').set_defaults(
        func=lambda args: tourney.get_diffs(), help='Generate diffs of submitters mutants to verify mutants are valid.')
    subparsers.add_parser('rescore_invalid_progs').set_defaults(
        func=lambda args: tourney.rescore_invalid_progs(), help='Read the diffs file and rescore any invalid progs.')

    return parser


def create_frontend_parser():
    """ Create a command parser for the frontend commands """

    parser = ArgumentParser(formatter_class=HelpFormatter)
    subparsers = parser.add_subparsers(title='commands')

    submitter_parser = ArgumentParser(add_help=False)
    submitter_parser.add_argument('submitter', type=Submitter, help='The submitter')

    elig_parser = subparsers.add_parser('check_eligibility', parents=[submitter_parser])
    elig_parser.add_argument('assg_name', type=str, help="The name of the assignment being submitted")
    elig_parser.set_defaults(func=lambda args: sub.check_submitter_eligibility(args.submitter, args.assg_name),
                             help='Check the submitter is eligible to submit to the tournament.')

    compile_parser = subparsers.add_parser('compile', parents=[submitter_parser])
    compile_parser.add_argument('submitter_dir', type=str, help="The location of the submitter")
    compile_parser.set_defaults(func=lambda args: sub.compile_submission(args.submitter, args.submitter_dir),
                                help='Prepare and compile a submission for validation.')

    val_tests_parser = subparsers.add_parser('validate_tests', parents=[submitter_parser])
    val_tests_parser.set_defaults(func=lambda args: sub.validate_tests(args.submitter),
                                  help='Validate the tests in a provided submission.')

    val_progs_parser = subparsers.add_parser('validate_progs', parents=[submitter_parser])
    val_progs_parser.set_defaults(func=lambda args: sub.validate_programs_under_test(args.submitter),
                                  help='Validate the programs under test in a provided submission.')

    submit_parser = subparsers.add_parser('submit', parents=[submitter_parser])
    submit_parser.set_defaults(func=lambda args: sub.make_submission(args.submitter), help='Make a submission.')

    return parser


def parse_args(backend: bool = False):
    """ Parse a commands sent to the tournament """
    parser = create_frontend_parser() if not backend else create_backend_parser()

    try:
        return parser.parse_args()

    except SystemExit:
        exit(1)
