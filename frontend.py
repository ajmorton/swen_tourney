"""
Frontend interface for the tournament. This is used to make submissions to the tournament.
"""
import os

import tournament.util.funcs
from tournament import util as parser
from tournament.util import FrontEndCommand
from tournament.util import Submitter
import tournament.submission


def main():
    """
    Parse and process frontend commands
    """
    command = parser.parse_frontend_args()
    submission_dir = command.dir
    assg_name = os.path.basename(submission_dir.rstrip('/'))
    submitter = Submitter(os.path.basename((os.path.dirname(submission_dir).rstrip('/'))))

    print()
    print("==================================")

    success, traces = False, "Error: unrecognised command: '{}'".format(command.type)
    if command.type == FrontEndCommand.CHECK_ELIGIBILITY:
        print("Checking submitter eligibility  ")
        success, traces = tournament.submission.check_submitter_eligibility(submitter, assg_name)

    elif command.type == FrontEndCommand.COMPILE:
        print("Preparing and compiling submission  ")
        success, traces = tournament.submission.compile_submission(submitter, submission_dir)

    elif command.type == FrontEndCommand.VALIDATE_TESTS:
        print("Validating submitted tests    ")
        success, traces = tournament.submission.validate_tests(submitter)

    elif command.type == FrontEndCommand.VALIDATE_PROGS:
        print("Validating submitted programs  ")
        success, traces = tournament.submission.validate_programs_under_test(submitter)

    elif command.type == FrontEndCommand.SUBMIT:
        print("Validating submitted programs  ")
        (success, traces) = tournament.submission.make_submission(submitter)

    print(traces)
    print("==================================")

    exit(0 if success else 1)


if __name__ == "__main__":
    tournament.util.funcs.assert_python_version(3, 5, 2)
    main()
